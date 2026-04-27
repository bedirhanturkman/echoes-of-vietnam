"""
Data transformation utilities.
Normalization, scaling, outlier detection, and coordinate validation.
"""

import numpy as np
from typing import Optional


def min_max_normalize(values: np.ndarray, new_min: float = 0.0, new_max: float = 100.0) -> np.ndarray:
    """
    Normalize values to [new_min, new_max] range.
    Used to convert t-SNE coordinates to 0-100 range for frontend compatibility.
    """
    v_min = np.min(values)
    v_max = np.max(values)

    if v_max - v_min == 0:
        # All values are the same — place at midpoint
        return np.full_like(values, (new_min + new_max) / 2, dtype=float)

    normalized = (values - v_min) / (v_max - v_min)
    return normalized * (new_max - new_min) + new_min


def clip_outliers_iqr(values: np.ndarray, factor: float = 1.5) -> np.ndarray:
    """
    Clip outliers using the Interquartile Range (IQR) method.
    Values beyond Q1 - factor*IQR and Q3 + factor*IQR are clipped.
    """
    q1 = np.percentile(values, 25)
    q3 = np.percentile(values, 75)
    iqr = q3 - q1

    lower_bound = q1 - factor * iqr
    upper_bound = q3 + factor * iqr

    return np.clip(values, lower_bound, upper_bound)


def validate_vietnam_coordinates(lat: Optional[float], lon: Optional[float]) -> bool:
    """
    Check if coordinates fall within Vietnam's approximate bounding box.
    Latitude:  8.0 - 23.5
    Longitude: 102.0 - 110.0
    """
    if lat is None or lon is None:
        return False
    return 8.0 <= lat <= 23.5 and 102.0 <= lon <= 110.0


def validate_war_date(year: int) -> bool:
    """
    Check if a year falls within the Vietnam War era (1955-1975).
    Includes some buffer for context events.
    """
    return 1955 <= year <= 1975


def linear_map(value: float, in_min: float, in_max: float,
               out_min: float, out_max: float) -> float:
    """
    Linearly map a value from one range to another.
    Used for mapping data dimensions to musical parameters.

    Example: sentiment (-1 to 1) → velocity (40 to 120)
    """
    if in_max - in_min == 0:
        return (out_min + out_max) / 2

    ratio = (value - in_min) / (in_max - in_min)
    ratio = max(0.0, min(1.0, ratio))  # Clamp to [0, 1]
    return ratio * (out_max - out_min) + out_min


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))
