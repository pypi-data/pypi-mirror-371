"""
Threshold algorithms for image preprocessing.
"""

import numpy as np

__all__ = ["median_threshold", "otsu_threshold"]


def median_threshold(arr: np.ndarray) -> int:
    """
    Compute the median threshold of a grayscale image array.

    The threshold is the median value of the pixel intensities.

    Parameters:
        arr: 2D numpy array of dtype uint8.

    Returns:
        threshold value as int.
    """
    return int(np.median(arr))


def otsu_threshold(arr: np.ndarray) -> int:
    """
    Compute Otsu's threshold for a uint8 grayscale image array.

    Implements Otsu's method by maximizing inter-class variance.

    Parameters:
        arr: 2D numpy array of dtype uint8.

    Returns:
        threshold value as int.
    """
    # Compute histogram and probabilities
    hist = np.bincount(arr.flatten(), minlength=256).astype(np.float64)
    prob = hist / hist.sum()
    # Cumulative sums
    omega = np.cumsum(prob)
    mu = np.cumsum(prob * np.arange(256))
    mu_t = mu[-1]
    # Between-class variance
    denom = omega * (1 - omega)
    denom[denom == 0] = np.nan  # avoid division by zero
    sigma_b_sq = (mu_t * omega - mu) ** 2 / denom
    return int(np.nanargmax(sigma_b_sq))
