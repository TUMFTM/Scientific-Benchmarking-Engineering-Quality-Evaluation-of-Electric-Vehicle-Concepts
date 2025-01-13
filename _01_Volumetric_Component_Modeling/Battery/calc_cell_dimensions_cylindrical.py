"""
Description:  This function calculates the optimal diameter of cylindrical cells for the filling.
              The function is executed for each of the six areas, which can be filled with battery cells,
              presupposed that the filling of the certain area is activated.
              The necessary cell number for the area will be split into cells in x and y direction.

              For more information see Chapter 4.6.3 in (1) and (2)

------------
Sources:  (1) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
          (2) Rosenberger et al., "Scientific benchmarking: Engineering quality evaluation of electric vehicle concepts", e-Prime - Advances in Electrical Engineering, Electronics and Energy 9, 2024
------------
Input: vehicle: Class element, which stores all values of the vehicle
       df_area: Dataframe, which stores all values necessary for the computation of optimal cell utilization
       area: Specifies, which area of the battery space is considered (underfloor, second level, front seat,
                                                                       small overlap, tunnel 1, tunnel 2)
       divisor: Array, where all possible divisors of the total cell number are stored
       cell_dim_all: Array, where all already computed possible cell combinations are stored
------------
Output: cell_dim_all: Updated cell dimension array which stores all possible cell dimensions
        df_area: Updated Dataframe with the number of cells in x and y direction and the diameter
------------
Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Calculate packagefactor and dimensional ratios
[3] Check divisor ratio
[4] Calculate number of cells and diameter in x and y direction
[5] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
# import modules
import numpy as np
import math
# import functions
# endregion


def calc_cell_dimensions_cylindrical(vehicle, df_area, area, divisor, cell_dim_all):
    # region [1] Assign Inputs
    # Assign Inputs from the dataframe (here are dimensions and cell numbers for each area stored)
    battery_space_in_x = df_area.loc[area, 'dim_x']
    battery_space_in_y = df_area.loc[area, 'dim_y']
    cells_by_area = df_area.loc[area, 'num_cell_area']

    # Assign vehicle inputs
    packagefactor = vehicle.battery.cell.packagefactor
    cell_height = vehicle.battery.cell.allcelldim[0, 2]
    # endregion

    # region [2] Calculate packagefactor and dimensional ratios
    # The general idea is that the cell number in x and y are depend from the ratios between the available space
    # dimensions and the ratio of the packagefactor

    # The ratio between the two dimensions (x and y) of the packagefactor
    ratio_package = packagefactor[0]/packagefactor[1]

    # Total ratio between x and y dimensions
    ratio_total = battery_space_in_x/battery_space_in_y/ratio_package

    # Calculate the ratio of the available divisors
    if np.size(divisor) != 2:
        ratio_divisor = divisor[:, 1] / divisor[:, 0]
    else:
        ratio_divisor = divisor[1]/divisor[0]
    # endregion

    # region [3] Check divisor ratio
    # Check where the ratio of the divisors is smaller than the total ratio
    check_divisor = np.argwhere(ratio_divisor < ratio_total)
    if len(check_divisor) >= 1:
        # This means that the exact number of cells can be placed inside the battery space)
        nums = divisor[check_divisor[0], :]
    else:
        # The exact amount of cells can't be placed inside the available space. Therefore a combination of cells in
        # x and y direction have to determined where the total ratio of the available space dimensions is equal
        # (rounding errors included) to the ratio of cells in x and y direction
        num_max = np.ceil(math.sqrt(cells_by_area * ratio_total))       # Calculate number of cells in first dimension
        num_min = np.floor(num_max/ratio_total)                         # Calculate number of cells in second dimension

        # Check if the product of cell numbers equals the necessary cell numbers
        if num_max * num_min < cells_by_area:
            num_min = num_min + 1

        nums = np.array([num_max, num_min])
    # endregion

    # region [4] Calculate number of cells and diameter in x and y direction
    # Assign cell numbers in x and y direction
    if battery_space_in_x > battery_space_in_y:
        num_x = np.max(nums)
        num_y = np.min(nums)
    else:
        num_y = np.max(nums)
        num_x = np.min(nums)

    # Calc total length which can be filled (depends on the packagefactor)
    length_cells_x = battery_space_in_x/packagefactor[0]
    length_cells_y = battery_space_in_y/packagefactor[1]

    # Calculate the possible cell diameter in both directions
    diameter_x = length_cells_x/num_x
    diameter_y = length_cells_y/num_y

    # The possible diameter is the minimum of the computed diameters
    diameter = min(diameter_x, diameter_y)

    # This is necessary to avoid calculation errors during the filling calculation. There are cases where
    # the recalculation of cell numbers in the calc_filling scripts lead into a number close to computed values
    # from this function (e.g. 69.999999 instead of 70) and because of rounding down a entire line of cells
    # might be missing)
    diameter = diameter - math.pow(10, -8)

    # Build the cell dimension array for all three dimensions
    cell_dim = np.array([diameter, diameter, cell_height])
    # endregion

    # region [5] Assign Outputs
    # Update the df_area Dataframe
    df_area.loc[area, 'num_x'] = num_x                  # Number of cells in x direction
    df_area.loc[area, 'num_y'] = num_y                  # Number of cells in y direction
    df_area.loc[area, 'ratio_total'] = ratio_total      # Total ratio between x and y direction
    df_area.loc[area, 'diameter_x'] = diameter_x        # Possible cell diameter in x direction
    df_area.loc[area, 'diameter_y'] = diameter_y        # Possible cell diameter in y direction

    # Update the array where all possible cell diameters are stored
    cell_dim_all = np.row_stack((cell_dim_all, cell_dim))
    # endregion

    return cell_dim_all, df_area
