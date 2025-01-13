"""
Description:  This function calculates the available space for the second level for the battery
              The SECOND LEVEL is placed underneath the second row of seats and its
              dimensions are determined by the underbody battery and the dimensional concept
              More information to the battery model can be found in Chapters 3.4.5 of (1) and Chapter 4.5 of (3).

------------
Sources:  (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", P. D. Thesis, Technical University of Munich, Institute of Automotive Technology, 2022
          (2) P. Köhler, „Semi-physikalische Modellierung von Antriebsstrangkomponenten für Elektrofahrzeuge,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021
          (3) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
------------
Input: vehicle: Class element, which stores all values of the vehicle
       parameters: Class element, which stores all necessary computation parameters
------------
Output: The dimensions of the available space in the second level
------------
Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] X dimensions: calculate second level length (2, p. 64)
[3] Y dimension: Calculate second level width (3, p. 52-57)
[4] Z dimension: Calculate second level height
[5] Assign Outputs
------------
"""

# region [0] import modules, classes and functions
# import modules
import numpy as np
import math
# import functions
# endregion


def calc_battery_space_dimensions_secondrow(vehicle, parameters):

    spacetable = vehicle.battery.spacetable                 # Table which stores all the spaces

    if vehicle.settings.fill_second_level == 1:
        # region [1] Assign Inputs
        # Retrieve the available underfloor length and position
        # (The installationspace values are used because it might be possible that the spacetable was modified due to a lowfloor vehicle)
        CX_underfloor = vehicle.battery.installationspace.CX_batt_underfloor    # Possible length of the battery area
        EX_underfloor = vehicle.battery.installationspace.EX_batt_underfloor    # Possible start point of the battery area in X-irection

        # Retrieve underfloor dimensions and positions (all in mm: These dimensions are not affected by a lowfloor vehicle)
        CY_underfloor = spacetable['underfloor']['CY']  # Width of the underfloor battery (without considering the sills, if present)
        CZ_underfloor = spacetable['underfloor']['CZ']  # Height of the underfloor battery (without considering cooling, lower and upper cover)
        EZ_underfloor = spacetable['underfloor']['EZ']  # Distance between underfloor battery and ground (the distance includes the bottom cover thickness)

        # Dimensions for the battery dimensional chains (1, Section 3.4.5)
        EX_SgRP2 = vehicle.manikin.SgRP2_X_front_axle           # Distance between SgrP and front axle (in mm)

        # Required free space between module top and battery top cover in mm
        EZ_free_space_mod2cover = parameters.dimensions.EZ.free_space_module_to_top_cover
        EZ_SGRP2_batt = parameters.dimensions.EZ.SgRP2_battery  # Seems like this distance goes until the bottom of the seat, not the battery -> ESLAM here
        EX_SL10_2 = parameters.manikin.SL10_2   # Longitudinal distance between SGRP2 and front edge of the passenger seat
        H5_2 = vehicle.manikin.H5_2           # Distance between SgRP and ground (H5-2 according to SAE J1100) in mm
        CZ_top_cover = parameters.dimensions.CZ.batt_top_cover  # Height of the top cover in mm (2, p. 76)
        # endregion

        # region [2] X dimensions: calculate second level length (2, p. 64)
        # Calculate the distance between front axle and the rearest point of the underfloor battery (in X direction)
        EX_battery_rear = CX_underfloor + EX_underfloor

        # The SECOND LEVEL length depends from the SgRP2
        CX_second_level = EX_battery_rear - (EX_SgRP2 - EX_SL10_2)
        CX_second_level = max(CX_second_level, 0)   # Avoid negative CX value for the second level

        # Minimum distance between SECOND LEVEL and front axle along X in mm
        EX_second_level = EX_SgRP2-EX_SL10_2
        # endregion

        # region [3] Y dimension: Calculate second level width (3, p. 52-57)
        # Assumption: SECOND LEVEL width = UNDERFLOOR width
        CY_second_level = CY_underfloor
        # endregion

        # region [4] Z dimension: Calculate second level height
        # Calculate the Z position of the second level in mm (3 p.52-57)
        EZ_second_level = EZ_underfloor + CZ_underfloor + EZ_free_space_mod2cover

        # The same cell dimensions are used for the second level --> Therefore the dimensional chain in z-direction is the same
        CZ_second_level = CZ_underfloor

        # Check if the height of the SgRP-2 is affected by this level
        H5_2_min = EZ_second_level + CZ_second_level + CZ_top_cover + EZ_free_space_mod2cover + EZ_SGRP2_batt

        if H5_2_min > H5_2:
            # The SgRP-2 has to be shifted upwards to enable hte fitting of the cells in the second level
            H5_2 = H5_2_min

            # Define the new theoretically possibly H30-2 measure based on the SgRP2 and the FRP of the vehicle
            FRP_Z_front_axle = vehicle.manikin.FRP_Z_front_axle
            H30_2_theo = H5_2 - FRP_Z_front_axle

            # Recalculate the H61-2 measure (head clearance)
            interior2ground_2SR = vehicle.dimensions.EZ.interior2ground_2SR

            Z = interior2ground_2SR - H5_2
            H61_2 = Z/math.cos(math.radians(8))                     # in mm

            # Assign new calculate values
            setattr(vehicle.manikin, 'H5_2', H5_2)
            setattr(vehicle.manikin, 'H30_2_theo', H30_2_theo)
            setattr(vehicle.manikin, 'H61_2', H61_2)
        # endregion

    else:
        CX_second_level = 0
        CY_second_level = 0
        CZ_second_level = 0
        EX_second_level = 0
        EZ_second_level = 0

    # region [5] Assign Output:
    # Dimensions and position of the second level (in mm)
    CX_second_level = max(CX_second_level, 0)
    CY_second_level = max(CY_second_level, 0)
    CZ_second_level = max(CZ_second_level, 0)

    # Store the dimensions of the second level
    secondlevel_spacetable = np.array([CX_second_level, CY_second_level, CZ_second_level,
                                       EX_second_level, EZ_second_level])
    spacetable['second_level'] = secondlevel_spacetable
    setattr(vehicle.battery, 'spacetable', spacetable)
    # endregion

    return vehicle
