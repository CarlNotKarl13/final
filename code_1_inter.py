import cv2
import numpy as np
from sklearn.cluster import KMeans

def segment_and_save_binary_image(input_image_path):
    # Charger l'image en couleur
    original_image = cv2.imread(input_image_path)
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    # Redimensionner l'image pour avoir un tableau 2D d'échantillons
    height, width, _ = original_image.shape
    samples = original_image.reshape((-1, 3))

    # Appliquer l'algorithme K-means avec 2 clusters
    kmeans = KMeans(n_clusters=2)
    kmeans.fit(samples)

    # Obtenir les labels des clusters et les réorganiser pour que le cluster avec la plus petite surface soit le label 0
    labels = kmeans.labels_
    unique_labels, counts = np.unique(labels, return_counts=True)
    smallest_cluster_label = unique_labels[np.argmin(counts)]

    # Créer une image binaire en ne conservant que le cluster avec la plus petite surface
    binary_image = (labels == smallest_cluster_label).reshape((height, width))

    # Sauvegarder l'image binaire directement avec le chemin complet
    output_binary_path = 'v0.3/static/images/Extracted_Image_Binary.png'
    binary_image = binary_image.astype(np.uint8) * 255
    cv2.imwrite(output_binary_path, binary_image)

    # Renvoyer le chemin vers l'image binaire
    return output_binary_path

