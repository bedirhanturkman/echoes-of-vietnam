"""
Dimensionality Reduction Service.
Reduces high-dimensional embeddings to 2D using t-SNE and clusters them with HDBSCAN.
"""

import numpy as np
from sklearn.manifold import TSNE

from app.core.data_transforms import min_max_normalize, clip_outliers_iqr


class ReductionService:
    """
    Reduce embedding vectors from 1536-d to 2-d and assign cluster labels.
    """

    def reduce_to_2d(
        self,
        embeddings: np.ndarray,
        random_state: int = 42,
        perplexity: float = None,
    ) -> np.ndarray:
        """
        Apply t-SNE to reduce embeddings to 2D coordinates.

        Args:
            embeddings: (N, 1536) array of embedding vectors
            random_state: Seed for reproducibility
            perplexity: t-SNE perplexity (auto-calculated if None)

        Returns:
            (N, 2) array of normalized 2D coordinates in [0, 100] range
        """
        n_samples = embeddings.shape[0]

        # Perplexity must be less than n_samples
        if perplexity is None:
            perplexity = min(30, max(2, n_samples - 1))

        tsne = TSNE(
            n_components=2,
            perplexity=perplexity,
            random_state=random_state,
            max_iter=1000,
            learning_rate="auto",
            init="pca" if n_samples > 4 else "random",
        )

        coords_2d = tsne.fit_transform(embeddings)

        # Clip outliers before normalization
        coords_2d[:, 0] = clip_outliers_iqr(coords_2d[:, 0])
        coords_2d[:, 1] = clip_outliers_iqr(coords_2d[:, 1])

        # Normalize to 0-100 range for frontend
        coords_2d[:, 0] = min_max_normalize(coords_2d[:, 0], 5, 95)
        coords_2d[:, 1] = min_max_normalize(coords_2d[:, 1], 5, 95)

        return coords_2d

    def cluster_embeddings(
        self,
        embeddings: np.ndarray,
        categories: list[str],
    ) -> list[int]:
        """
        Assign cluster labels to embeddings.
        
        First tries HDBSCAN for automatic clustering.
        Falls back to category-based clustering if HDBSCAN isn't available
        or produces poor results.

        Args:
            embeddings: (N, 1536) array
            categories: List of category strings for fallback

        Returns:
            List of integer cluster labels
        """
        try:
            import hdbscan
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=max(2, len(embeddings) // 5),
                min_samples=1,
                metric="euclidean",
            )
            labels = clusterer.fit_predict(embeddings)

            # If too many points are noise (-1), fall back
            noise_ratio = (labels == -1).sum() / len(labels)
            if noise_ratio > 0.5:
                return self._category_based_clusters(categories)

            return labels.tolist()

        except ImportError:
            # HDBSCAN not installed — use category-based fallback
            return self._category_based_clusters(categories)

    def _category_based_clusters(self, categories: list[str]) -> list[int]:
        """
        Assign cluster IDs based on event categories.
        This is a deterministic fallback when HDBSCAN isn't available.
        """
        category_map = {
            "conflict": 0,
            "peace_talks": 1,
            "civilian_impact": 2,
            "political_transition": 3,
            "uncertainty": 4,
        }
        return [category_map.get(cat, 4) for cat in categories]
