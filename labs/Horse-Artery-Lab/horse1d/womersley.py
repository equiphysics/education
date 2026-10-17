"""Witzig-Womersley wall shear stress for pulsatile flow in a rigid tube.

For the n-th harmonic Q_n of the flow, the wall shear stress is (paper, Eq 6)

    tau_n = mu / (pi R^3) * Q_n * F(Lambda_n),
    F(L) = L * J1(L)/J0(L) / (1 - 2 J1(L) / (L J0(L))),
    Lambda_n = alpha_n * i^(3/2),   alpha_n = R * sqrt(n * omega * rho / mu).

For slow flow (alpha -> 0) F -> -4, which is Poiseuille: tau = -4 mu Q / (pi R^3).
For fast flow (large alpha) |F| grows like alpha: a thin boundary layer at the wall.
"""
import numpy as np
from scipy.special import jve


def womersley_number(R, freq_hz, rho, mu):
    return R * np.sqrt(2.0 * np.pi * freq_hz * rho / mu)


def shear_factor(alpha):
    """F(Lambda) for real Womersley number(s) alpha >= 0 (array ok)."""
    alpha = np.asarray(alpha, dtype=float)
    out = np.full(alpha.shape, -4.0 + 0j)
    big = alpha > 1e-3
    L = alpha[big] * np.exp(1j * 3 * np.pi / 4)
    # jve is exponentially scaled, so the ratio stays finite for large alpha
    r = jve(1, L) / jve(0, L)
    out[big] = L * r / (1.0 - 2.0 * r / L)
    return out


def wall_shear_from_flow(Q_samples, R, T, rho, mu, n_harmonics):
    """Wall shear stress tau(t) (Pa) from one period of flow samples (m^3/s).

    Q_samples: array (..., M) of equally spaced samples over one period.
    R: radius (m), broadcastable to Q_samples[..., 0].
    """
    M = Q_samples.shape[-1]
    Qh = np.fft.rfft(Q_samples, axis=-1) / M
    n = np.arange(Qh.shape[-1])
    alpha = womersley_number(np.asarray(R)[..., None], n / T, rho, mu)
    F = shear_factor(alpha)
    F[..., 0] = -4.0
    Th = (mu / (np.pi * np.asarray(R)[..., None] ** 3)) * F * Qh
    Th[..., n_harmonics + 1:] = 0.0
    return np.fft.irfft(Th * M, n=M, axis=-1)
