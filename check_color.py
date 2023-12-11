import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


def dominant_colors(image_path, num_clusters=2):
    # Load the image
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Flatten the image to get a list of pixels
    pixels = image.reshape((-1, 3))

    # Apply K-means to get the clusters
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(pixels)

    # Get the cluster centers (dominant colors)
    dominant_colors = kmeans.cluster_centers_.astype(int)

    return dominant_colors