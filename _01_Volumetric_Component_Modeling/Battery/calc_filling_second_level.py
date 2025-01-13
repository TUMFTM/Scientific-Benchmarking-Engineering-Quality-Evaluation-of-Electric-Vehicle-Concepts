"""
Description: This function fills the second level and calculates how many cells fit in
             total. To fill the second level, the cells which fit in the underbody area
             swapped in X and Y in their orientation to find the optimal configuration
             More information to the battery model can be found in Chapters 3.4.6 of (1) and in Chapter 4.6 of (3)
------------
Sources: (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", P. D. Thesis, Technical University of Munich, Institute of Automotive Technology, 2022
         (2) P. Köhler, „Semi-physikalische Modellierung von Antriebsstrangkomponenten für Elektrofahrzeuge,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021
         (3) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       second_level_dim: Dimensions of the available space for the second row
       cell_dim: Dimensions of the cells used in the underfloor of the vehicle
------------
Output: cell_dim_second_level: Cell Dimensions that also fit in the second level
        pack_dim_second_level: Pack Dimensions that also fit in the second level
        num_cell_second_level: Number of cells that can be placed in the second level
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Filling option is deactivated
[3] Calculate the filling of the second level
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
import numpy as np
# endregion


def calc_filling_second_level(vehicle, second_level_dim, cell_dim):

    # region [1] Assign required Inputs
    check_filling = vehicle.settings.fill_second_level

    batt_cooling = vehicle.dimensions.CZ.batt_cooling    # Height of the cooling plate in mm (2, p. 76)

    # Difference in height (Z-direction) between cell and module in mm (2, p. 76)
    EZ_cell2module = vehicle.dimensions.EZ.cell2module

    # Get the packagefactor to recalculate the pack_dim for the second level cell
    packfactor = vehicle.battery.cell.packagefactor
    # endregion

    # region [2] Filling option is deactivated
    # Option second level deactivated --> set number of cells to 0
    if check_filling == 0:
        cell_dim_second_level = np.zeros(np.shape(cell_dim))
        pack_dim_second_level = np.zeros(np.shape(cell_dim))
        num_cell_second_level = np.zeros(np.shape(cell_dim))
    # endregion

    # region [3] Calculate the filling of the second level
    else:   # Option second level activated --> Calculate number of cells
        # Allow a swapping only in x and y direction -> Same strategy as the small Overlap
        cell_layout = np.zeros((np.shape(cell_dim)[0], 6))
        cell_layout[:, 0:3] = cell_dim
        # Swap x and y directions
        cell_layout[:, 3:6] = np.column_stack((cell_dim[:, 1], cell_dim[:, 0], cell_dim[:, 2]))

        # Calculate the corresponding pack layouts
        pack_layout = np.zeros((np.shape(cell_dim)[0], 6))
        pack_layout[:, 0:3] = cell_layout[:, 0:3] * packfactor
        pack_layout[:, 3:6] = cell_layout[:, 3:6] * packfactor    # Swap x and y directions

        # Add to the pack dimensions the required dimensions for the battery cooling and the module housing
        pack_layout[:, 2] = pack_layout[:, 2] + batt_cooling + EZ_cell2module
        pack_layout[:, 5] = pack_layout[:, 5] + batt_cooling + EZ_cell2module

        # Calculate the number of cell fitting for each configuration in each direction
        num_cell_orig = np.floor(second_level_dim / pack_layout[:, 0:3])
        num_cell_rot = np.floor(second_level_dim / pack_layout[:, 3:6])
        num_cell_second_level_layout = np.column_stack((num_cell_orig, num_cell_rot))

        # Calculate the total number of cell for each configuration
        num_total_orig = np.prod(num_cell_second_level_layout[:, 0:3], axis=1)
        num_total_rot = np.prod(num_cell_second_level_layout[:, 3:6], axis=1)
        num_cell_second_level_total = np.column_stack((num_total_orig, num_total_rot))

        # Find the column with the highest number of cells
        id_max = np.argmax(num_cell_second_level_total, axis=1)

        # Identify for every i_th cell, the rotation which has the highest integration potential and assign it as an output
        num_cell_second_level = np.zeros((len(id_max), 3))   # Preallocate the vector to speed up calculation
        cell_dim_second_level = np.zeros((len(id_max), 3))   # Preallocate the vector to speed up calculation
        pack_dim_second_level = np.zeros((len(id_max), 3))   # Preallocate the vector to speed up calculation

        for i in range(0, len(id_max)):
            idx = id_max[i]
            num_cell_second_level[i, :] = num_cell_second_level_layout[i, idx * 3:idx*3+3]
            cell_dim_second_level[i, :] = cell_layout[i, idx * 3:idx * 3 + 3]
            pack_dim_second_level[i, :] = pack_layout[i, idx * 3:idx * 3 + 3]
    # endregion

    return cell_dim_second_level, pack_dim_second_level, num_cell_second_level
