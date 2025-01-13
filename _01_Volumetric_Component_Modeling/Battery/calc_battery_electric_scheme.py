"""
Description:  This function fills the available battery space with cells such that the simulated vehicle
              has the same amount of cells. For this case all the different areas which can be filled (underfloor,
              second level, front seat, small overlap, tunnel 1 and tunnel 2) area computed separately.
              A target value is specified for each area based on the percentage of this area in the total
              installation space. With this target value the number of cells in x and y direction for each area
              can then be computed (depending on the cell format). Based on the number of cell in each direction
              the possible cell dimensions can be estimated.
              For more information see Chapter 4.6.3 of (1) and (2)

------------
Sources:  (1) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
          (2) Rosenberger et al., "Scientific benchmarking: Engineering quality evaluation of electric vehicle concepts", e-Prime - Advances in Electrical Engineering, Electronics and Energy 9, 2024
          (3) P. Köhler, „Semi-physikalische Modellierung von Antriebsstrangkomponenten für Elektrofahrzeuge,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021
------------
Input: vehicle: Class element, which stores all values of the vehicle
       parameters: Class element, which stores all necessary computation parameters
------------
Output: The resulting cell dimensions and the simulated battery capacity
------------
Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Calculate areas dimensions
[3] Create the dataframe
[4] Calculate the divisor
[5] Calculate the optimal cell dimensions
[6] Calculate the filling of the battery space
[7] Calculate battery capacity
[8] Assign Outputs
[9] Calculate the cell volume
[10] Assign filltable
------------
"""

# region [0] Import modules, classes and functions
# import modules
import numpy as np
import pandas as pd
import re
import math
# import functions
from .calc_cell_dimensions_cylindrical import calc_cell_dimensions_cylindrical
from .calc_cell_dimensions_prismatic_pouch import calc_cell_dimensions_prismatic_pouch
from .calc_filling import calc_filling
# endregion


