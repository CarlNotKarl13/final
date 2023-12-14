
import numpy as np
import pandas as pd
from skimage.morphology import disk, binary_opening, binary_erosion, binary_dilation
from skimage.filters import median
from skimage.measure import regionprops_table, label
from skimage.morphology import disk, binary_opening, binary_erosion, binary_dilation
from scipy.ndimage import binary_fill_holes
from scipy.special import ellipe
import matplotlib.pyplot as plt
from math import pi
from imageio import imread, imwrite
import imageio.v2 as imageio

import skimage
from skimage import io, morphology, measure
from scipy.ndimage import label
from skimage.morphology import disk, binary_opening, binary_erosion, binary_dilation
from skimage.filters import median
from skimage.measure import regionprops_table, label
from scipy.ndimage import binary_fill_holes
import matplotlib.pyplot as plt


def necking(img_path,board_heights):
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% INPUT DATA %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    input_image = imageio.imread(img_path)
    board_height = board_heights  # [mm]
    #nb_of_sieves = 6
#nb_of_sieves = 6

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% PARAMETERS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    erosion_mm = 2
    eic_multiplier = 1

    #input_image = input_image[:, :, 1]
    x, y = input_image.shape
    Logical = input_image > 0

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% VARIABLES %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%% CALCULATIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    pixel_size = board_height/x
    print(pixel_size)
    #n_hood_close = disk(2)
    #n_hood_erode = disk(round(erosion_mm / pixel_size))
    #n_hood_erode = disk(10)
    #n_hood_dilation = disk(2)

    #A = median(Logical)
    #B = binary_opening(A, n_hood_close)
    #C = binary_erosion(B, n_hood_erode)
    #bin_image = C.astype(np.uint8)

    SE = morphology.disk(1)
    Powder = morphology.binary_erosion(Logical, SE)
    Powder = morphology.binary_closing(Powder, SE)
    Powder = morphology.binary_dilation(Powder, SE)
    # Berechnungen
    Bin_Image = Powder
    bin_image = Bin_Image.astype(np.uint8)

    labeled_image = label(bin_image)
    plt.imshow(labeled_image, cmap='turbo')  # Using a colormap that provides distinct colors
    plt.colorbar()  # Optional: to show the color scale
    plt.savefig('v0.3\static\images\labeled_image.png', bbox_inches='tight')
    plt.close()

    properties = regionprops_table(labeled_image, properties=['equivalent_diameter', 'area', 'perimeter', 'orientation', 'solidity', 'euler_number', 'centroid', 'major_axis_length', 'minor_axis_length'])
    properties_table = pd.DataFrame(properties)
    #region = label(bin_image)
    nb_of_particles = properties_table.shape[0]
    N = np.arange(1, nb_of_particles + 1)

    # Creating the Stat_Summary
    # Initialisation de Stat_Summary
    stat_summary = np.zeros((nb_of_particles, 9))

    # Remplissage des colonnes de Stat_Summary
    stat_summary[:, 0] = N
    stat_summary[:, 1] = properties_table['equivalent_diameter'] * pixel_size  # Change 'equiv_diameter' to 'equivalent_diameter'
    stat_summary[:, 2] = 4/3 * pi * (stat_summary[:, 1]/2) ** 3 * pixel_size ** 3
    stat_summary[:, 3] = properties_table['major_axis_length'] / properties_table['minor_axis_length']
    # Calcul de la colonne "Waviness"
    #for i in range(nb_of_particles):
        # Access 'convex_image' property from properties_table
    #    perimeter_image = binary_fill_holes(properties_table['convex_image'][i]) #erreur de calcul 
    #    stat_summary[i, 4] = properties_table['perimeter'][i] / np.sum(perimeter_image)
    stat_summary[:, 5] = properties_table['orientation']
    stat_summary[:, 6] = properties_table['euler_number']
    stat_summary[:, 7] = properties_table['solidity']
    # Calcul de la dernière colonne
    for i in range(nb_of_particles):
        stat_summary[i, 8] = properties_table['perimeter'][i] / (np.pi * properties_table['equivalent_diameter'][i])
    #for i in range(nb_of_particles):
        # a =  properties_table['major_axis_length'][i] 
        # b =  properties_table['minor_axis_length'][i] 
        # if b < a:
        #     e = np.sqrt(1 - (b**2 / a**2))
        #     perimetre = 4 * a * ellipe(e**2)
        # else:
        #     e=1
        #     perimetre = np.pi * properties_table['equivalent_diameter'][i]
        # stat_summary[i, 8] = properties_table['perimeter'][i] / (np.pi * properties_table['equivalent_diameter'][i])
        #stat_summary[i, 8] = properties_table['perimeter'][i] / perimetre

    # Création de Stat_Summary_Table
    stat_summary_table = np.zeros((8, 9))

    # Calcul des statistiques récapitulatives
    for i in range(8):
        stat_summary_table[i, :] = np.array([np.mean(stat_summary[:, i+1]), np.std(stat_summary[:, i+1]), np.min(stat_summary[:, i+1]), np.percentile(stat_summary[:, i+1], 10), np.percentile(stat_summary[:, i+1], 25), np.median(stat_summary[:, i+1]), np.percentile(stat_summary[:, i+1], 75), np.percentile(stat_summary[:, i+1], 90), np.max(stat_summary[:, i+1])])

    # Création de la table finale
    names = ['Equivalent Diameter', 'Equivalent Volume', 'Aspect ratio', 'Waviness', 'Orientation', 'Euler Number', 'Solidity', 'Perimeter/P_Circle_eq']
    t = pd.DataFrame(stat_summary_table, columns=['Mean', 'Stdev', 'Minimum', 'Decile_1', 'Quartile_1', 'Median', 'Quartile_3', 'Decile_9', 'Maximum'], index=names)
    print(t)
    # Nettoyage de la matrice de sortie des grains déformés
    eic = stat_summary_table[7, 6] - stat_summary_table[7, 4]
    threshold_up_perimeter = stat_summary_table[7, 6] + eic_multiplier * eic
    threshold_down_perimeter = stat_summary_table[7, 6] - eic_multiplier * eic

    list_necking_grains = np.zeros(nb_of_particles)

    for i in range(nb_of_particles):
        if stat_summary[i, 8] > threshold_up_perimeter or stat_summary[i, 8] < threshold_down_perimeter:# or stat_summary[i, 3] > 2 or stat_summary[i, 1] > stat_summary_table[0, 6] + eic_multiplier*(stat_summary_table[0, 7]-stat_summary_table[0, 5]):
        #if stat_summary[i, 1] > stat_summary_table[0, 6] + eic_multiplier*(stat_summary_table[0, 7]-stat_summary_table[0, 5]):    
        #if stat_summary[i, 3] > 2:
            print([i, stat_summary[i,1]])
            #print(stat_summary[i,1])
            # ajouter un critère sur la taille tout simplement: ça ne peut pas être trop gros non plus
            list_necking_grains[i] = stat_summary[i,0]# Le -1 sert à recaler list necking grain sur region (fonction np.isin ci-dessous)

    selected_grains = np.isin(labeled_image, list_necking_grains) 

    #n_hood_erode = disk(round(erosion_mm/pixel_size)-1)
    #selected_grains = binary_dilation(~selected_grains, n_hood_dilation)
    selected_grains = ~selected_grains

    name_excel = ['N', 'Equivalent Diameter', 'Equivalent Volume', 'Aspect ratio', 'Waviness', 'Orientation', 'Euler Number', 'Solidity', 'Perimeter/P_Circle_eq']
    t_excel = pd.DataFrame(stat_summary, columns=name_excel)
    t_excel.to_excel('PSSD_Cluster.xlsx', index=False)

    # Préparation de l'image des grains sélectionnés en couleur
    selected_grains_colors = np.zeros((x, y, 3))
    selected_grains_colors[:, :, 0] = input_image
    selected_grains_colors[:, :, 1] = 255*selected_grains
    selected_grains_colors[:, :, 2] = 255*selected_grains

    # Sauvegarde des images
    output_path = 'v0.3/static/images/Selected_Grains_Colors.png'
    imageio.imwrite(output_path, selected_grains_colors.astype(np.uint8))
    max_grains_size = np.max(stat_summary[:, 1])
    return output_path, max_grains_size

