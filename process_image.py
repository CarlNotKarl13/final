import cv2
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
import matplotlib.pyplot as plt
from skimage.measure import regionprops, label
from scipy import ndimage
import matplotlib.pyplot as plt



def process_image(input_img_path):
    ############################################################################
    ####################### Aggregate process of the python file #################
    ############################################################################
    # Load the image from the file path
    Input_RGB_Image = cv2.imread(input_img_path)[..., ::-1]
    Input_BW_Image = Input_RGB_Image[:, :, 0] 
    print('test')
    n_Colors = 2
    colors = [
        [0, 0, 0],
        [0, 0, 1],
        [0, 1, 1],
        [0, 1, 0],
        [1, 1, 0],
        [1, 0, 0],
        [1, 1, 1],
        [1, 0, 1]
    ]

    X, Y, _ = Input_RGB_Image.shape
     # VARIABLES
    Stack = np.zeros((X, Y, 4), dtype=np.float32)
    Surface_Area = np.zeros(n_Colors)
    Cluster_Name = [""] * n_Colors
    # CALCULATIONS
    Edge_BSE_Image = cv2.Canny(Input_BW_Image, 100, 200) / 255.0
    Edge_Smoothed_BSE_Image = cv2.GaussianBlur(Edge_BSE_Image, (0, 0), 1)

    Transformed_RGB_Image = Input_RGB_Image / 255.0

    Stack[:, :, :3] = Transformed_RGB_Image
    Stack[:, :, 3] = Edge_BSE_Image
    print('test2')

    pixels = Input_RGB_Image.reshape((-1, 3))
    kmeans = KMeans(n_clusters=n_Colors, n_init=3).fit(pixels)
    pixel_labels = kmeans.labels_.reshape(X, Y)

    print('test3')
    masks = [pixel_labels == i for i in range(n_Colors)]
    clusters = [Input_RGB_Image * mask[:, :, np.newaxis] for mask in masks]
    areas = [np.mean(mask) for mask in masks]

    for i, area in enumerate(areas):
        Surface_Area[i] = 100 * area
        Cluster_Name[i] = f"Cluster {i+1}"

    Matrix = np.zeros((X, Y, 3, n_Colors))

    for s in range(3):
        for i in range(n_Colors):
            Matrix[:, :, s, i] = masks[i] * colors[i][s]

    RGB_Clusters = np.sum(Matrix, axis=3)
    # Create table using pandas

    T = pd.DataFrame({
        'Cluster_Name': Cluster_Name,
        'Surface_Area': Surface_Area
    })
    
    print(T)
    
        # FIGURES
    plt.figure(1)
    plt.imshow(Input_RGB_Image)
    plt.title('Input RGB Image')
    plt.savefig('v0.3\static\images\input_rgbb_image.png')
    plt.close()            
    print("test ultime")
    plt.figure(2)
    plt.imshow(Input_BW_Image, cmap='gray') 
    plt.title('Input BW Image')
    plt.savefig('v0.3\static\images\input_bw_image.png')
    plt.close()
    print("test ultime")
    plt.figure(3)
    plt.imshow(RGB_Clusters)
    plt.title('RGB Clusterized image')
    plt.savefig('v0.3\static\images\gb_clusterized_image.png')
    plt.close()
    print("test ultime")
    plt.figure(4)
    plt.imshow(Edge_BSE_Image, cmap='gray')
    plt.title('Edge Detection')
    plt.savefig('v0.3\static\images\edge_detection.png')
    plt.close()

    plt.figure(5)
    plt.imshow(Edge_Smoothed_BSE_Image, cmap='gray')
    plt.title('Smoothed Edge Detection')
    plt.savefig('v0.3\static\images\smoothed_edge_detection.png')
    plt.close()

####################################################################################
############################# PSSD PART OF THE PYTHON PROGRAM #########################
########################################################################################
    Input_Image = cv2.imread('C:\\Users\\carl1\\OneDrive\\Bureau\\CESI\\v0.5\\test_feature\\virtual_lab1\\Big_Red_Board_6-12_Paint_Corrected.png',cv2.IMREAD_GRAYSCALE)
    board_height = 800
    n_bins = 10
    Max_Grain_Size = 20
    X, Y = Input_Image.shape
    I = Input_Image > 0

    # VARIABLES
    binning = np.linspace(0, 1.1 * Max_Grain_Size, n_bins)
    V_eq_bin = np.zeros(n_bins)
    N_bin = np.zeros(n_bins)

    # CALCULATIONS
    pixel_size = X / board_height
    Bin_Image = I.astype(np.uint8)
    label_image = label(Bin_Image)  # Label connected components

    # Use 'intensity_image' to specify properties
    Properties_table = regionprops(label_image, intensity_image=Bin_Image)

    Nb_of_Particles = len(Properties_table)
    Stat_Summary = np.zeros((Nb_of_Particles, 3))

    for i, prop in enumerate(Properties_table):
        major_axis_length = prop.major_axis_length
        minor_axis_length = prop.minor_axis_length
        equivalent_diameter = np.sqrt(4 * prop.area / np.pi)  # Calculate equivalent diameter using area
        Stat_Summary[i, 1] = equivalent_diameter * pixel_size
        Stat_Summary[i, 2] = 4/3 * np.pi * (equivalent_diameter / 2)**3 * pixel_size**3

    D_eq = Stat_Summary[:, 1]
    V_eq = Stat_Summary[:, 2]

    for i in range(Nb_of_Particles):
        for j in range(1, n_bins-1):
            if binning[j-1] < D_eq[i] < binning[j]:
                V_eq_bin[j] += V_eq[i]
                N_bin[j] += 1
    print("hello test")
    # OUTPUT DATA
    fig_1 = plt.figure(1)
    plt.plot(binning, 100 * np.cumsum(V_eq_bin)/max(np.cumsum(V_eq_bin)), 'k', linewidth=2)
    plt.ylabel('Cumulative Size Distribution [%]')
    plt.axis([0, max(binning), 0, 110])
    plt.twinx()
    plt.plot(binning, V_eq_bin/max(np.cumsum(V_eq_bin)), 'r', linewidth=2)
    plt.grid()
    plt.minorticks_on()
    plt.xlabel('Diameter [mm]')
    plt.ylabel('PSD')
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    
    # Enregistrer la figure 1
    fig_1.savefig('v0.3\static\images\cumulative_size.png')

    fig_2 = plt.figure(2)
    plt.imshow(I, cmap='gray')
    plt.close()
    # Enregistrer la figure 2
    fig_2.savefig('v0.3\\static\\images\\binary.png')
    print("hello test2")
    # Créez une série pandas à partir des valeurs que vous souhaitez enregistrer
    data = pd.Series(100 * np.cumsum(V_eq_bin)/max(np.cumsum(V_eq_bin)))

    # Créez une série pandas pour binning
    binning_series = pd.Series(binning)

    # Créez une série pandas pour V_eq_bin/max(np.cumsum(V_eq_bin))
    v_eq_ratio_series = pd.Series(V_eq_bin / max(np.cumsum(V_eq_bin)))

    # Créez un DataFrame pandas à partir de toutes les séries
    df = pd.DataFrame({
        'Binning (mm)': binning_series,
        'Cumulative Size Distribution (%)': data,
        'V_eq_bin_ratio': v_eq_ratio_series
    })

    # Enregistrez le DataFrame dans un fichier Excel
    df.to_excel('v_eq_data.xlsx', index=False)  # Modifiez le nom du fichier si nécessaire
    print("where are you ")