import numpy as np
from sklearn.cluster import KMeans
from sklearn.utils import shuffle
from functools import lru_cache

def recreate_image(codebook: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Recreate the (compressed) image from the code book & labels"""
    return codebook[labels].astype(np.uint8)

def kmeans_quantize(img: np.ndarray, n_colors: int = 50) -> np.ndarray:
    image_array_sample = shuffle(img, random_state=0, n_samples=1_000)
    kmeans = KMeans(n_clusters=n_colors, random_state=0).fit(image_array_sample)

    # Get labels for all points
    labels = kmeans.predict(img)
    return recreate_image(kmeans.cluster_centers_, labels)
