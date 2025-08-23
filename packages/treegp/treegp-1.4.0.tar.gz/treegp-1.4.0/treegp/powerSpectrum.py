import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter
from scipy.interpolate import RegularGridInterpolator
from typing import Optional, Tuple


class EmpiricalPSDKernel2D:
    """
    Empirical 2D stationary GP kernel built from measured data using
    Bochner's theorem (non-negative power spectral density ⇔ positive semidefinite
    covariance).

    Pipeline
    --------
    Given irregular samples (x_i, y_i) with residuals z_i:
      1) Estimate the empirical covariance C_emp(hx, hy) on a uniform lag grid by
         binning pairwise products z_i z_j at vector lags h = (x_j - x_i, y_j - y_i)
         within a maximum range r_max.
      2) Denoise with a Gaussian filter (applied to numerator & counts separately).
         Force even symmetry C(h) = C(-h).
      3) Project to the PSD cone via Fourier domain: S = FFT(C), S <- max(S, 0),
         then C <- IFFT(S). (Bochner's theorem ⇒ PSD everywhere.)
      4) Build an interpolator K(hx, hy) over the lag grid for fast evaluation.

    Notes
    -----
    * The kernel is *stationary* and can represent general anisotropy (not assumed
      isotropic or axis-aligned). No parametric form (e.g., Von Karman) is assumed.
    * The construction guarantees a positive semidefinite covariance (up to small
      numerical error) because the power spectrum is constrained to be non-negative.
    * For large N, pairwise binning can be expensive. Use r_max to truncate
      interactions and/or set subsample_pairs < 1 for speed.

    Parameters
    ----------
    grid_size : int
        Number of bins per axis for the lag grid (uniform). Higher ⇒ finer kernel.
    r_max : Optional[float]
        Maximum lag magnitude to consider (in same units as x,y). If None, it is
        set to half the larger side of the spatial bounding box.
    smooth_sigma : float
        Gaussian smoothing (in bins) applied to the binned numerator and counts
        before division. Use ~1-2 for light smoothing, larger for noisy data.
    pad_factor : int
        Zero-padding factor for the FFT projection (>=1). 2 or 3 reduces wrap-around
        artifacts when projecting in the spectral domain.
    min_psd : float
        Floor for the power spectrum during projection. Use 0 to hard-clip negatives;
        a small positive value can help numerical stability.
    nugget : float
        Optional white-noise variance added on the diagonal when evaluating K(X, X).
    subsample_pairs : float in (0,1]
        Randomly keep this fraction of pairs for binning (speed/variance trade-off).
    random_state : Optional[int]
        RNG seed for reproducible subsampling.
    """

    def __init__(
        self,
        grid_size: int = 128,
        r_max: Optional[float] = None,
        smooth_sigma: float = 1.5,
        pad_factor: int = 2,
        min_psd: float = 0.0,
        nugget: float = 0.0,
        subsample_pairs: float = 1.0,
        random_state: Optional[int] = None,
    ):
        if grid_size < 8:
            raise ValueError("grid_size must be >= 8")
        if pad_factor < 1:
            raise ValueError("pad_factor must be >= 1")
        self.grid_size = int(grid_size)
        self.r_max_user = r_max
        self.smooth_sigma = float(smooth_sigma)
        self.pad_factor = int(pad_factor)
        self.min_psd = float(min_psd)
        self.nugget = float(nugget)
        self.subsample_pairs = float(subsample_pairs)
        self.random_state = random_state

        # Fitted attributes
        self.hx: Optional[np.ndarray] = None
        self.hy: Optional[np.ndarray] = None
        self.C_grid: Optional[np.ndarray] = None
        self.var_: Optional[float] = None
        self._interp: Optional[RegularGridInterpolator] = None

    def fit(
        self, x: np.ndarray, y: np.ndarray, z: np.ndarray
    ) -> "EmpiricalPSDKernel2D":
        """Fit the empirical PSD‑projected kernel from samples.

        Parameters
        ----------
        x, y : arrays of shape (N,)
            Sample coordinates.
        z : array of shape (N,)
            Measured residuals/field values. The mean will be removed.
        """
        x = np.asarray(x).ravel()
        y = np.asarray(y).ravel()
        z = np.asarray(z).ravel()
        if not (x.size == y.size == z.size):
            raise ValueError("x, y, z must have the same length")
        n = x.size
        if n < 3:
            raise ValueError("Need at least 3 samples")

        # Demean
        z = z - np.mean(z)
        self.var_ = float(np.mean(z**2))

        # Choose lag extent
        if self.r_max_user is None:
            Lx = float(np.max(x) - np.min(x))
            Ly = float(np.max(y) - np.min(y))
            r_max = 0.5 * max(Lx, Ly)
        else:
            r_max = float(self.r_max_user)
        if r_max <= 0:
            raise ValueError("r_max must be positive or inferable from data")

        # Uniform lag grid (centers)
        g = int(self.grid_size)
        hx = np.linspace(-r_max, r_max, g)
        hy = np.linspace(-r_max, r_max, g)
        hx_edges = np.linspace(-r_max, r_max, g + 1)
        hy_edges = np.linspace(-r_max, r_max, g + 1)

        # Bin pairwise products z_i z_j at lags within r_max using a KDTree
        numer = np.zeros((g, g), dtype=np.float64)
        denom = np.zeros((g, g), dtype=np.float64)  # counts

        tree = cKDTree(np.c_[x, y])
        rng = np.random.default_rng(self.random_state)

        # Process in blocks to keep memory bounded
        # Include self-pairs via query_ball_point (will include i itself)
        for i in range(n):
            idx = tree.query_ball_point([x[i], y[i]], r=r_max)
            # Upper-triangular to avoid double counting
            idx = [j for j in idx if j >= i]
            if len(idx) == 0:
                continue
            dx = x[idx] - x[i]
            dy = y[idx] - y[i]
            w = z[idx] * z[i]

            if self.subsample_pairs < 1.0:
                m = len(idx)
                keep = rng.random(m) < self.subsample_pairs
                if np.any(keep):
                    dx, dy, w = dx[keep], dy[keep], w[keep]
                else:
                    continue

            # Weighted sums over lag bins
            Hn, _, _ = np.histogram2d(dx, dy, bins=[hx_edges, hy_edges], weights=w)
            Hc, _, _ = np.histogram2d(dx, dy, bins=[hx_edges, hy_edges])
            numer += Hn
            denom += Hc

        # Denoise: smooth numerator and counts, then divide
        if self.smooth_sigma > 0:
            numer_s = gaussian_filter(numer, sigma=self.smooth_sigma, mode="nearest")
            denom_s = gaussian_filter(denom, sigma=self.smooth_sigma, mode="nearest")
        else:
            numer_s, denom_s = numer, denom

        with np.errstate(invalid="ignore", divide="ignore"):
            C_emp = np.divide(
                numer_s, denom_s, out=np.zeros_like(numer_s), where=denom_s > 0
            )

        # Ensure even symmetry: C(h) = C(-h)
        C_even = 0.5 * (C_emp + np.flipud(np.fliplr(C_emp)))

        # Set the zero-lag to sample variance (robustly)
        center = (g // 2, g // 2)
        C_even[center] = self.var_

        # Project to non-negative PSD via FFT with optional zero-padding
        C_psd = self._project_to_psd(
            C_even, pad_factor=self.pad_factor, min_psd=self.min_psd
        )

        # Store and build interpolator
        self.hx, self.hy, self.C_grid = hx, hy, C_psd
        self._interp = RegularGridInterpolator(
            (hx, hy), C_psd, bounds_error=False, fill_value=0.0, method="linear"
        )
        return self

    @staticmethod
    def _project_to_psd(
        C: np.ndarray, pad_factor: int = 2, min_psd: float = 0.0
    ) -> np.ndarray:
        """Project a real-even covariance grid C(hx,hy) to the PSD cone.

        Steps: FFT (with shift so h=0 is centered) → clip negatives → IFFT → crop.
        Zero-padding reduces circular wrap-around artifacts.
        """
        C = np.asarray(C, dtype=np.float64)
        g0x, g0y = C.shape
        if pad_factor > 1:
            px = (pad_factor - 1) * g0x
            py = (pad_factor - 1) * g0y
            pad = ((px // 2, px - px // 2), (py // 2, py - py // 2))
            Cpad = np.pad(C, pad, mode="constant", constant_values=0.0)
        else:
            Cpad = C

        # Centered FFT (h=0 at center)
        S = np.fft.fftshift(np.fft.fftn(np.fft.ifftshift(Cpad))).real
        # Enforce non-negativity in the spectrum (Bochner)
        if min_psd <= 0:
            S_pos = np.maximum(S, 0.0)
        else:
            S_pos = np.maximum(S, float(min_psd))

        # Back to covariance, keep real part
        Cproj = np.fft.fftshift(np.fft.ifftn(np.fft.ifftshift(S_pos))).real

        # Crop back to original size if padded
        if pad_factor > 1:
            sx, sy = Cproj.shape
            x0 = (sx - g0x) // 2
            y0 = (sy - g0y) // 2
            Cproj = Cproj[x0 : x0 + g0x, y0 : y0 + g0y]

        # Force symmetry again to counter tiny numerical drift
        Cproj = 0.5 * (Cproj + np.flipud(np.fliplr(Cproj)))
        return Cproj

    def kernel_at_lag(self, hx: np.ndarray, hy: np.ndarray) -> np.ndarray:
        """Evaluate K(hx, hy) on arrays of the same shape (broadcast supported)."""
        if self._interp is None:
            raise RuntimeError("Call fit() first")
        pts = np.stack([np.ravel(hx), np.ravel(hy)], axis=-1)
        vals = self._interp(pts)
        return vals.reshape(np.broadcast(hx, hy).shape)

    def __call__(
        self,
        X1: np.ndarray,
        X2: Optional[np.ndarray] = None,
        add_nugget: bool = False,
        block: int = 4096,
    ) -> np.ndarray:
        """Return the covariance matrix K(X1, X2) using the learned kernel.

        Parameters
        ----------
        X1 : array (n1, 2)
        X2 : array (n2, 2) or None (defaults to X1)
        add_nugget : add self.nugget to the diagonal if X2 is None
        block : block size to control memory during interpolation
        """
        if self._interp is None:
            raise RuntimeError("Call fit() first")
        X1 = np.asarray(X1, dtype=float)
        if X1.ndim != 2 or X1.shape[1] != 2:
            raise ValueError("X1 must have shape (n, 2)")
        if X2 is None:
            X2 = X1
        else:
            X2 = np.asarray(X2, dtype=float)
            if X2.ndim != 2 or X2.shape[1] != 2:
                raise ValueError("X2 must have shape (m, 2)")

        n1, n2 = X1.shape[0], X2.shape[0]
        K = np.empty((n1, n2), dtype=float)

        # Blocked evaluation to keep memory bounded
        for i0 in range(0, n1, block):
            i1 = min(i0 + block, n1)
            Xi = X1[i0:i1]
            # Compute all pairwise lags to X2: shape (bi, n2, 2)
            dx = Xi[:, None, 0] - X2[None, :, 0]
            dy = Xi[:, None, 1] - X2[None, :, 1]
            val = self.kernel_at_lag(dx, dy)
            K[i0:i1, :] = val

        if add_nugget and X2 is X1 and self.nugget > 0:
            K[np.diag_indices_from(K)] += self.nugget
        return K


# -----------------------------
# Minimal usage example
# -----------------------------
if __name__ == "__main__":
    # Synthetic demo: anisotropic correlated field sampled irregularly
    rng = np.random.default_rng(0)
    n = 2000
    x = 200 * rng.random(n)
    y = 100 * rng.random(n)

    # Create a ground truth anisotropic kernel for testing
    def true_kernel(dx, dy):
        # rotated anisotropic Gaussian
        th = np.deg2rad(30.0)
        c, s = np.cos(th), np.sin(th)
        xr = c * dx + s * dy
        yr = -s * dx + c * dy
        ax, ay = 30.0, 10.0
        return np.exp(-0.5 * ((xr / ax) ** 2 + (yr / ay) ** 2))

    # Sample a GP with the true kernel on these irregular points
    # Build covariance with a nugget
    X = np.c_[x, y]
    Dx = X[:, None, 0] - X[None, :, 0]
    Dy = X[:, None, 1] - X[None, :, 1]
    K_true = true_kernel(Dx, Dy) + 0.05 * np.eye(n)
    # Draw one realization
    L = np.linalg.cholesky(K_true + 1e-6 * np.eye(n))
    z = L @ rng.standard_normal(n)

    # Fit empirical kernel
    ker = EmpiricalPSDKernel2D(
        grid_size=128,
        r_max=None,
        smooth_sigma=1.5,
        pad_factor=2,
        min_psd=0.0,
        nugget=0.05,
        subsample_pairs=0.5,
        random_state=42,
    )
    ker.fit(x, y, z)

    # Build GP covariance on a small test set
    Xt = np.stack(
        np.meshgrid(np.linspace(0, 200, 15), np.linspace(0, 100, 10)), axis=-1
    ).reshape(-1, 2)
    K_emp = ker(Xt, Xt, add_nugget=True)
    print("Empirical kernel matrix shape:", K_emp.shape)