def calc_battery_electric_scheme(vehicle, parameters):
    # region [1] Assign Inputs
    # Get cell specific inputs
    cell_type = vehicle.battery.cell.cell_type                              # Cell type: prismatic/pouch/cylindrical
    packagefactor = vehicle.battery.cell.packagefactor                      # Packagefactor in x and y direction
    energy_density_volumetric = vehicle.battery.cell.energy_density_vol     # Cell volumetric energy density in Wh/l
    cell_voltage = parameters.battery.cell_voltage                          # Nominal cell voltage

    # Get battery specific inputs
    topology = vehicle.topology.battery_topology            # Integration principle (lowfloor/highfloor/mixedfloor)
    net2gross = parameters.battery.net_to_gross_capacity_factor     # Conversion factor from net to gross capacity (-)
    network_str = vehicle.battery.electrical_interconnection        # Number of serial and parallel cells as string
    batt_cooling = vehicle.dimensions.CZ.batt_cooling               # Height of the cooling plate in mm (3, p. 76)
    EZ_cell2module = vehicle.dimensions.EZ.cell2module              # Difference in height (Z-direction) between cell and module in mm (3, p. 76)

    # Get the network of the battery (number of serial and parallel cells
    no_cells_serial = int(re.findall(r"[-+]?\d*\.\d+|\d+", network_str)[0])
    no_cells_parallel = int(re.findall(r"[-+]?\d*\.\d+|\d+", network_str)[1])
    no_cells_electric = no_cells_serial * no_cells_parallel

    # Assign the previously calculated battery spaces:
    Tspace = vehicle.battery.spacetable  # Table containing the previously calculated battery spaces
    Ftable = vehicle.battery.filltable  # Table containing the number of fitting cells for each space
    # endregion

    # region [2] Calculate areas dimensions
    # Retrieve the previously calculated battery spaces
    underbody_dim = Tspace['underfloor'].to_numpy()[0:3]        # Dimension of the underbody in all three directions
    second_level_dim = Tspace['second_level'].to_numpy()[0:3]   # Dimension of the second_level in all three directions
    tunnel_1_dim = Tspace['tunnel_1'].to_numpy()[0:3]           # Dimensions of the first tunnel segment
    tunnel_2_dim = Tspace['tunnel_2'].to_numpy()[0:3]           # Dimensions of the second tunnel segment
    sov_dim = Tspace['small_overlap'].to_numpy()[0:3]           # Dimensions of the small overlap area
    front_seat_dim = Tspace['front_seat'].to_numpy()[0:3]       # Dimensions of the area underneath the front seat

    # Calculate the area in mm^2 for each of the six areas
    area_underbody = np.prod(underbody_dim[0:2])
    area_second_level = np.prod(second_level_dim[0:2])
    area_tunnel_1 = np.prod(tunnel_1_dim[0:2])
    area_tunnel_2 = np.prod(tunnel_2_dim[0:2])
    area_sov = np.prod(sov_dim[0:2])
    area_front_seat = np.prod(front_seat_dim[0:2])

    # If the small overlap is not filled with cells its area has to be set to zero
    if vehicle.settings.fill_smalloverlapspace == 0:
        area_sov = 0

    # Create an array where the dimensions in x and y direction of the available areas is stored
    dim_all = np.column_stack((underbody_dim, second_level_dim, front_seat_dim, sov_dim, tunnel_1_dim, tunnel_2_dim))
    dim_all_x = dim_all[0, :]
    dim_all_y = dim_all[1, :]

    # Create an array where all the areas of the available battery spaces ares stored
    area_array = np.array([area_underbody, area_second_level, area_front_seat, area_sov, area_tunnel_1, area_tunnel_2])

    # Compute the total battery area
    area_total = np.sum(area_array)

    # Calculate the share of each area in the total area
    area_relative = area_array/area_total
    # endregion

    # region [3] Create the dataframe
    # Create index for each of the six available areas
    name_areas = ['underbody', 'second_level', 'front_seat', 'small_overlap', 'tunnel_1', 'tunnel_2']

    # Create the columns of the dataframe
    if cell_type.lower() == 'cylindrical':
        columns = ['dim_x', 'dim_y', 'area_total', 'area_relative', 'num_cell_area', 'ratio_total', 'num_x', 'num_y',
                   'diameter_x', 'diameter_y']
        initialize_array = np.zeros((6, 10))
    else:
        columns = ['dim_x', 'dim_y', 'area_total', 'area_relative', 'num_cell_area']
        initialize_array = np.zeros((6, 5))

    # Initialize the dataframe with zeros
    df_area = pd.DataFrame(initialize_array, index=name_areas, columns=columns)

    # Fill the dataframe with already known information
    df_area['dim_x'] = dim_all_x                    # Length of the available battery space (in x direction)
    df_area['dim_y'] = dim_all_y                    # Width of the available battery space (in y direction)
    df_area['area_total'] = area_array              # Area in mm^2 for each area
    df_area['area_relative'] = area_relative        # Percentual share of each area

    # Calculate the number of cells which shall be filled into each area
    num_cell_area = np.rint(no_cells_electric * area_relative)

    while True:
        # This loop avoids rounding errors and increases the number of cells in the underfloor until the number
        # of cells in all areas equal the total number of cells
        if np.sum(num_cell_area) >= no_cells_electric:
            break
        else:
            num_cell_area[0] = num_cell_area[0] + 1

    # Assign the number of cells for each area
    df_area['num_cell_area'] = num_cell_area
    # endregion

    # region [4] Calculate the divisor
    dict_divisor = dict()

    # Iterate over each of the six areas
    for area in name_areas:
        area_total = df_area.loc[area, 'area_total']
        # Check if the area shall be filled (only possible if the area is bigger than 0mm^2)
        if area_total != 0:

            # Find number of cells for the corresponding area
            cells_by_area = df_area.loc[area, 'num_cell_area']
            divisor = np.array([1, cells_by_area])

            # Calculate all divisors and save them in a matrix (e.g for 4 cells [[1, 8], [2,4]])
            for i in range(2, int(math.sqrt(cells_by_area)) + 1):
                check_divisor = cells_by_area % i
                if check_divisor == 0:
                    # Fill the array with both divisor numbers
                    new_array = np.array([i, cells_by_area/i])
                    divisor = np.row_stack((divisor, new_array))

            # Save the divisor matrix into an dictionary
            dict_divisor[area] = divisor
    # endregion

    # region [5] Calculate the optimal cell dimensions
    cell_dim_all = np.empty((0, 3))

    # Iterate over each area and append the optimal computed cell dimensions to the array cell_dim_all
    for area in name_areas:
        area_total = df_area.loc[area, 'area_total']

        # Check if the area needs to be filled
        if area_total != 0:
            if cell_type.lower() == 'cylindrical':
                # Calculate cell dimensions for cylindrical cells
                cell_dim_all, df_area = calc_cell_dimensions_cylindrical(vehicle, df_area, area, dict_divisor[area], cell_dim_all)
            else:
                # Extract the divisors
                divisor = dict_divisor[area]

                # Reshape the divisor into a onedimensional array (e.g. [1, 2, 4, 8]
                if np.size(divisor) != 2:
                    divisor = np.concatenate((divisor[:, 0], np.flipud(divisor[:, 1])))

                # Calculate the optimal cell dimensions for pouch and prismatic cells
                cell_dim_all, dict_divisor[area] = \
                    calc_cell_dimensions_prismatic_pouch(vehicle, parameters, df_area, area, cell_dim_all, divisor, no_cells_electric)

    # Calculate the dimensions of the cell pack
    pack_dim_all = cell_dim_all * packagefactor
    pack_dim_all[:, 2] = pack_dim_all[:, 2] + batt_cooling + EZ_cell2module
    # endregion

    # region [6] Calculate the filling of the battery space
    dict_filling, cell_dim, no_cells_geometric = calc_filling(vehicle, cell_dim_all, pack_dim_all)
    pack_dim = cell_dim * packagefactor
    pack_dim[:, 2] = pack_dim[:, 2] + EZ_cell2module + batt_cooling
    # endregion

    # region [7] Calculate battery capacity
    if np.sum(no_cells_electric) == 0:

        # It is not possible to reach a sufficient voltage. The battery cannot be used
        setattr(vehicle.battery, 'energy_is_gross_in_kWh', 0)  # Set battery energy to 0 kWh
        setattr(vehicle.battery, 'battery_voltage', 0)  # Set battery voltage to 0 V

        raise Exception('THE CHOSEN BATTERY VOLTAGE RANGE CANNOT BE REACHED: THEREFORE THE BATTERY CANNOT BE USED')

    # The number of cells which had to be estimated in order to reach an acceptable battery voltage
    lost_cells = no_cells_electric - no_cells_geometric

    # Calculate the battery voltage
    battery_voltage = no_cells_serial * cell_voltage

    # Calculate the cell volume (in l) and derive the cell and battery energy (Koehler, pp. 69)
    cell_volume = calc_cell_volume(cell_dim, cell_type)
    cell_energy = cell_volume * energy_density_volumetric
    battery_energy = no_cells_electric * cell_energy / 1000

    # Choose cell with the biggest resulting battery energy
    battery_energy_in_kWh = np.max(battery_energy, axis=0)
    index_max = np.argmax(battery_energy, axis=0)
    # endregion

    # region [8] Assign Outputs
    if topology.lower() != 'lowfloor':
        # noinspection PyUnboundLocalVariable
        small_overlap_filltable = assign_spacetable(dict_filling['small_overlap'], index_max)
        Ftable['small_overlap'] = small_overlap_filltable
    else:
        # Assign the cell fitting under the front seat row
        # noinspection PyUnboundLocalVariable
        filltable_front_seat = assign_spacetable(dict_filling['front_seat'], index_max)
        Ftable['front_seat'] = filltable_front_seat

    # Assign the cell fitting in the underfloor
    underfloor_filltable = assign_spacetable(dict_filling['underfloor'], index_max)

    # Assign the cell fitting in second level under the rear seat row
    filltable_second_level = assign_spacetable(dict_filling['second_level'], index_max)

    # Assign the cell fitting in the tunnel
    filltable_tunnel_1 = assign_spacetable(dict_filling['tunnel_1'], index_max)

    # Assign the cells fitting in the second part of the tunnel
    filltable_tunnel_2 = assign_spacetable(dict_filling['tunnel_2'], index_max)

    Ftable['underfloor'] = underfloor_filltable
    Ftable['second_level'] = filltable_second_level
    Ftable['tunnel_1'] = filltable_tunnel_1
    Ftable['tunnel_2'] = filltable_tunnel_2

    # Update the table storing the number of cells
    setattr(vehicle.battery, 'filltable', Ftable)

    # Store the dataframe
    setattr(vehicle.battery, 'filling_electric_scheme', df_area)
    setattr(vehicle.battery, 'electric_scheme_divisor', dict_divisor)

    # Update the dimensions of the cell
    setattr(vehicle.battery.cell, 'allcelldim', cell_dim)
    setattr(vehicle.battery.cell, 'allpackdim', pack_dim)

    # Save the resulting number of cells and the lost cells (if any) due to the electrical layout calculation
    setattr(vehicle.battery, 'num_of_cells', no_cells_electric)
    setattr(vehicle.battery, 'num_of_cells_serial', no_cells_serial)
    setattr(vehicle.battery, 'lost_cells', lost_cells[index_max])

    # Save the cell characteristics and dimensions
    setattr(vehicle.battery.cell, 'energy', cell_energy[index_max])  # Resulting energy of the cell in Wh
    setattr(vehicle.battery, 'energy_is_gross_in_kWh', battery_energy_in_kWh)  # The total energy of the battery in kWh (gross, i.e. not all this energy can be used)
    battery_energy_net_in_kWh = battery_energy_in_kWh * net2gross
    setattr(vehicle.battery, 'energy_is_net_in_kWh', battery_energy_net_in_kWh)  # The usable energy of the battery in kWh (net)
    setattr(vehicle.battery, 'battery_voltage', battery_voltage)  # Total battery_voltage in V
    # endregion

    return vehicle


