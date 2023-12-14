import numpy as np
import pandas as pd
from skimage.io import imread
from skimage.morphology import disk, binary_erosion, binary_closing, binary_dilation, label
from skimage.measure import regionprops_table,regionprops, label
import matplotlib.pyplot as plt
from skimage.measure import find_contours
from math import pi
from scipy.stats import cumfreq
import cv2

def plot_PSSD(img_path,board_size,Max_Grain_Size):
    # %% %%%%%%%%%%%%%%%%%%%%%%%%%%%%% INPUT DATA %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Input files
    
    input_image = imread(img_path)
    input_image= input_image[:,:,1]
    input_image= input_image>0

    # Input parameters
    n_bins = 10
    board = board_size
    #%%%%%%%%%%%%%%%% Parameters %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    n_bounding_box = 5 / 100
    x, y = input_image.shape[:2]
    pixel_size = board / (max(x,y)*(1+n_bounding_box))
    #Max_Grain_Size = 30

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%Variables%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    binning = np.linspace(0, 1.1 * Max_Grain_Size, n_bins)  # binning in mm
    V_eq_bin = np.zeros(n_bins)
    N_bin = np.zeros(n_bins)
    Aspect_Ratio_bin = np.zeros(n_bins)
    Perim_bin = np.zeros(n_bins)

    #%%%%%%%%%%%%%%% Calculations (BinMap morphological pre-treatment)%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    SE = disk(1)

    input_image = binary_erosion(input_image, SE)
    input_image = binary_closing(input_image, SE)
    input_image = binary_dilation(input_image, SE)


    #%%%%%%%%%%%%%%%%%%%% Calculations (PSSD BinMap)%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    bin_image = input_image
    bin_image = bin_image.astype(np.uint8)



    # From BinMap to a "Region" map with corresponding Size and Shape properties
    labeled_image= label(bin_image)
    properties = regionprops_table(labeled_image, properties=['equivalent_diameter', 'area', 'perimeter', 'orientation', 'solidity', 'euler_number', 'centroid', 'major_axis_length', 'minor_axis_length'])  # 'xy' specifies that coordinates are in (row, column) format
    properties_table = pd.DataFrame(properties)
    region = label(bin_image)

    Nb_of_Particles = np.max(region)
    Stat_Summary = np.zeros((Nb_of_Particles, 9))
    N = np.arange(1, Nb_of_Particles + 1)


    Stat_Summary[:, 0] = N
    Stat_Summary[:, 1] = properties_table['equivalent_diameter'] * pixel_size
    Stat_Summary[:, 2] = 4/3 * np.pi * (Stat_Summary[:, 1]/2) ** 3 * pixel_size ** 3
    Stat_Summary[:, 3] = properties_table['major_axis_length'] / properties_table['minor_axis_length']

    #for i in range(Nb_of_Particles):
    #    Stat_Summary[i, 4] = properties_table['perimeter'][i] / np.sum(measure.perimeter(Properties[i].convex_image))

    Stat_Summary[:, 5] = properties_table['orientation']
    Stat_Summary[:, 6] = properties_table['euler_number']
    Stat_Summary[:, 7] = properties_table['solidity']


    for i in range(Nb_of_Particles):
        # Assurez-vous que l'index est correct
        Stat_Summary[i, 8] = properties_table['perimeter'][i] / (np.pi * properties_table['equivalent_diameter'][i])

    Name_Excel = ['N', 'Equivalent Diameter', 'Equivalent Volume', 'Aspect ratio', 'Waviness', 'Orientation', 'Euler Number', 'Solidity', 'Perimeter/P_Circle_eq']
    T_Excel = pd.DataFrame(Stat_Summary, columns=Name_Excel)
    T_Excel.to_excel('v0.3//PSSD_Cluster.xlsx', index=False)


    def stat_summary(array):
        return [np.mean(array), np.std(array), np.min(array), np.percentile(array, 10), np.percentile(array, 25),
                np.median(array), np.percentile(array, 75), np.percentile(array, 90), np.max(array)]

    Stat_Summary_Table = np.zeros((8, 9))
    for i in range(8):
        Stat_Summary_Table[i, :] = stat_summary(Stat_Summary[:, i+1])
    # Création du tableau T
    # Noms des propriétés
    Name = ['Equivalent Diameter', 'Equivalent Volume', 'Aspect ratio', 'Waviness', 'Orientation', 'Euler Number', 'Solidity', 'Perimeter/P_Circle_eq']

    # Données
    Mean = Stat_Summary_Table[:, 0]
    Stdev = Stat_Summary_Table[:, 1]
    Minimum = Stat_Summary_Table[:, 2]
    Decile_1 = Stat_Summary_Table[:, 3]
    Quartile_1 = Stat_Summary_Table[:, 4]
    Median = Stat_Summary_Table[:, 5]
    Quartile_3 = Stat_Summary_Table[:, 6]
    Decile_9 = Stat_Summary_Table[:, 7]
    Maximum = Stat_Summary_Table[:, 8]

    # Création du DataFrame
    T = pd.DataFrame({
        'Name': Name,
        'Mean': Mean,
        'Stdev': Stdev,
        'Minimum': Minimum,
        'Decile_1': Decile_1,
        'Quartile_1': Quartile_1,
        'Median': Median,
        'Quartile_3': Quartile_3,
        'Decile_9': Decile_9,
        'Maximum': Maximum
    })

    # Extraction des colonnes D_eq et V_eq de Stat_Summary
    D_eq = Stat_Summary[:, 1]
    V_eq = Stat_Summary[:, 2]

    # Extraction de la colonne D_eq de Stat_Summary
    D_eq = Stat_Summary[:, 1]

    # Extraction de la colonne V_eq de Stat_Summary
    V_eq = Stat_Summary[:, 2]

    # Initialisation des tableaux pour les bins
    V_eq_bin = np.zeros(n_bins)
    Aspect_Ratio_bin = np.zeros(n_bins)
    Perim_bin = np.zeros(n_bins)
    N_bin = np.zeros(n_bins)

    # Boucle pour remplir les bins
    for i in range(Nb_of_Particles):
        for j in range(1, n_bins - 1):
            if binning[j-1] < D_eq[i] < binning[j]:
                V_eq_bin[j] += V_eq[i]
                Aspect_Ratio_bin[j] = (N_bin[j] * Aspect_Ratio_bin[j] + Stat_Summary[i, 3]) / (N_bin[j] + 1)
                Perim_bin[j] = (N_bin[j] * Perim_bin[j] + Stat_Summary[i, 8]) / (N_bin[j] + 1)
                N_bin[j] += 1

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%OUTPUT DATA%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Plot 1
    # Plot 1
    fig_1, ax1 = plt.subplots()
    ax1.plot(binning, 100 * np.cumsum(V_eq_bin) / np.max(np.cumsum(V_eq_bin)), 'k', linewidth=2)
    ax1.set_ylabel('Cumulative Size Distribution [%]')
    ax1.set_xlabel('Diameter [mm]')
    ax1.set_ylim([0, 110])

    # Ajout d'un axe secondaire à droite
    ax2 = ax1.twinx()
    ax2.plot(binning, V_eq_bin / np.max(np.cumsum(V_eq_bin)), 'r', linewidth=2)
    ax2.set_ylabel('PSD')

    # Personnalisation de l'affichage
    ax1.grid()
    ax1.grid(which='minor', linestyle='--')
    ax1.tick_params(axis='both', labelsize=14)
    ax2.tick_params(axis='y', labelsize=14)

    # Affichage
    fig_1.savefig('v0.3\\static\\images\\cumulative_size_distrib.png')

    plt.close()

    # Plot 2
    fig_2, ax1 = plt.subplots()
    ax1.plot(binning, 100 * np.cumsum(np.random.randn(len(binning))), 'k--', linewidth=1)
    ax1.set_ylabel('Cumulative Size Distribution [%]')
    ax1.set_xlabel('Diameter [mm]')
    ax1.set_ylim([0, 110])

    # Ajout d'un axe secondaire à droite
    ax2 = ax1.twinx()
    ax2.plot(binning, Aspect_Ratio_bin, 'r', label='Aspect Ratio', linewidth=2)
    ax2.plot(binning, Perim_bin, 'b-', label='Roughness', linewidth=2)
    ax2.set_ylabel('Aspect Ratio & Roughness')

    # Personnalisation de l'affichage
    ax1.grid()
    ax1.grid(which='minor', linestyle='--')
    ax1.tick_params(axis='both', labelsize=14)
    ax2.tick_params(axis='y', labelsize=14)

    # Ajout de la légende
    ax2.legend(loc='upper left')

    # Affichage
    fig_2.savefig('v0.3\\static\\images\\cumulative_size_aspect.png')
    plt.close()

    # Plot 3
    fig_3, ax = plt.subplots()
    ax.hist(Aspect_Ratio_bin, bins=10)
    ax.set_xlabel('Aspect Ratio')
    ax.grid()
    ax.tick_params(axis='both', labelsize=14)

    # Affichage
    fig_3.savefig('v0.3\\static\\images\\aspect_ratio.png')
    plt.close()

    # Plot 4
    fig_4, ax = plt.subplots()
    ax.hist(Perim_bin, bins=10)
    ax.set_xlabel('Roughness')
    ax.grid()
    ax.tick_params(axis='both', labelsize=14)

    # Affichage
    fig_4.savefig('v0.3\\static\\images\\roughness.png')
    plt.close()

