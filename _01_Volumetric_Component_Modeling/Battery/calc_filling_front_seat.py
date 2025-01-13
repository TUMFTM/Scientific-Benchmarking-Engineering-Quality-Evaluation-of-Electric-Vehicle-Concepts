"""
Description: This function fills the area under the front seat with battery cells. To fill this area,
             the cells which fit in the underbody area swapped in X and Y in their orientation to find the optimal configuration
             Computational method is the same as in the function calc_filling_second_level

             For more information look at Chapter 4.6 of (1) and (2)
------------
Sources: (1) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
         (2) Rosenberger et al., "Scientific benchmarking: Engineering quality evaluation of electric vehicle concepts", e-Prime - Advances in Electrical Engineering, Electronics and Energy 9, 2024
         (3) P. Köhler, „Semi-physikalische Modellierung von Antriebsstrangkomponenten für Elektrofahrzeuge,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       front_seat_dim: Dimensions of the available space for the area under the front seats
       cell_dim: Dimensions of the cells used in the underfloor of the simulated vehicle
       pack_dim: Dimensions of the cell pack used in the underfloor of the simulated vehicle (cell dimensions * packagefactor)
------------
Output: cell_dim_front_seat: Cell Dimensions that also fit under the front seat
        pack_dim_front_seat: Pack Dimensions that also fit under the front seat
        num_cell_front_seat: Number of cells that can be placed under the front seat
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Filling option is deactivated
[3] Calculate the filling of the area under the first seat row
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
import numpy as np
# endregion


def calc_filling_front_seat(vehicle, front_seat_dim, cell_dim, pack_dim):

    # region [1] Assign required Inputs
    check_filling = vehicle.settings.fill_frontseat_area

    batt_topology = vehicle.topology.battery_topology  # Lowfloor, mixedfloor or highfloor

    batt_cooling = vehicle.dimensions.CZ.batt_cooling    # Height of the cooling plate in mm (3, p. 76)

    # Difference in height (Z-direction) between cell and module in mm (3, p. 76)
    EZ_cell2module = vehicle.dimensions.EZ.cell2module

    # Get the packagefactor to recalculate the pack_dim for the front seat cell
    packfactor = vehicle.battery.cell.packagefactor
    # endregion

    # region [2] Filling option is deactivated
    # Option front seat is deactivated --> set number of cells to 0
    if check_filling == 0:

        if batt_topology.lower() != 'lowfloor':
            cell_dim_front_seat = np.zeros(np.shape(cell_dim))
            pack_dim_front_seat = np.zeros(np.shape(cell_dim))
            num_cell_front_seat = np.zeros(np.shape(cell_dim))
        else:
            cell_dim_front_seat = cell_dim
            pack_dim_front_seat = pack_dim
            num_cell_front_seat = np.zeros((np.shape(pack_dim_front_seat)[0], 3))
    # endregion

    # region [3] Calculate the filling of the area under the first seat row
    else:   # Option is activated --> Calculate filling
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
        num_cell_orig = np.floor(front_seat_dim / pack_layout[:, 0:3])
        num_cell_rot = np.floor(front_seat_dim / pack_layout[:, 3:6])
        num_cell_front_seat_layout = np.column_stack((num_cell_orig, num_cell_rot))

        # Calculate the total number of cell for each configuration
        num_total_orig = np.prod(num_cell_front_seat_layout[:, 0:3], axis=1)
        num_total_rot = np.prod(num_cell_front_seat_layout[:, 3:6], axis=1)
        num_cell_front_seat_total = np.column_stack((num_total_orig, num_total_rot))

        # Find the column with the highest number of cells
        id_max = np.argmax(num_cell_front_seat_total, axis=1)

        # Identify for every i_th cell, the rotation which has the highest integration potential and assign it as an output
        num_cell_front_seat = np.zeros((len(id_max), 3))   # Preallocate the vector to speed up calculation
        cell_dim_front_seat = np.zeros((len(id_max), 3))   # Preallocate the vector to speed up calculation
        pack_dim_front_seat = np.zeros((len(id_max), 3))   # Preallocate the vector to speed up calculation

        for i in range(0, len(id_max)):
            idx = id_max[i]
            num_cell_front_seat[i, :] = num_cell_front_seat_layout[i, idx * 3:idx*3+3]
            cell_dim_front_seat[i, :] = cell_layout[i, idx * 3:idx * 3 + 3]
            pack_dim_front_seat[i, :] = pack_layout[i, idx * 3:idx * 3 + 3]
    # endregion

    return cell_dim_front_seat, pack_dim_front_seat, num_cell_front_seat