# region [9] Calculate the cell volume
def calc_cell_volume(cell_dim, cell_type):
    """
    Description:  This function returns one vector containing the volume of every possible
                  cell combination, distinguishing between prismatic/pouch and cylindrical
                  cells for the volume calculation (3, p. 69).
    """
    if cell_type.lower() == 'cylindrical':

        # The cell height is the array value, which is different from the other two values
        pos_height_val = np.column_stack((cell_dim[:, [1]] - cell_dim[:, [2]], cell_dim[:, [0]] - cell_dim[:, [2]],
                                          cell_dim[:, [0]] - cell_dim[:, [1]]))
        pos_height = pos_height_val == 0
        cell_height = np.sum(cell_dim * pos_height, axis=1)

        # The cell diameter is the array value, which is equal to one of other two values
        pos_diameter = np.column_stack(
            (cell_dim[:, 0] == cell_dim[:, 1], cell_dim[:, 1] == cell_dim[:, 2], cell_dim[:, 2] == cell_dim[:, 0]))
        cell_diameter = np.sum(cell_dim * pos_diameter, axis=1)

        # Cell volume in liter
        cell_volume = np.power(cell_diameter / 2, 2) * math.pi * cell_height / math.pow(10, 6)

    else:
        # Cell volume in liter
        cell_volume = cell_dim[:, 0] * cell_dim[:, 1] * cell_dim[:, 2] / math.pow(10, 6)

    return cell_volume
# endregion


# region [10] Assign filltable
def assign_spacetable(fill_information, index_max):
    """
    Description:    This function assigns the cell dimensions into the spacetable
    """
    num_cell = fill_information['num_cell']
    cell_dim = fill_information['cell_dim']
    pack_dim = fill_information['pack_dim']
    # Function to create the spacetable array for all dimensions
    try:
        num_cell = np.array([num_cell[index_max, 0], num_cell[index_max, 1], num_cell[index_max, 2]])
    except IndexError:
        num_cell = np.zeros((1, 3))

    try:
        cell_dim = np.array([cell_dim[index_max, 0], cell_dim[index_max, 1], cell_dim[index_max, 2]])
    except IndexError:
        cell_dim = np.zeros((1, 3))

    try:
        pack_dim = np.array([pack_dim[index_max, 0], pack_dim[index_max, 1], pack_dim[index_max, 2]])
    except IndexError:
        pack_dim = np.zeros((1, 3))

    spacetable_array = np.concatenate((num_cell, cell_dim, pack_dim))

    return spacetable_array
# endregion
