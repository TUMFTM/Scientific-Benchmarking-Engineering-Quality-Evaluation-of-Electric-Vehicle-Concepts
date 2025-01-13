"""
Description: In the small overlap area, the same cells as the underfloor has to be
             used. Nevertheless, the cells can be swapped with respect to the underfloor.
             More information to the battery model can be found in Chapters 3.4.6 of (1)
------------
Sources: (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", P. D. Thesis, Technical University of Munich, Institute of Automotive Technology, 2022
         (2) P. Köhler, „Semi-physikalische Modellierung von Antriebsstrangkomponenten für Elektrofahrzeuge,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021
         (3) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       small_overlap: Dimensions of the available space for the small overlap
       cell_dim: Dimensions of the cells used in the underfloor of the vehicle
------------
Output: cell_dim_sov: Cell Dimensions that also fit in the small overlap area
        pack_dim_sov: Pack Dimensions that also fit in the small overlap area
        num_cell_sov: Number of cells that can be placed in the small overlap area
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Option not activated
[3] Calc small overlap filling
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
import numpy as np
# endregion


def calc_filling_small_overlap(vehicle, small_overlap, cell_dim):
    # region [1] Assign Inputs
    batt_cooling = vehicle.dimensions.CZ.batt_cooling      # Height of the cooling plate in mm (2, p. 76)

    # Difference in height (Z-direction) between cell and module in mm (2, p. 76)
    EZ_cell2module = vehicle.dimensions.EZ.cell2module
    # endregion

    # region [2] Option not activated
    # Option small overlap deactivated --> set number of cells to 0
    if vehicle.settings.fill_smalloverlapspace == 0:

        cell_dim_sov = np.zeros(np.shape(cell_dim))
        pack_dim_sov = np.zeros(np.shape(cell_dim))
        num_cell_sov = np.zeros(np.shape(cell_dim))
    # endregion

    # region [3] Calculate small overlap filling
    else:   # option small overlap activated --> calculate number of cells
        # Initialize the variables (this increases the calculation speed)
        pack_layout = np.zeros((np.shape(cell_dim)[0], 6))
        cell_layout = np.zeros((np.shape(cell_dim)[0], 6))

        # In the small overlap, the cells can be swapped with respect to the underfloor
        cell_layout[:, 0:3] = cell_dim  # The first 3 rows of cell_layout contain the cell_layout of the underbody
        # The last 3 rows of cell_layout contain the cell layout like the underbody with swapped x and y dimensions
        cell_layout[:, 3:6] = np.column_stack((cell_dim[:, 1], cell_dim[:, 0], cell_dim[:, 2]))

        # Calculate the corresponding pack layout
        packfactor = vehicle.battery.cell.packagefactor
        pack_layout[:, 0:3] = cell_layout[:, 0:3] * packfactor      # The first 3 rows of pack_layout contain the pack_layout of the underbody
        pack_layout[:, 3:6] = cell_layout[:, 3:6] * packfactor      # The last 3 rows of pack_layout contain the pack layout like the underbody with swapped x and y dimensions

        # Add to the pack dimensions the required dimensions for the battery cooling
        pack_layout[:, 2] = pack_layout[:, 2] + batt_cooling + EZ_cell2module
        pack_layout[:, 5] = pack_layout[:, 5] + batt_cooling + EZ_cell2module

        # Calculate the resulting number of cells
        num_cell_orig = np.floor(small_overlap/pack_layout[:, 0:3])
        num_cell_rot = np.floor(small_overlap/pack_layout[:, 3:6])
        num_cell_small_overlap_layout = np.column_stack((num_cell_orig, num_cell_rot))

        # Calculate total number of cells
        # -> First column: How many cells fit using the orientation of the underfloor
        # -> Second column: How many cells fit swapping the orientation (swapping x and y)
        num_total_orig = np.prod(num_cell_small_overlap_layout[:, 0:3], axis=1)
        num_total_rot = np.prod(num_cell_small_overlap_layout[:, 3:6], axis=1)
        num_cell_small_overlap_total = np.column_stack((num_total_orig, num_total_rot))

        # Find the column with the highest number of cells
        id_max = np.argmax(num_cell_small_overlap_total, axis=1)

        # Identify for every i_th cell, the rotation which has the highest integration potential and assign it as output
        num_cell_sov = np.zeros((len(id_max), 3))    # Preallocate the vector to speed up calculation
        cell_dim_sov = np.zeros((len(id_max), 3))    # Preallocate the vector to speed up calculation
        pack_dim_sov = np.zeros((len(id_max), 3))    # Preallocate the vector to speed up calculation

        for i in range(0, len(id_max)):

            idx = id_max[i]
            num_cell_sov[i, :] = num_cell_small_overlap_layout[i, idx * 3:idx * 3 + 3]
            cell_dim_sov[i, :] = cell_layout[i, idx * 3:idx * 3 + 3]
            pack_dim_sov[i, :] = pack_layout[i, idx * 3:idx * 3 + 3]

        if np.sum(np.prod(num_cell_sov, axis=1)) == 0:
            # Define errorlog
            errorlog_list = vehicle.errorlog
            text_errorlog = 'There is no cell fitting in the small overlap area: The option will be deactivated'
            print(text_errorlog)
            errorlog_list.append(text_errorlog)

            # Set cell dimensions to zero
            cell_dim_sov = np.zeros((np.shape(cell_dim)))
            pack_dim_sov = np.zeros((np.shape(cell_dim)))
            num_cell_sov = np.zeros((np.shape(cell_dim)))

            # deactivate option
            setattr(vehicle.settings, 'fill_smalloverlapspace', 0)
    # endregion

    return cell_dim_sov, pack_dim_sov, num_cell_sov
