from skimage import io, morphology, measure
from scipy.ndimage import label
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from skimage.morphology import disk, binary_opening, binary_erosion, binary_dilation
from skimage.filters import median
from skimage.measure import regionprops_table, label
from scipy.ndimage import binary_fill_holes
import matplotlib.pyplot as plt
from math import pi
from imageio import imread, imwrite
import imageio.v2 as imageio


def graph_PSSD(img_path):
    # Laden des Bildes
    Powder = io.imread(img_path)
    Powder = Powder[:, :, 0]
    Powder = Powder > 0  # Converting to logical

    # Schwellenwerte
    Threshold_up_Perimeter = 1.5
    Threshold_down_Perimeter = 0.9
    Threshold_Aspect_Ratio = 1.1

    # Parameter
    X, Y = Powder.shape
    pixel_size = 0.3

    # Variablen
    Aspect_Ratio_Map = np.zeros((X, Y))
    Perimeter_Waviness = np.zeros((X, Y))
    Size_Map = np.zeros((X, Y))

    # Morphologische Vorbehandlung
    SE = morphology.disk(1)
    Powder = morphology.binary_erosion(Powder, SE)
    Powder = morphology.binary_closing(Powder, SE)
    Powder = morphology.binary_dilation(Powder, SE)

    # Berechnungen
    Bin_Image = Powder
    Bin_Image = Bin_Image.astype(np.uint8)

    ##########################################################

    labeled_image = label(Bin_Image)
    Properties = regionprops_table(labeled_image, properties=['equivalent_diameter', 'area', 'perimeter', 'orientation', 'solidity', 'euler_number', 'centroid', 'major_axis_length', 'minor_axis_length'])
    Properties_table = pd.DataFrame(Properties)
    #region = label(bin_image)

    ##################################################################

    #Properties = measure.regionprops(Bin_Image)
    #Properties_table = measure.regionprops_table(Bin_Image, properties=('equivalent_diameter', 'area', 'perimeter', 'orientation', 'solidity', 'euler_number', 'centroid', 'major_axis_length', 'minor_axis_length', 'convex_image'))
    Region= label(Bin_Image)

    print(Properties_table)
    # Erstellung der PSSD-Tabelle
    Nb_of_Particles = np.max(Region)
    Stat_Summary = np.zeros((Nb_of_Particles, 9))
    N = np.arange(1, Nb_of_Particles + 1)
    print(Nb_of_Particles)

    print(Properties_table['equivalent_diameter'])
    Stat_Summary[:, 0] = N
    Stat_Summary[:, 1] = Properties_table['equivalent_diameter'] * pixel_size
    Stat_Summary[:, 2] = 4/3 * np.pi * (Stat_Summary[:, 1]/2) ** 3 * pixel_size ** 3
    Stat_Summary[:, 3] = Properties_table['major_axis_length'] / Properties_table['minor_axis_length']

    #for i in range(Nb_of_Particles):
    #    Stat_Summary[i, 4] = Properties_table['perimeter'][i] / np.sum(measure.perimeter(Properties[i].convex_image))

    Stat_Summary[:, 5] = Properties_table['orientation']
    Stat_Summary[:, 6] = Properties_table['euler_number']
    Stat_Summary[:, 7] = Properties_table['solidity']

    for i in range(Nb_of_Particles):
        Stat_Summary[i, 8] = Properties_table['perimeter'][i] / (np.pi * Properties_table['equivalent_diameter'][i])

    # Export als Excel-Datei
    Name_Excel = ['N', 'Equivalent Diameter', 'Equivalent Volume', 'Aspect ratio', 'Waviness', 'Orientation', 'Euler Number', 'Solidity', 'Perimeter/P_Circle_eq']
    T_Excel = pd.DataFrame(Stat_Summary, columns=Name_Excel)
    T_Excel.to_excel('PSSD_Cluster.xlsx', index=False)

    # Statistikberechnung
    def stat_summary(array):
        return [np.mean(array), np.std(array), np.min(array), np.percentile(array, 10), np.percentile(array, 25),
                np.median(array), np.percentile(array, 75), np.percentile(array, 90), np.max(array)]

    Stat_Summary_Table = np.zeros((8, 9))
    for i in range(8):
        Stat_Summary_Table[i, :] = stat_summary(Stat_Summary[:, i+1])

    # Tabellenerstellung
    Name = ['Equivalent Diameter', 'Equivalent Volume', 'Aspect ratio', 'Waviness', 'Orientation', 'Euler Number', 'Solidity', 'Perimeter/P_Circle_eq']
    T = pd.DataFrame(Stat_Summary_Table, columns=['Mean', 'Stdev', 'Minimum', 'Decile_1', 'Quartile_1', 'Median', 'Quartile_3', 'Decile_9', 'Maximum'])
    T.insert(0, 'Name', Name)

    # Karten für das Seitenverhältnis und die "Welligkeit" des Umfangs
    print(Nb_of_Particles)
    for i in range(X):
        for j in range(Y):
            Index = Region[i, j]
            if Index > 0 :
                Aspect_Ratio_Map[i, j] = 1 + Stat_Summary[Index - 1, 3]
                Perimeter_Waviness[i, j] = 1 + Stat_Summary[Index - 1, 8]
                Size_Map[i, j] = 1 + Stat_Summary[Index - 1, 1]

    Aspect_Ratio_Map = Aspect_Ratio_Map * Powder
    Perimeter_Waviness = Perimeter_Waviness * Powder
    Size_Map = Size_Map * Powder

    Aspect_Ratio_Map = Aspect_Ratio_Map / np.quantile(Aspect_Ratio_Map.max(), 0.9) * 255
    Perimeter_Waviness = Perimeter_Waviness / Perimeter_Waviness.max() * 255
    Size_Map = Size_Map / np.quantile(Size_Map, 0.9) * 255


    # %% %%%%%%%%%%%%%%%%%%%%%%%%%%%%% FIGURES %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    fig_1 = plt.figure(1)
    plt.imshow(Bin_Image, cmap='gray')
    fig_1.savefig('v0.3\\static\\images\\cumulative_siiize.png')
    plt.close()
    

    fig_2 = plt.figure(2)
    plt.imshow(Aspect_Ratio_Map, cmap='turbo')
    plt.title('Aspect Ratio map')
    fig_2.savefig('v0.3\\static\\images\\aspect_ration.png')
    plt.close()
    

    fig_3 = plt.figure(3)
    plt.imshow(Perimeter_Waviness, cmap='turbo')
    plt.title('Roughness map')
    fig_3.savefig('v0.3\\static\\images\\roughness.png')
    plt.close()
    

    fig_4 = plt.figure(4)
    plt.imshow(Size_Map, cmap='turbo')
    plt.title('Size map') 
    fig_4.savefig('v0.3\\static\\images\\size_map.png')
    plt.close()
   

