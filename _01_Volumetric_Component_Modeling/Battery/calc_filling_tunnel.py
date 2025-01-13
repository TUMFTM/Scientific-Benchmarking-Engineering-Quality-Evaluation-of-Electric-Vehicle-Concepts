"""
Description: This function fills the tunnel and calculates how many cell fits in total. This function only calls
             the tunnel filling of a highfloor vehicle (which means that the tunnel is not divided into two areas)
             To fill the tunnel the cells which fit in the underbody are swapped in each possible orientation
             to find the optimal configuration.
             More information to the battery model can be found in Chapters 3.4.6 of (1) and Chapter 4.6 of (3)
------------
Sources: (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", P. D. Thesis, Technical University of Munich, Institute of Automotive Technology, 2022
         (2) P. Köhler, „Semi-physikalische Modellierung von Antriebsstrangkomponenten für Elektrofahrzeuge,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021
         (3) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       tunnel_1_dim: Dimensions of the available space for the tunnel_1 segment
       cell_dim: Dimensions of the cells used in the underfloor of the vehicle
------------
Output: cell_dim_tunnel: Cell Dimensions that also fit in the tunnel
        pack_dim_tunnel: Pack Dimensions that also fit in the tunnel
        num_cell_tunnel: Number of cells that can be placed in the tunnel
------------

 Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Filling option is deactivated
[3] Calculate the filling of the tunnel
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
import numpy as np
# endregion


def calc_filling_tunnel(vehicle, tunnel_1_dim, cell_dim):
    # region [1] Assign Inputs
    cell_type = vehicle.battery.cell.cell_type          # pouch, cylindrical, prismatic

    # Assign the packagefactor
    packfactor = vehicle.battery.cell.packagefactor

    # Height of the cooling plate in mm  (2, p. 76)
    batt_cooling = vehicle.dimensions.CZ.batt_cooling

    # Difference in height (Z-direction) between cell and module in mm (2, p. 76)
    EZ_cell2module = vehicle.dimensions.EZ.cell2module
    # endregion

    # region [2] Filling option is deactivated
    if vehicle.settings.fill_tunnel == 0:   # option tunnel deactivated --> set number of cells to 0
        cell_dim_tunnel = np.zeros(np.shape(cell_dim))
        pack_dim_tunnel = np.zeros(np.shape(cell_dim))
        num_cell_tunnel = np.zeros(np.shape(cell_dim))

    # endregion

    # region [3] Calculate the filling of the tunnel
    else:   # option tunnel activated --> calculate number of cells

        if cell_type.lower() == 'cylindrical':

            # For cylindrical cells due to the symmetry of the cell there is no need to test all the swaps
            cell_layout = np.zeros((np.shape(cell_dim)[0], 9))
            cell_layout[:, 0:3] = cell_dim
            # Swap y and z directions
            cell_layout[:, 3:6] = np.column_stack((cell_dim[:, 0], cell_dim[:, 2], cell_dim[:, 1]))
            # Swap x and z directions
            cell_layout[:, 6:9] = np.column_stack((cell_dim[:, 2], cell_dim[:, 1], cell_dim[:, 0]))

            #  Calculate corresponding packlayouts
            pack_layout = np.zeros((np.shape(cell_dim)[0], 9))
            pack_layout[:, 0:3] = cell_layout[:, 0:3] * packfactor
            pack_layout[:, 3:6] = cell_layout[:, 3:6] * packfactor    # Swap y and z directions
            pack_layout[:, 6:9] = cell_layout[:, 6:9] * packfactor    # Swap y and z directions

            # Add the space in Z-direction required for the battery cooling
            pack_layout[:, 2] = pack_layout[:, 2] + batt_cooling + EZ_cell2module
            pack_layout[:, 5] = pack_layout[:, 5] + batt_cooling + EZ_cell2module
            pack_layout[:, 8] = pack_layout[:, 8] + batt_cooling + EZ_cell2module

            # Calculate the number of cell fitting for each configuration in each direction
            num_cell_orig = np.floor(tunnel_1_dim / pack_layout[:, 0:3])
            num_cell_rot_1 = np.floor(tunnel_1_dim / pack_layout[:, 3:6])
            num_cell_rot_2 = np.floor(tunnel_1_dim / pack_layout[:, 6:9])
            num_cell_tunnel_layout = np.column_stack((num_cell_orig, num_cell_rot_1, num_cell_rot_2))

            # Calculate the total number of cells for each configuration
            num_total_orig = np.prod(num_cell_tunnel_layout[:, 0:3], axis=1)
            num_total_rot_1 = np.prod(num_cell_tunnel_layout[:, 3:6], axis=1)
            num_total_rot_2 = np.prod(num_cell_tunnel_layout[:, 6:9], axis=1)
            num_cell_tunnel_total = np.column_stack((num_total_orig, num_total_rot_1, num_total_rot_2))

        elif cell_type.lower() == 'prismatic':

            # Rotate each cells in all direction -> the cells in the tunnel do not necessarily need to be positioned like the cells in the underbody
            cell_layout = np.zeros((np.shape(cell_dim)[0], 18))
            cell_layout[:, 0:3] = cell_dim
            cell_layout[:, 3:6] = np.column_stack((cell_dim[:, 0], cell_dim[:, 2], cell_dim[:, 1]))      # Swap y and z directions
            cell_layout[:, 6:9] = np.column_stack((cell_dim[:, 1], cell_dim[:, 0], cell_dim[:, 2]))      # Swap x and y directions
            cell_layout[:, 9:12] = np.column_stack((cell_dim[:, 1], cell_dim[:, 2], cell_dim[:, 0]))     # Multiple swapping
            cell_layout[:, 12:15] = np.column_stack((cell_dim[:, 2], cell_dim[:, 0], cell_dim[:, 1]))    # Multiple swapping
            cell_layout[:, 15:18] = np.column_stack((cell_dim[:, 2], cell_dim[:, 1], cell_dim[:, 0]))    # Multiple swapping

            # Calculate corresponding packlayouts
            pack_layout = np.zeros((np.shape(cell_dim)[0], 18))
            pack_layout[:, 0:3] = cell_dim * packfactor
            pack_layout[:, 3:6] = cell_layout[:, 3:6] * packfactor        # Swap y and z directions
            pack_layout[:, 6:9] = cell_layout[:, 6:9] * packfactor        # Swap y and z directions
            pack_layout[:, 9:12] = cell_layout[:, 9:12] * packfactor      # Swap y and z directions
            pack_layout[:, 12:15] = cell_layout[:, 12:15] * packfactor    # Swap y and z directions
            pack_layout[:, 15:18] = cell_layout[:, 15:18] * packfactor    # Swap y and z directions

            # Add the space required for the battery cooling along the z direction
            pack_layout[:, 2] = pack_layout[:, 2] + batt_cooling + EZ_cell2module
            pack_layout[:, 5] = pack_layout[:, 5] + batt_cooling + EZ_cell2module
            pack_layout[:, 8] = pack_layout[:, 8] + batt_cooling + EZ_cell2module
            pack_layout[:, 11] = pack_layout[:, 11] + batt_cooling + EZ_cell2module
            pack_layout[:, 14] = pack_layout[:, 14] + batt_cooling + EZ_cell2module
            pack_layout[:, 17] = pack_layout[:, 17] + batt_cooling + EZ_cell2module

            # Calculate the number of cell fitting for each orientation (expressed as triple x,y,z)
            num_cell_orig = np.floor(tunnel_1_dim / pack_layout[:, 0:3])
            num_cell_rot_1 = np.floor(tunnel_1_dim / pack_layout[:, 3:6])
            num_cell_rot_2 = np.floor(tunnel_1_dim / pack_layout[:, 6:9])
            num_cell_rot_3 = np.floor(tunnel_1_dim / pack_layout[:, 9:12])
            num_cell_rot_4 = np.floor(tunnel_1_dim / pack_layout[:, 12:15])
            num_cell_rot_5 = np.floor(tunnel_1_dim / pack_layout[:, 15:18])
            num_cell_tunnel_layout = np.column_stack((num_cell_orig, num_cell_rot_1, num_cell_rot_2,
                                                      num_cell_rot_3, num_cell_rot_4, num_cell_rot_5))

            # Calculate the total number of cells filling
            num_total_orig = np.prod(num_cell_tunnel_layout[:, 0:3], axis=1)
            num_total_rot_1 = np.prod(num_cell_tunnel_layout[:, 3:6], axis=1)
            num_total_rot_2 = np.prod(num_cell_tunnel_layout[:, 6:9], axis=1)
            num_total_rot_3 = np.prod(num_cell_tunnel_layout[:, 9:12], axis=1)
            num_total_rot_4 = np.prod(num_cell_tunnel_layout[:, 12:15], axis=1)
            num_total_rot_5 = np.prod(num_cell_tunnel_layout[:, 15:18], axis=1)
            num_cell_tunnel_total = np.column_stack((num_total_orig, num_total_rot_1, num_total_rot_2,
                                                     num_total_rot_3, num_total_rot_4, num_total_rot_5))

        elif cell_type.lower() == 'pouch':

            # Rotate each cells in all direction -> the cells in the tunnel do not necessarily need to be positioned like the cells in the underbody
            cell_layout = np.zeros((np.shape(cell_dim)[0], 6))
            cell_layout[:, 0:3] = cell_dim
            # Swap x and y directions
            cell_layout[:, 3:6] = np.column_stack((cell_dim[:, 1], cell_dim[:, 0], cell_dim[:, 2]))

            # Calculate corresponding packlayouts
            pack_layout = np.zeros((np.shape(cell_dim)[0], 6))
            pack_layout[:, 0:3] = cell_dim * packfactor
            pack_layout[:, 3:6] = cell_layout[:, 3:6] * packfactor    # Swap y and z directions

            # Add the space required for the battery cooling along the z direction
            pack_layout[:, 2] = pack_layout[:, 2] + batt_cooling + EZ_cell2module
            pack_layout[:, 5] = pack_layout[:, 5] + batt_cooling + EZ_cell2module

            # Calculate the number of cell fitting for each orientation (expressed as triple x,y,z)
            num_cell_orig = np.floor(tunnel_1_dim / pack_layout[:, 0:3])
            num_cell_rot_1 = np.floor(tunnel_1_dim / pack_layout[:, 3:6])
            num_cell_tunnel_layout = np.column_stack((num_cell_orig, num_cell_rot_1))

            # Calculate the total number of cells filling
            num_total_orig = np.prod(num_cell_tunnel_layout[:, 0:3], axis=1)
            num_total_rot_1 = np.prod(num_cell_tunnel_layout[:, 3:6], axis=1)
            num_cell_tunnel_total = np.column_stack((num_total_orig, num_total_rot_1))
        else:
            raise Exception("The cell type is not correctly assign. Only cylindrical, pouch and prismatic is allowed")

        # Find the column with the highest number of cells
        id_max = np.argmax(num_cell_tunnel_total, axis=1)

        # Identify for every i_th cell, the rotation which has the highest integration potential and assign it as an output
        num_cell_tunnel = np.zeros((len(id_max), 3))    # Preallocate the vector to speed up calculation
        cell_dim_tunnel = np.zeros((len(id_max), 3))    # Preallocate the vector to speed up calculation
        pack_dim_tunnel = np.zeros((len(id_max), 3))    # Preallocate the vector to speed up calculation

        for i in range(0, len(id_max)):
            idx = id_max[i]
            num_cell_tunnel[i, :] = num_cell_tunnel_layout[i, idx * 3: idx * 3 + 3]
            cell_dim_tunnel[i, :] = cell_layout[i, idx * 3: idx * 3 + 3]
            pack_dim_tunnel[i, :] = pack_layout[i, idx * 3: idx * 3 + 3]
    # endregion

    return cell_dim_tunnel, pack_dim_tunnel, num_cell_tunnel
