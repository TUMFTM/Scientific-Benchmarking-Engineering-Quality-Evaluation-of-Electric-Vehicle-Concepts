"""
Description:  This function calculates available tunnel space for vehicles with filled tunnel
              More information to the tunnel model in general can be found in Chapter 3.4.5 of (1)
              If the area under the front seat is filled with cells then the tunnel is divided into two parts.
              More information to this split can be found in Chapter 4.5 of (3)

------------
Sources:  (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", P. D. Thesis, Technical University of Munich, Institute of Automotive Technology, 2022
          (2) P. Köhler, „Semi-physikalische Modellierung von Antriebsstrangkomponenten für Elektrofahrzeuge,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021
          (3) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023

------------
Input: vehicle: Class element, which stores all values of the vehicle
       parameters: Class element, which stores all necessary computation parameters
------------
Output: The dimensions of the available space in the tunnel
------------
Implementation
[0] Import modules, classes and functions
[1] Initialize variable
[2] X dimensions: calc tunnel length
[3] Y direction: calc tunnel width
[4] Z direction: calc tunnel height
[5] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
# import modules
import numpy as np
import math
# import functions

# endregion


def calc_battery_space_dimensions_tunnel(vehicle, parameters):

    # Get the vehicles spacetable where the available spaces for the battery cells are stored
    spacetable = vehicle.battery.spacetable

    if vehicle.settings.fill_tunnel == 1:
        # region [1] Assign Inputs
        topology = vehicle.topology.battery_topology

        # Values describing the starting position of the tunnel
        CX_batt_underfloor = vehicle.battery.installationspace.CX_batt_underfloor   # Possible length of battery area
        EX_tunnel = vehicle.battery.installationspace.EX_batt_underfloor            # Position of battery area

        # Endpoint of the tunnel area
        if topology.lower() == 'lowfloor':
            CX_rear_seat = spacetable['underfloor']['CX']       # Length of battery area under the rear seats
        else:
            CX_rear_seat = spacetable['second_level']['CX']     # Length of second level area

        # Position and length of the area under the front seats
        CX_second_level_front = spacetable['front_seat']['CX']  # Length of area under front seats
        EX_second_level_front = spacetable['front_seat']['EX']  # Position of area under front seats

        # Assumption: The same buffer distance of the tunnel has also be guaranteed in X-Direction
        EX_tunnel_batt_space = parameters.dimensions.EY.tunnel_battery  # Distance between tunnel wall and battery in Y direction

        # Relevant values in Y-direction (all in mm) (1, section 3.4.5)
        W20_1 = vehicle.manikin.W20_1                               # Distance SgRP and vehicle center in mm
        SW16 = vehicle.manikin.SW16_1                               # Width of the front seat in mm
        EY_tunnel_batt = parameters.dimensions.EY.tunnel_battery    # Distance between tunnel wall and battery in Y direction

        # Relevant values in Z-direction (all in mm)
        CZ_underfloor = spacetable['underfloor']['CZ']  # Height of the underfloor battery (without considering cooling, lower and upper cover)
        EZ_underfloor = spacetable['underfloor']['EZ']  # Distance between the lowest surface of the underfloor battery and the ground (the distance includes the bottom cover and battery cooling thickness)

        H30_1 = vehicle.manikin.H30_1       # H30-1 at the SgRP-1 (the real value of the vehicle is used)
        H5_1 = vehicle.manikin.H5_1         # H5-1 at the SgRP-1 (the calculated value of the vehicle is used)
        tunnel_H30_ratio = parameters.battery.tunnel_factor    # Ratio between tunnel height and H30
        EZ_free_space_mod2cover = parameters.dimensions.EZ.free_space_module_to_top_cover   # Space between battery modules and top cover in mm (2, p. 76)
        EZ_tunnel_batt = parameters.dimensions.EZ.tunnel_battery  # Distance between tunnel wall and battery in Z direction
        # endregion

        # region [2] X dimensions: calc tunnel length
        # Start point of the first tunnel area
        EX_batt_tunnel_1 = EX_tunnel

        # Length of the battery tunnel (depending whether the area under the front seats is filled with cells) (3, p.57)
        if vehicle.settings.fill_frontseat_area == 1:  # Only appears in lowfloor vehicles
            # Length of the first tunnel area between battery start and first seat row
            # Buffer EX_tunnel_batt_space is assumed to be the same as in the Y-Direction
            CX_batt_tunnel_1 = EX_second_level_front - EX_tunnel - EX_tunnel_batt_space

            # Position of the start point of the second tunnel area
            EX_batt_tunnel_2 = EX_second_level_front + CX_second_level_front + EX_tunnel_batt_space

            # Calc length of the second tunnel area (subtract the already filled area under the rear seats
            CX_batt_tunnel_2 = EX_tunnel + CX_batt_underfloor - CX_rear_seat - EX_batt_tunnel_2
        else:
            # The tunnel runs across the entire length of the battery (no interruption by the first seat row)
            EX_batt_tunnel_2 = 0
            CX_batt_tunnel_2 = 0

            # Get length of the tunnel element
            if vehicle.settings.fill_second_level == 1:
                # Mixed- or Highfloor vehicle with a second level of cells
                CX_batt_tunnel_1 = CX_batt_underfloor - CX_rear_seat
            elif topology.lower() == 'lowfloor':
                # Lowfloor vehicle (area under rear set is already filled with cells)
                CX_batt_tunnel_1 = CX_batt_underfloor - CX_rear_seat
            else:
                # The tunnel can be placed along the entire battery length
                CX_batt_tunnel_1 = CX_batt_underfloor
        # endregion

        # region [3] Y direction: calc tunnel width
        # From the calculated W20 derive the tunnel width (for potential integration of battery modules/components)
        # For the derivation use the driver seat width (SW16), which is segment dependent
        # Note: tunnel width is the outer width of the tunnel including the trim
        CY_tunnel = 2 * (W20_1 - SW16/2)

        # Derive the installation space for the tunnel based on the W20_1 (in mm):
        CY_batt_tunnel = CY_tunnel - EY_tunnel_batt * 2

        # If the value is smaller than 0, then assign 0 to CY_batt_tunnel
        CY_batt_tunnel = max(CY_batt_tunnel, 0)
        # endregion

        # region [4] Z direction: calc tunnel height
        # Assumption: Only one type of cell dimensions is used in the vehicle therefore the height is the same
        # as in the underbody (3, p.52-57)
        CZ_batt_tunnel = CZ_underfloor

        # Lower position of the tunnel in Z direction
        if topology.lower() == 'lowfloor':
            # In Z-direction the tunnel use the space of the underfloor
            EZ_batt_tunnel = EZ_underfloor

        else:
            # In a mixed or highfloor case the tunnel is placed above the underbody
            EZ_batt_tunnel = EZ_underfloor + CZ_batt_tunnel + EZ_free_space_mod2cover

        # Check if this cell dimensions fit in the tunnel
        # Highest position of the tunnel in Z direction
        EZ_batt_tunnel_max = H5_1 - H30_1 * (1 - tunnel_H30_ratio) - EZ_tunnel_batt

        # Resulting battery height in the tunnel
        EZ_batt_tunnel_highest_point = EZ_batt_tunnel + CZ_batt_tunnel + EZ_free_space_mod2cover

        # Check if the necessary space fot the tunnel in z direction is higher than the maximal available space
        # given by the seating position
        if EZ_batt_tunnel_highest_point > EZ_batt_tunnel_max:

            # Assign necessary Inputs for the new calculation of the passenger compartment
            AHP_Z_front_axle = vehicle.manikin.AHP_Z_front_axle
            AHP2interior_top = vehicle.dimensions.EZ.AHP2interior_top

            # Shift the SgRP upwards by lifting the H5-1 measure
            H5_1_recalc = EZ_batt_tunnel_highest_point + EZ_tunnel_batt + H30_1 * (1 - tunnel_H30_ratio)

            # Calculate the theoretically possible H30_1 measure
            H30_1_theo = H5_1_recalc - AHP_Z_front_axle

            # Effective headroom first seat row (H61_1, same computation as in calc_passenger_compartment_z)
            Z = AHP2interior_top - H30_1_theo
            H61_1 = Z / math.cos(math.radians(8))       # Estimated head clearance in mm

            # Assign the new Outputs
            setattr(vehicle.manikin, 'H5_1', H5_1_recalc)
            setattr(vehicle.manikin, 'H30_1_theo', H30_1_theo)
            setattr(vehicle.manikin, 'H61_1', H61_1)
        # endregion

    else:   # Set all tunnel dimensions to 0 if option is deactivated
        CX_batt_tunnel_1 = 0
        CX_batt_tunnel_2 = 0
        CY_batt_tunnel = 0
        CZ_batt_tunnel = 0
        EZ_batt_tunnel = 0
        EX_batt_tunnel_1 = 0
        EX_batt_tunnel_2 = 0

    # region [5] Assign Outputs
    # Ensure that the tunnel dimensions are not negative!
    CX_batt_tunnel_1 = max(CX_batt_tunnel_1, 0)
    CX_batt_tunnel_2 = max(CX_batt_tunnel_2, 0)
    CY_batt_tunnel = max(CY_batt_tunnel, 0)
    CZ_batt_tunnel = max(CZ_batt_tunnel, 0)

    # Store the tunnel dimensions
    tunnel_dimensions_1 = np.array([CX_batt_tunnel_1, CY_batt_tunnel, CZ_batt_tunnel,
                                  EX_batt_tunnel_1, EZ_batt_tunnel])
    tunnel_dimensions_2 = np.array([CX_batt_tunnel_2, CY_batt_tunnel, CZ_batt_tunnel,
                                    EX_batt_tunnel_2, EZ_batt_tunnel])
    spacetable['tunnel_1'] = tunnel_dimensions_1
    spacetable['tunnel_2'] = tunnel_dimensions_2

    setattr(vehicle.battery, 'spacetable', spacetable)
    # endregion

    return vehicle
