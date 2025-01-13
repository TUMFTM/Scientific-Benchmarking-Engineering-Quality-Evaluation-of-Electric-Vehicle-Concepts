"""
Description:    This function calculates the position on the longitudinal (X) direction of the first row of seats.
                ATTENTION: H30-1, L53-1 and so on are defined at the Design Point (SgRP)!!
                More information to this regard in the further sources and in [1]
------------
Sources:   (1) SAE J1100 - https://www.sae.org/standards/content/j1100_200911/
           (2) SAE J4004 - Positioning the H-Point Design Tool - Seating Reference Point and Seat Track Length, 2008.
           (3) E. Elagamy, "Creation of a Parametric Model for the Derivation of the Conceptual Dimensions for Battery Electric Vehicle", Master thesis, 2020
           (4) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Design", Ph.D. Thesis, 2022
------------
Input:   vehicle: Class element, which stores all the vehicle information
         parameters: Class element, which stores all necessary computation parameters
------------
Output:  Updated vehicle and parameter classes with the dimensions of the first seat row in x direction of the passenger compartment
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Assign Inputs
[2] Calculation of first seat row measures along the X direction
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
# Import classes
# Import methods
# endregion


def calc_passenger_compartment_x_first_seatrow(vehicle, parameters):
    # region [1]: Assign Inputs
    # These measures are described in (1)
    H30_1 = vehicle.manikin.H30_1                               # mm
    L113 = vehicle.dimensions.GX.L113                           # mm
    A46 = parameters.manikin.A46_1                              # deg
    Thigh_Length = parameters.manikin.thigh                     # mm
    Lower_Leg_length = parameters.manikin.lower_leg             # mm
    AHP_to_Ankle_Pivot = parameters.manikin.AHP_to_ankle_pivot  # mm
    BOF_to_AHP = parameters.manikin.AHP_to_BOF                  # mm
    Foot_height = parameters.manikin.foot_height                # mm
    A40_1 = parameters.manikin.A40_1                            # deg

    # Regressions
    L62H30_1 = parameters.regr.interior.L6fromH30_1             # Regression to estimate L6 from H30-1
    # endregion

    # region [2]: Calculation of first seat row measures along the X direction
    # Calculation of A47 (according to (2) p. 11) in degrees
    A47 = 2.522e-7 * math.pow(H30_1, 3) - 3.961e-4 * math.pow(H30_1, 2) + 4.644e-2 * H30_1 + 73.374

    # Calculate the inclination angle between calf center line and ground
    calf_angle = 180 - (A46 + A47 - 6.5)     # 6.5 deg is the difference between the bare foot plane and the centerline of the undepressed accelerator pedal

    # Position of the ankle point with respect to AHP point
    AHP_to_ankle_point_X = math.cos(math.radians(180 - A47 - math.degrees(math.atan(Foot_height/AHP_to_Ankle_Pivot)))) * \
                           math.sqrt(math.pow(Foot_height, 2) + math.pow(AHP_to_Ankle_Pivot, 2))

    AHP_to_ankle_point_Z = math.sin(math.radians(180 - A47 - math.degrees(math.atan(Foot_height/AHP_to_Ankle_Pivot)))) * \
                           math.sqrt(math.pow(Foot_height, 2) + math.pow(AHP_to_Ankle_Pivot, 2))

    # Calculate with the manikin size and the given manikin dimensions the resulting thigh angle in deg
    thigh_angle = math.degrees(math.asin(-(H30_1 - Lower_Leg_length * math.sin(math.radians(calf_angle)) - AHP_to_ankle_point_Z)/Thigh_Length))

    # since the equations for the derivation of A47 and SgRPx are interrelated with the lower limbs dimensions available in the SAE standards, derivation
    # of the L99-1 based on the calf angle, thigh angle and the lower limbs dimensions is valid
    # With thigh angle and calf angle derive the A44 in deg (angle valid for the manikin at the design point)
    A44 = 180 - calf_angle - thigh_angle                            # in deg

    # Calculating L53 at the SgRP in mm
    L53_1 = AHP_to_ankle_point_X + Lower_Leg_length * math.cos(math.radians(calf_angle)) + \
            Thigh_Length * math.cos(math.radians(thigh_angle))      # [mm]

    # Calculation of L99_1 (according to [1])
    delta_X_BOF_AHP = BOF_to_AHP * math.cos(math.radians(A47))      # [mm]
    L99_1 = L53_1 + delta_X_BOF_AHP                                 # [mm]

    # Recalculate the position of the AHP and SGRP with respect to the front axle
    AHP_X_front_axle = L113 + delta_X_BOF_AHP
    SgRP_X_front_axle = AHP_X_front_axle + L53_1

    # Finally derive the L6, i.e. the distance between BOF and wheel steering center along X
    coefficients = L62H30_1.coefficients
    L6 = coefficients[0] + H30_1 * coefficients[1]                  # More information at (3)
    # endregion

    # region [3]: Assign Outputs
    # Assign the measures in X direction (all in mm)
    setattr(vehicle.manikin, 'L53_1', L53_1)    # L53-1 at the SGRP
    setattr(vehicle.manikin, 'L99_1', L99_1)    # L99-1 at the SGRP
    setattr(vehicle.manikin, 'L6', L6)

    # Assign the manikin angles in degrees
    setattr(vehicle.manikin, 'A47', A47)
    setattr(vehicle.manikin, 'A46_1', A46)
    setattr(vehicle.manikin, 'A44_1', A44)
    setattr(vehicle.manikin, 'thigh_angle', thigh_angle)
    setattr(vehicle.manikin, 'calf_angle', calf_angle)
    setattr(vehicle.manikin, 'A40_1',  A40_1)

    # Position of the reference points in mm
    setattr(vehicle.manikin, 'AHP_X_front_axle', AHP_X_front_axle)
    setattr(vehicle.manikin, 'BOF_X_front_axle', L113)
    setattr(vehicle.manikin, 'SgRP_X_front_axle', SgRP_X_front_axle)
    # endregion

    return vehicle, parameters
