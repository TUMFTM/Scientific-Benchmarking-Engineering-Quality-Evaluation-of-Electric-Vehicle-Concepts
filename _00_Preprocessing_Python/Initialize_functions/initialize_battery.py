"""
Description:  This function initializes the battery cells. There are two different methods available.
              When the user decides to use the 'normal' calculation mode then the possible cell dimensions
              are selected from the entire dataset of battery cells. All the possible cell combination inside the
              given range for length and width are calculated. For the height of the cells the given cell height
              from the Excel sheet is used.
              In the other cases the entire cell dimensions (length, width, height) from the Excel are used.
------------
Sources: None
------------
Input: vehicle: Class element, which stores all values of the vehicle
       parameters: Class element, which stores all necessary computation parameters
------------
Output: All possible battery cell combinations (in usually two different ones)
------------
Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Calculate every possible (allowed) cell layout
[3] Initialize battery tables as Dataframe
[4] Error handling
[5] Assign outputs
"""

# region [0] import modules, classes and functions
# import modules
import numpy as np
import pandas as pd
# endregion


def initialize_battery(vehicle, parameters):
    # region [1] Assign Inputs
    cell_type = vehicle.Input.cell_type                 # pouch/prismatic/cylindrical
    cooling_in_Z = vehicle.settings.cooling_in_z        # 1: cooling in z direction, 0: no cooling in z direction
    cell_dim_Input = vehicle.Input.cell_dimension       # Cell dimensions defined in the Excel sheet

    # Check whether the cooling plate has to be considered for the Z-dimensional chain
    if cooling_in_Z == 1:  # Examples: Audi e-tron, Jaguar I-Pace, Mercedes EQC...
        CZ_batt_cooling = parameters.dimensions.CZ.batt_cooling.cooling_in_Z  # Battery cooling thickness in Z in mm
        CZ_batt_bottom_cover = parameters.dimensions.CZ.batt_bottom_cover.cooling_in_Z  # Battery bottom cover in mm
    else:  # Tesla Model 3 or vehicles with air cooling
        CZ_batt_cooling = parameters.dimensions.CZ.batt_cooling.no_cooling_in_Z  # Battery cooling thickness in Z in mm
        CZ_batt_bottom_cover = parameters.dimensions.CZ.batt_bottom_cover.no_cooling_in_Z  # Battery bottom cover in mm

    if cell_type.lower() == 'prismatic':
        EZ_cell2module = parameters.dimensions.EZ.offset_cell2module.prismatic
        packagefactor = parameters.battery.packagefactor.prismatic
        energy_density_vol = parameters.battery.cell_energy_density_vol.prismatic       # Wh/l
        energy_density_grav = parameters.battery.cell_energy_density_grav.prismatic     # Wh/kg

    elif cell_type.lower() == 'pouch':
        EZ_cell2module = parameters.dimensions.EZ.offset_cell2module.pouch
        packagefactor = parameters.battery.packagefactor.pouch
        energy_density_vol = parameters.battery.cell_energy_density_vol.pouch           # Wh/l
        energy_density_grav = parameters.battery.cell_energy_density_grav.pouch         # Wh/kg

    elif cell_type.lower() == 'cylindrical':
        EZ_cell2module = parameters.dimensions.EZ.offset_cell2module.cylindrical
        packagefactor = parameters.battery.packagefactor.cylindrical
        energy_density_vol = parameters.battery.cell_energy_density_vol.cylindrical     # Wh/l
        energy_density_grav = parameters.battery.cell_energy_density_grav.cylindrical   # Wh/kg

    else:
        raise Exception("The cell type is invalid. Only prismatic, cylindrical or pouch cells are possible")

    # Define the cell dimensions
    cell_dim_x = cell_dim_Input[0]         # Define array with cell dimension in x direction
    cell_dim_y = cell_dim_Input[1]         # Define array with cell dimension in y direction
    cell_dim_z = cell_dim_Input[2]         # Define array with cell dimension in z direction

    if cell_type.lower() == 'cylindrical':
        # X and Y dimensions are equal, since the section of the cell is a circle
        x, z = np.meshgrid(cell_dim_x, cell_dim_z, indexing='ij')
        cell_dim = np.row_stack((x.flatten(), x.flatten(), z.flatten())).transpose()
    else:
        # Pouch and prismatic cells
        x, y, z = np.meshgrid(cell_dim_x, cell_dim_y, cell_dim_z, indexing='ij')
        cell_dim = np.row_stack((x.flatten(), y.flatten(), z.flatten())).transpose()
    # endregion

    # region [2] Calculate every possible (allowed) cell layout
    # The only allowed rotational degree for the cells is the one along the vertical direction
    swap_width_length = 1   # 1: The cell may be rotated so, that its length and width are swapped; 0: This rotation is blocked
    swap_length_height = 0  # 1: The cell may be rotated so, that its length is parallel to the Z-direction; 0: This rotation is blocked
    swap_width_height = 0   # 1: The cell may be rotated so, that its width  is parallel to the Z-direction; 0: This rotation is blocked

    # Create the Permutation matrix: Required for rotating the cells!
    permmat_1 = np.array([[0, 1, 2], [1, 0, 2]])    # The cell is orientated so, that its height is placed parallel to the Z direction
    permmat_2 = np.array([[2, 1, 0], [1, 2, 0]])    # The cell is orientated so, that its length is placed parallel to the Z direction
    permmat_3 = np.array([[0, 2, 1], [2, 0, 1]])    # The cell is orientated so, that its width  is placed parallel to the Z direction
    permmat = np.row_stack((permmat_1, permmat_2, permmat_3))

    # Eliminate from the permutation matrix the rotations/swappings which are not allowed
    filter_permmat = np.array([[swap_width_length], [swap_width_length], [swap_length_height],
                              [swap_length_height], [swap_width_height], [swap_width_height]])

    remove_filter = np.asarray(np.where(filter_permmat == 0))
    if np.size(remove_filter) != 0:
        permmat = np.delete(permmat, remove_filter[0], 0)

    # Permute the cell based on the rotional degrees of freedom and calculate all possible cells layouts
    allcelldim = np.zeros((1, 3))
    for i in range(0, np.shape(cell_dim)[0]):
        orig_cell = np.array([cell_dim[i, 0], cell_dim[i, 1], cell_dim[i, 2]])   # Basis cell described as [Length, Width, Height]
        all_allowed_layouts = orig_cell[permmat]                              # Create the allowed rotations from the basis cells
        allcelldim = np.vstack((allcelldim, all_allowed_layouts))
    allcelldim = np.delete(allcelldim, 0, 0)

    # Remove duplicates (duplicates exist only if the x,y or z dimensions are in similar ranges)
    allcelldim = np.unique(allcelldim, axis=0)

    # Calculate the resulting package dimensions for each cell
    allpackdim = allcelldim * packagefactor

    # Add cooling plate and cell module housing height to the package factor in Z direction
    allpackdim[:, 2] = allpackdim[:, 2] + CZ_batt_cooling + EZ_cell2module

    # Compute the original cell height (is later necessary to determine the batteryspace in Z-direction)
    cell_z_original = np.max(cell_dim[:, 2]) + CZ_batt_cooling + EZ_cell2module
    # endregion

    # region [3] Initialize battery tables as Dataframe
    # Create the spacetable
    spacetable = pd.DataFrame(columns=['underfloor', 'small_overlap', 'second_level', 'front_seat', 'tunnel_1', 'tunnel_2'],
                              index=['CX', 'CY', 'CZ', 'EX', 'EZ'])
    filltable = pd.DataFrame(columns=['underfloor', 'small_overlap', 'second_level', 'front_seat', 'tunnel_1', 'tunnel_2'],
                             index=['NumCellX', 'NumCellY', 'NumCellZ', 'CellDimX', 'CellDimY', 'CellDimZ', 'PackDimX', 'PackDimY', 'PackDimZ'])

    for col in spacetable:
        spacetable[col] = np.zeros(5)
        filltable[col] = np.zeros(9)
    # endregion

    # region [4] Error handling
    # For some reasons, the cell dimensions may contain NaN. If that is the case,
    # the tool will enter an infinite loop. Avoid this by breaking the code here
    if np.any(np.isnan(allpackdim[:, 0])) or np.any(np.isnan(allpackdim[:, 1])) or np.any(np.isnan(allpackdim[:, 2])):
        text_error = 'UNEXPECTED ERROR: SOME OF THE POSSIBLE CELL DIMENSIONS HAVE NaN VALUES: PLEASE CHECK THE INITIALIZATION IN THE FUNCTION: initialize_battery'
        raise Exception(text_error)

    elif np.any(np.prod(allpackdim, axis=1) == 0):
        text_error = 'UNEXPECTED ERROR: SOME OF THE POSSIBLE CELL DIMENSIONS HAVE NULL VALUES: PLEASE CHECK THE INITIALIZATION IN THE FUNCTION: initialize_battery'
        raise Exception(text_error)

    # region [5] Assign outputs
    # Assign dimension parameters
    setattr(vehicle.dimensions.CZ, 'batt_cooling', CZ_batt_cooling)             # Thickness of the cooling plate (in mm) along the Z direction
    setattr(vehicle.dimensions.CZ, 'batt_bottom_cover', CZ_batt_bottom_cover)   # Thickness of the battery bottom cover (in mm) along the Z direction
    setattr(vehicle.dimensions.EZ, 'cell2module', EZ_cell2module)               # Difference in height (Z direction) between cell and module
    setattr(vehicle.dimensions.CZ, 'CZ_batt_underfloor', cell_z_original)  # Original height of the cell

    # Assign information about the cell
    setattr(vehicle.battery.cell, 'packagefactor', packagefactor)               # Packagefactor used for the calculation
    setattr(vehicle.battery.cell, 'allcelldim', allcelldim)                     # Cell dimensions of all the simulated cells
    setattr(vehicle.battery.cell, 'allpackdim', allpackdim)                     # Pack dimensions of all the simulated cells
    setattr(vehicle.battery.cell, 'energy_density_vol', energy_density_vol)     # Volumetric energy density at the cell level in Wh/l
    setattr(vehicle.battery.cell, 'energy_density_grav', energy_density_grav)   # Gravimetric energy density at the cell level in Wh/kg
    setattr(vehicle.battery.cell, 'cell_type', cell_type)                       # Type of cell (in this case always cylindrical

    # Assign the tables
    setattr(vehicle.battery, 'spacetable', spacetable)
    setattr(vehicle.battery, 'filltable', filltable)
    # endregion
    return vehicle
