"""
Description:  This function calculates the "optimal" cell dimensions for pouch and prismatic cells for a given area.
              Therefore for each cell type the range of the small cell side is given (based on the dimensions of
              real cells).
              As an input the number of cells of the area is given. Within the given dimension range all possible
              cell dimensions are calculated, such that the specific area is filled with the input number of cells.
              After that it is checked if the total number of cells is reached over all areas. If this is not the
              case, the necessarily number of cells for the corresponding area is iteratively increased.

              Cells could be placed in both possible rotations inside the area. The rotations are:
              Rotation 1: The small cell side is on the x axis       Rotation 2: The small cell side is on the y axis
              ------------------------                               -------------
              |                      |                               |           |
              |                      |                               |           |
              ------------------------                               |           |
                                                                     |           |
              ^X direction                                           |           |
              |                                                      |           |
              |                                                      |           |
              ----------> Y direction                                -------------

              For more information see Chapter 4.6.3 in (1) and (2)
------------
Sources:  (1) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
          (2) Rosenberger et al., "Scientific benchmarking: Engineering quality evaluation of electric vehicle concepts", e-Prime - Advances in Electrical Engineering, Electronics and Energy 9, 2024
------------
Input: vehicle: Class element, which stores all values of the vehicle
       parameters: Class element, which stores all necessary computation parameters
       df_area: Dataframe, which stores all values necessary for the computation of optimal cell utilization
       dimensions_area: Dictionary which stores the dimensions of all possible areas
       area: Specifies, which area of the battery space is considered (underfloor, second level, front seat,
                                                                       small overlap, tunnel 1, tunnel 2)
       cell_dim_all: Array, where all already computed possible cell combinations are stored
       divisor: Array, where all possible divisors of the total cell number are stored
       no_cells_electric: Total number of cells placed inside the real vehicle
------------
Output: cell_dim_all: Updated cell dimensions array with all cell dimensions resulting in the exact number of cells as the real vehicle
        divisor: Updated divisor array
------------
Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Calc cell dimensions
[3] Calc filling of battery space
[4] Check loop condition
------------
"""

# region [0] Import modules, classes and functions
# import modules
import numpy as np
# import functions
from .calc_filling import calc_filling
# endregion


def calc_cell_dimensions_prismatic_pouch(vehicle, parameters, df_area, area, cells_dim_all,
                                         divisor, no_cells_electric):
    # region [1] Assign Inputs
    # Assign Inputs from the area dataframe
    num_cell_area = df_area.loc[area, 'num_cell_area']      # Number of cells in the corresponding area
    battery_space_in_x = df_area.loc[area, 'dim_x']         # Space of corresponding area in x direction in mm
    battery_space_in_y = df_area.loc[area, 'dim_y']         # Space of corresponding area in y direction in mm

    # Assign Inputs from vehicle struct
    cell_type = vehicle.battery.cell.cell_type              # Pouch or prismatic
    cell_dim_small_side = getattr(parameters.battery.cell.dimensions_y, cell_type)   # Range of smaller side dimension of cell
    cells_dim_max = np.array(cell_dim_small_side)
    packagefactor = vehicle.battery.cell.packagefactor          # Packagefactor of the corresponding cells
    cell_height = vehicle.battery.cell.allcelldim[0, 2]         # Height of the cell
    # endregion

    while True:
        # region [2] Calc cell dimensions
        # Calc space, which can be filled with cells
        size_pack = np.array([battery_space_in_x, battery_space_in_y]) / packagefactor[0:2]

        # Calc the number of cells possible in both directions considering the minimal and maximal cell dimensions
        num_theo_rot_1 = size_pack[0] / cells_dim_max   # Range of number of cells for first rotation in x direction
        num_theo_rot_2 = size_pack[1] / cells_dim_max   # Range of number of cells for second rotation in y direction

        # Find the possible divisor, which lay between the minimal and maximal number of cells
        idx_rot_1 = (divisor > num_theo_rot_1[1]) * (divisor < num_theo_rot_1[0])
        idx_rot_2 = (divisor > num_theo_rot_2[1]) * (divisor < num_theo_rot_2[0])

        # Calculate the number of cells in the first direction
        num_cell_rot_1_x = divisor[idx_rot_1]       # Possible number of cells in x direction for the first rotation
        num_cell_rot_2_y = divisor[idx_rot_2]       # Possible number of cells in y direction for the second rotation

        # Calculate the number of cells in the second direction
        num_cell_rot_1_y = num_cell_area / num_cell_rot_1_x     # Possible number of cells in y direction for the first rotation
        num_cell_rot_2_x = num_cell_area / num_cell_rot_2_y     # Possible number of cells in x direction for the second rotation

        # Calculate the possible cell dimensions for the first rotation
        dimensions_rot_1_x = size_pack[0] / num_cell_rot_1_x    # Cell dimensions in x direction
        dimensions_rot_1_y = size_pack[1] / num_cell_rot_1_y    # Cell dimensions in y direction
        if len(num_cell_rot_1_x) != 0:
            # Merge the corresponding x and y dimensions
            dimensions_rot_1 = np.array(list(zip(dimensions_rot_1_x, dimensions_rot_1_y)))
        else:
            dimensions_rot_1 = np.empty((0, 2))

        # Calculate the possible cell dimensions for the second rotation
        dimensions_rot_2_y = size_pack[1] / num_cell_rot_2_y    # Cell dimensions in y direction
        dimensions_rot_2_x = size_pack[0] / num_cell_rot_2_x    # Cell dimensions in x direction
        if len(num_cell_rot_2_y) != 0:
            # Merge the corresponding x and y dimensions
            dimensions_rot_2 = np.array(list(zip(dimensions_rot_2_x, dimensions_rot_2_y)))
        else:
            dimensions_rot_2 = np.empty((0, 2))

        # Concatenate all dimensions into one array
        dim = np.row_stack((dimensions_rot_1, dimensions_rot_2))

        # Expand the cell dimensions with the cell height
        height = np.ones((len(dim), 1)) * cell_height
        cell_dim_possible_all = np.column_stack((dim, height))

        # Calculate pack dimensions
        pack_dim_possible_all = cell_dim_possible_all * packagefactor
        # endregion

        # region [3] Calc filling of battery space
        dict_filling, cell_dim, no_cells_geometric = calc_filling(vehicle, cell_dim_possible_all, pack_dim_possible_all)
        # endregion

        # region [4] Check loop condition
        # Check if there is a combination where enough cells can be placed inside all areas
        if np.any(no_cells_geometric >= no_cells_electric):
            # Filter out all cell dimensions, which can't reached the number of electrical cells
            idx_num_cell = np.argwhere(no_cells_geometric >= no_cells_electric).reshape(-1)
            cells_dim_all = np.row_stack((cells_dim_all, cell_dim[idx_num_cell, :]))
            break
        else:
            # Increase the number of cells of the area and calculate the cell dimensions again
            num_cell_area = num_cell_area + 1

            # Adapt the divisor to the new number of cells
            divisor = np.array([1])
            for i in range(2, int(num_cell_area) + 1):
                check_divisor = num_cell_area % i
                if check_divisor == 0:
                    divisor = np.column_stack((divisor, i))
        # endregion

    return cells_dim_all, divisor
