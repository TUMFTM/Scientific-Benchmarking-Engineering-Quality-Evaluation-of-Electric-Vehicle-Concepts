"""
Description:  This function fills the previously calculated battery space with cells. This is done by calculate
              the number of cells for all the six different areas based on the integration principle of the
              vehicle. The result is the total number of cells, which can be placed inside the battery space

              For more information see Chapter 4.6 of (1), (2) and Chapter 3.4.6 of (3)
------------
Sources:  (1) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
          (2) Rosenberger et al., "Scientific benchmarking: Engineering quality evaluation of electric vehicle concepts", e-Prime - Advances in Electrical Engineering, Electronics and Energy 9, 2024
          (3) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", P. D. Thesis, Technical University of Munich, Institute of Automotive Technology, 2022
------------
Input: vehicle: Class element, which stores all values of the vehicle
       cell_dim: Dimensions of all possible cell combinations
       pack_dim: Dimensions of all possible pack combinations
------------
Output: dict_filling: Dictionary which stores for each area the number of cells and the cell and pack dimensions
        cell_dim: Calculated cell dimensions
        no_cells_geometric: Total number of cells which can be placed inside the battery installation space

------------
Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
2] Calculate the filling of each area
[3] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
# import modules
import numpy as np
# import functions
from .calc_filling_underfloor import calc_filling_underfloor
from .calc_filling_second_level import calc_filling_second_level
from .calc_filling_front_seat import calc_filling_front_seat
from .calc_filling_tunnel import calc_filling_tunnel
from .calc_filling_tunnel_lowfloor import calc_filling_tunnel_lowfloor
from .calc_filling_small_overlap import calc_filling_small_overlap
# endregion


def calc_filling(vehicle, cell_dim, pack_dim):
    # region [1] Assign Inputs
    topology = vehicle.topology.battery_topology    # Integration principle (highfloor, mixedfloor, lowfloor)
    Tspace = vehicle.battery.spacetable             # Table containing the previously calculated battery spaces

    # Retrieve the previously calculated battery spaces
    underbody_dim = Tspace['underfloor'].to_numpy()[0:3]        # Underbody area in all three dimensions in mm
    second_level_dim = Tspace['second_level'].to_numpy()[0:3]   # second level area in all three dimensions in mm
    tunnel_1_dim = Tspace['tunnel_1'].to_numpy()[0:3]           # first tunnel area in all three dimensions in mm
    tunnel_2_dim = Tspace['tunnel_2'].to_numpy()[0:3]           # second tunnel area in all three dimensions in mm
    sov_dim = Tspace['small_overlap'].to_numpy()[0:3]           # Small overlap area in all three dimensions in mm
    front_seat_dim = Tspace['front_seat'].to_numpy()[0:3]       # front seat area in all three dimensions in mm
    # endregion

    # region [2] Calculate the filling of each area
    # To fill the space it is required to distinguish between lowfloor and highfloor integration principles
    if topology.lower() == 'lowfloor':

        # Calculate the cells fitting in the underfloor (area under the rear seats
        cell_dim_underfloor, pack_dim_underfloor, num_cell_underfloor = calc_filling_underfloor(underbody_dim, cell_dim, pack_dim)

        # The cells not fitting in the underfloor have been filtered out. Use the "filtered" vector to fill the other spaces
        cell_dim = cell_dim_underfloor
        pack_dim = pack_dim_underfloor

        # Fill the second level under the rear seat row with cells
        cell_dim_second_level, pack_dim_second_level, num_cell_second_level = \
            calc_filling_second_level(vehicle, second_level_dim, cell_dim)

        # Fill the area under the front seat with cells
        cell_dim_front_seat, pack_dim_front_seat, num_cell_front_seat = \
            calc_filling_front_seat(vehicle, front_seat_dim, cell_dim, pack_dim)

        # Fill the two tunnel areas with cells
        cell_dim_tunnel, pack_dim_tunnel, num_cell_tunnel_1, num_cell_tunnel_2 = \
            calc_filling_tunnel_lowfloor(vehicle, tunnel_1_dim, tunnel_2_dim, cell_dim, pack_dim)

        # Set dimension of small overlap area to zero (not filled in lowfloor vehicles)
        cell_dim_sov = np.zeros((1, 3))
        pack_dim_sov = np.zeros((1, 3))
        num_cell_sov = np.zeros((1, 3))

        # Sum up the number of cells to derive the total amount of cells fitting
        no_cells_geometric = np.prod(num_cell_underfloor, axis=1) + np.prod(num_cell_second_level, axis=1) + \
                             np.prod(num_cell_tunnel_1, axis=1) + np.prod(num_cell_tunnel_2, axis=1) + \
                             np.prod(num_cell_front_seat, axis=1)

    else:   # A distinction between highfloor and mixedfloor is not required
        # Calculate the cells fitting in the underfloor
        cell_dim_underfloor, pack_dim_underfloor, num_cell_underfloor = calc_filling_underfloor(underbody_dim, cell_dim, pack_dim)

        # The cells not fitting in the underfloor have been filtered out. Use the "filtered" vector to fill the other spaces
        cell_dim = cell_dim_underfloor

        # Fill the small overlap (only if the option is activated)
        cell_dim_sov, pack_dim_sov, num_cell_sov = calc_filling_small_overlap(vehicle, sov_dim, cell_dim)

        # Fill the second level under the second seat row with cells
        cell_dim_second_level, pack_dim_second_level, num_cell_second_level = \
            calc_filling_second_level(vehicle, second_level_dim, cell_dim)

        # Fill the tunnel
        cell_dim_tunnel, pack_dim_tunnel, num_cell_tunnel_1 = calc_filling_tunnel(vehicle, tunnel_1_dim, cell_dim)
        num_cell_tunnel_2 = np.zeros(np.shape(num_cell_tunnel_1))

        # Set dimensions of front seat area to zero (can't be filled in high- or mixedfloor vehicles)
        cell_dim_front_seat = np.zeros((1, 3))
        pack_dim_front_seat = np.zeros((1, 3))
        num_cell_front_seat = np.zeros((1, 3))

        # Sum up the to derive the total amount of cells fitting
        no_cells_geometric = np.prod(num_cell_underfloor, axis=1) + np.prod(num_cell_second_level, axis=1) + \
                             np.prod(num_cell_tunnel_1, axis=1) + np.prod(num_cell_sov, axis=1)
    # endregion

    # region [3] Assign Outputs
    # For each area a dictionary is created to store the cell dimensions, the pack dimensions and the number of cells
    dict_underfloor = {'cell_dim': cell_dim_underfloor, 'pack_dim': pack_dim_underfloor,
                       'num_cell': num_cell_underfloor}
    dict_sov = {'cell_dim': cell_dim_sov, 'pack_dim': pack_dim_sov, 'num_cell': num_cell_sov}
    dict_second_level = {'cell_dim': cell_dim_second_level, 'pack_dim': pack_dim_second_level,
                       'num_cell': num_cell_second_level}
    dict_front_seat = {'cell_dim': cell_dim_front_seat, 'pack_dim': pack_dim_front_seat,
                       'num_cell': num_cell_front_seat}
    dict_tunnel_1 = {'cell_dim': cell_dim_tunnel, 'pack_dim': pack_dim_tunnel, 'num_cell': num_cell_tunnel_1}
    dict_tunnel_2 = {'cell_dim': cell_dim_tunnel, 'pack_dim': pack_dim_tunnel, 'num_cell': num_cell_tunnel_2}

    dict_filling = {'underfloor': dict_underfloor, 'small_overlap': dict_sov, 'second_level': dict_second_level,
                    'front_seat': dict_front_seat, 'tunnel_1': dict_tunnel_1, 'tunnel_2': dict_tunnel_2}
    # endregion

    return dict_filling, cell_dim, no_cells_geometric
