"""
Description:  This function calculates the available battery space for lowfloor vehicles.
              Therefore for the predefined theoretical possible underfloor space only the part under the
              second seat row is considered to be filled with battery cells. For this calculation the already known
              width and height from the previous underfloor calculation will be used because it is assumed that these
              values are the same (same approach as in (2))
              If the space under the front seats is also filled with cells the available space there is
              computed with a similar approach. Because the same cell is used in the same vehicle the height of the
              cells under the first seat row is the same as for the cells under the second seat row

              For more information, see (1, p.52-57)
------------
Sources:  (1) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
          (2) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", P. D. Thesis, Technical University of Munich, Institute of Automotive Technology, 2022
          (3) P. Köhler, „Semi-physikalische Modellierung von Antriebsstrangkomponenten für Elektrofahrzeuge,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021
          (4) Rosenberger et al., "Scientific benchmarking: Engineering quality evaluation of electric vehicle concepts", e-Prime - Advances in Electrical Engineering, Electronics and Energy 9, 2024
------------
Input: vehicle: Class element, which stores all values of the vehicle
       parameters: Class element, which stores all necessary computation parameters
------------
Output: The dimensions of the available space in the second level
------------
Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Calculate available space in X dimensions under rear seats (3, p.64)
[3] Update the spacetable
[4] Calculate available space under the front seat row
[4.1] Assign specific Inputs
[4.2] Calculate space dimensions in X direction
[4.3] Calculate space dimensions in Y direction
[4.4] Calculate space dimensions in Z direction
[5] Assign Outputs
------------
"""

# region [0] import modules, classes and functions
# import modules
import numpy as np
import math
# import functions
# endregion


