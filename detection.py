import cv2
import numpy as np
from skimage import color, morphology, measure
from scipy.ndimage import median_filter
from sklearn.cluster import KMeans
from scipy import ndimage as ndi


def detection_image(input_image_path,board_heights):
    # %% %%%%%%%%%%%%%%%%%%%%%%%%%%%%% INPUT DATA %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    Aggregates_Image = cv2.imread(input_image_path)
    board_height = board_heights  # [mm]

    n_bounding_box = 5 / 100
    n_morpho = 0.1 / 100
    print('1')
    # %% %%%%%%%%%%%%%%%%%%%%%%%%%%%% PARAMETERS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    X, Y, Z = Aggregates_Image.shape
    n_morpho = n_morpho * max(X, Y)  # Change '5' to the number of pixels for opening
    n_bounding_box = n_bounding_box * max(X, Y)
    print('2')
    # %% %%%%%%%%%%%%%%%%%%%%%%%%%%% CALCULATIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Transformation into hsv and Recovery of the "s" layer (saturation layer)
    Agg_Image_hsv = cv2.cvtColor(Aggregates_Image, cv2.COLOR_BGR2HSV)
    Agg_Image_s = median_filter(Agg_Image_hsv[:, :, 1], size=(5, 5))
    print('3')
    # Clustering of the "s" layer into 2 clusters
    V_Agg_Image_s = Agg_Image_s.reshape(X * Y, 1)
    kmeans = KMeans(n_clusters=2).fit(V_Agg_Image_s)
    idx = kmeans.labels_
    Clustered_Image = idx.reshape(X, Y).astype(np.uint8)
    Cluster1_bin = (idx == 0).reshape(X, Y)
    Cluster2_bin = (idx == 1).reshape(X, Y)
    Cluster1 = Agg_Image_s * Cluster1_bin.astype(np.uint8)
    Cluster2 = Agg_Image_s * Cluster2_bin.astype(np.uint8)
    print('4')
    # Identification of the backboard by the cluster having the max average "s" value
    Average_Cluster_1_Color = np.mean(Cluster1[Cluster1 != 0])
    Average_Cluster_2_Color = np.mean(Cluster2[Cluster2 != 0])

    Backboard_bin = Cluster2_bin if Average_Cluster_2_Color > Average_Cluster_1_Color else Cluster1_bin
    print('44')
    # Morphological operation on the backgoard
    se = morphology.disk(round(n_morpho))
    print(n_morpho)
    Backboard_filled = ndi.binary_fill_holes(Backboard_bin)
    print('45')
    Backboard_opened = morphology.binary_opening(Backboard_filled, se)
    print('5')
    # Edge detection
    Labeled_Image, numAreas = measure.label(Backboard_opened, return_num=True)
    stats = measure.regionprops(Labeled_Image)
    areas = [prop.area for prop in stats]
    maxAreaIndex = np.argmax(areas)
    Largest_Area_Image = (Labeled_Image == maxAreaIndex + 1)
    print('6')
    stats = measure.regionprops(Largest_Area_Image.astype(int))
    bbox = stats[0].bbox
    print(bbox)
    adjustedBbox = [bbox[1] + n_bounding_box, bbox[0] + n_bounding_box, bbox[3] - 2 * n_bounding_box, bbox[2] - 2 * n_bounding_box]

    x1 = round(adjustedBbox[0])
    y1 = round(adjustedBbox[1])
    x2 = round(adjustedBbox[2])
    y2 = round(adjustedBbox[3])
    print('7')
    # Extract the pixels within the adjusted box
    Extracted_Image = Aggregates_Image[y1:y2, x1:x2]
    print('8')
    # %% %%%%%%%%%%%%%%%%%%%%%%%%%%% OUTPUT DATA %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    pixel_size = board_height / max(bbox[3] - bbox[1], bbox[2] - bbox[0])
    output_path='v0.3/static/images/Extracted_Image.png'
    cv2.imwrite(output_path, Extracted_Image)
   
    print('9')
    # %% %%%%%%%%%%%%%%%%%%%%%%%%%%%%% FIGURES %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # You can use matplotlib to display images as in MATLAB.
    return output_path