def calc_battery_space_dimensions_underfloor_lowfloor(vehicle, parameters):
    # region [1] Assign Inputs
    spacetable = vehicle.battery.spacetable

    # Retrieve underfloor dimensions and positions (all in mm)
    CX_underfloor = spacetable['underfloor']['CX']  # Possible length of the underfloor battery
    CY_underfloor = spacetable['underfloor']['CY']  # Width of the underfloor battery (without considering the sills, if present)
    CZ_underfloor = spacetable['underfloor']['CZ']  # Height of the underfloor battery (without considering cooling, lower and upper cover)
    EX_underfloor = spacetable['underfloor']['EX']  # Distance between underfloor battery and front axle
    EZ_underfloor = spacetable['underfloor']['EZ']  # Distance between underfloor battery and ground (the distance includes the bottom cover thickness)

    # Dimensions for the battery dimensional chains (2)
    EX_SgRP2 = vehicle.manikin.SgRP2_X_front_axle           # Distance between SgrP and front axle (in mm)
    EX_SL10_2 = parameters.manikin.SL10_2   # Longitudinal distance between SGRP2 and front edge of the passenger seat
    # endregion

    # region [2] Calculate available space in X dimensions under rear seats (3, p.64)
    # Calculate the distance between front axle and the rearest point of the underfloor battery (in X direction)
    EX_battery_rear = CX_underfloor + EX_underfloor

    # The under the rear seat row depends from the SgRP2
    CX_underfloor_lowfloor = EX_battery_rear - (EX_SgRP2 - EX_SL10_2)
    CX_underfloor_lowfloor = max(CX_underfloor_lowfloor, 0)

    # Minimum distance between underfloor space and front axle along X in mm
    EX_underfloor_lowfloor = EX_SgRP2 - EX_SL10_2
    # endregion

    # region [3] Update the spacetable
    spacetable_underfloor_lowfloor = np.array([CX_underfloor_lowfloor, CY_underfloor, CZ_underfloor,
                                               EX_underfloor_lowfloor, EZ_underfloor])
    spacetable['underfloor'] = spacetable_underfloor_lowfloor
    # endregion

    # region [4] Calculate available space under the front seat row
    # Check whether the the space under the front seats are filled with battery cell (1, p.52-57)
    if vehicle.settings.fill_frontseat_area == 1:
        # region [4.1] Assign specific Inputs
        # Measures of the manikin at front seat row
        EX_SgRP = vehicle.manikin.SgRP_X_front_axle     # Distance between SgRP-1 and front axle (in mm)
        H5_1 = vehicle.manikin.H5_1                     # Distance between SgRP-1 and ground (H5-1 in SAE J1100) in mm
        W20_1 = vehicle.manikin.W20_1                   # Distance between SgRP-1 and vehicle center in y-direction
        SW16_1 = vehicle.manikin.SW16_1                 # Seat width of the vehicle depending on its vehicle segment

        # Define parameters
        EZ_free_space_mod2cover = parameters.dimensions.EZ.free_space_module_to_top_cover   # Required free space between module top and battery top cover in mm
        EZ_SGRP1_batt = parameters.dimensions.EZ.SgRP2_battery  # Distance between SgRP and battery (assumed to be the same as for the second seat row)
        EX_SL10_1 = parameters.manikin.SL10_1               # Longitudinal distance between SGRP1 and front edge of the driver seat
        CZ_top_cover = parameters.dimensions.CZ.batt_top_cover      # Height of the top cover in mm (3, p. 76)
        EY_tunnel_batt = parameters.dimensions.EY.tunnel_battery    # Distance between tunnel wall and battery in Y direction
        # endregion

        # region [4.2] Calculate front seat space dimensions in X direction
        # It is assumed that the battery starts at the SgRP-1 to ensure enough space under the seat for the second seat row
        EX_battery_rear_front_seat = EX_SgRP

        # The length of the battery is assumed to be equal to the seat length SL10-1 (same assumption as for the second seat row)
        CX_front_seat = EX_SL10_1

        # Calc starting position of the battery
        EX_front_seat = EX_battery_rear_front_seat - CX_front_seat
        # endregion

        # region [4.3] Calculate front seat space dimensions in Y direction
        # Definition of the space under the seats (Assumption, that the width must be reduced under the seat with housing structures (EY_tunnel_batt)
        CY_under_seats = 2 * W20_1 + SW16_1 - 2 * EY_tunnel_batt

        # If the underfloor dimension is lower than the space under the seats the underfloor dimensions will be used
        CY_front_seat = min(CY_under_seats, CY_underfloor)
        # endregion

        # region [4.4] Calculate front seat space dimensions in Z direction
        # Assumption: Only one cell format is used in the battery
        CZ_front_seat = CZ_underfloor

        # Calculate the Z position of the second level in mm
        EZ_front_seat = EZ_underfloor

        # Check if the height of the SgRP-1 is affected by this level
        H5_1_min = EZ_front_seat + CZ_front_seat + CZ_top_cover + EZ_free_space_mod2cover + EZ_SGRP1_batt

        if H5_1_min > H5_1:
            # The SgRP-1 has to be shifted upwards to enable the fitting of the cells in the second level
            H5_1 = H5_1_min

            # Define the new theoretically possibly H30-1 measure based on the SgRP1 and the FRP of the vehicle
            AHP_Z_front_axle = vehicle.manikin.AHP_Z_front_axle
            H30_1_theo = H5_1 - AHP_Z_front_axle

            # Recalculate the H61-1 measure (head clearance)
            AHP2interior_top = vehicle.dimensions.EZ.AHP2interior_top

            Z = AHP2interior_top - H30_1_theo
            H61_1 = Z/math.cos(math.radians(8))                     # in mm

            # Assign new calculate values
            setattr(vehicle.manikin, 'H5_1', H5_1)
            setattr(vehicle.manikin, 'H30_1_theo', H30_1_theo)
            setattr(vehicle.manikin, 'H61_1', H61_1)
        # endregion

    else:
        CX_front_seat = 0
        CY_front_seat = 0
        CZ_front_seat = 0
        EX_front_seat = 0
        EZ_front_seat = 0
    # endregion

    # region [5] Assign Output:
    # Store the dimensions of the second level
    secondlevel_front_spacetable = np.array([CX_front_seat, CY_front_seat, CZ_front_seat,
                                       EX_front_seat, EZ_front_seat])
    spacetable['front_seat'] = secondlevel_front_spacetable

    # Assign in the new spacetable
    setattr(vehicle.battery, 'spacetable', spacetable)
    # endregion

    return vehicle
