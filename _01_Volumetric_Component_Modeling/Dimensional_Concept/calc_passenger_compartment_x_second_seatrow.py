"""
Description:    This function calculates the position on the longitudinal (X) direction of the second row of seats.
                For this scope, empirical correlations with the position of the 1st row and the dimensions of
                the wheelhouses are used.
------------
Sources:   (1) SAE J1100 - https://www.sae.org/standards/content/j1100_200911/
           (2) E. Elagamy, "Creation of a Parametric Model for the Derivation of the Conceptual Dimensions for Battery Electric Vehicle", Master Thesis, 2020
------------
Input:   vehicle: Class element, which stores all the vehicle information
         parameters: Class element, which stores all necessary computation parameters
------------
Output:  Updated vehicle and parameter classes with the dimensions of the second seat row in x direction of the passenger compartment
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Assign Inputs
[2] Calculation of passenger compartment in X direction
[3] Estimation of the limb angles using the previously calculated L53_2 and the input H30_2
[4] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
# Import classes
# Import methods
# endregion


def calc_passenger_compartment_x_second_seatrow(vehicle, parameters):
    # region [1]: Assign Inputs
    # Dimensional concept dimensions:
    L101 = vehicle.dimensions.GX.wheelbase          # Wheelbase (initial input) in mm
    L113 = vehicle.dimensions.GX.L113               # Distance between front wheel center point and BOF in mm (1)
    H30_2 = vehicle.manikin.H30_2                   # Distance between FRP and SgRP2 along the Z-direction in mm (1)
    L99_1 = vehicle.manikin.L99_1                   # Distance between BOF and SgRP in mm (1)
    L114 = vehicle.manikin.SgRP_X_front_axle        # Distance between front wheel center point and SgRP in mm (1)
    A40_2 = parameters.manikin.A40_2                # Torso angle of the second row of seats in deg (1)
    A47_2 = parameters.manikin.A47_2                # Angle of the foot of the second row of seats in deg (2)

    # For the calculation of the lower limbs angles of the rear mannequin -> These dimensions are defined in (1)
    Thigh_Length = parameters.manikin.thigh                     # in mm
    Lower_Leg_length = parameters.manikin.lower_leg             # in mm
    Foot_height = parameters.manikin.foot_height                # in mm
    AHP_to_Ankle_Pivot = parameters.manikin.AHP_to_ankle_pivot  # in mm

    # Retrieve the required regressions:
    RegrFRP = parameters.regr.interior.FRP2front_axle   # Regression between L114 and the SgRP2 position (2) pag 83
    RegrL115_2 = getattr(parameters.regr.interior.L115_2, vehicle.topology.frameform)
    # endregion

    # region [2]: Calculation of passenger compartment in X direction
    # Get the coefficients from the regression. L115_2 is computed via a regression between L101 and L113
    coefficients = RegrL115_2.coefficients
    L115_2 = coefficients[0] + coefficients[1] * L101 + coefficients[2] * L113      # in mm

    # Check if the L101 is in the given regression limits
    if L101 < RegrL115_2.Limits['Indep_var_1'][0] or L101 > RegrL115_2.Limits['Indep_var_1'][1]:
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The value of L101 required for the L115-2 is outside of the regression limits: ' \
                        'the calculated values will be extrapolated'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    # Check if the L113 is in the given regression limits
    if L113 < RegrL115_2.Limits['Indep_var_2'][0] or L113 > RegrL115_2.Limits['Indep_var_2'][1]:
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The value of L113 required for the L115-2 Regression is outside of the regression limits: ' \
                        'the calculated values will be extrapolated'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    # Calculate the L99_2 measure
    L99_2 = L101 - L115_2 - L113                  # in mm

    # Calculation of the FRP based on the analysis of the heel point
    # (result is a linear regression model dep. on SgRP X positioning)
    coefficients = RegrFRP.coefficients
    FRP_X_front_axle = coefficients[0] + coefficients[1] * L114       # in mm

    # Check if the L114 is in the given regression limits
    if L114 < RegrFRP.Limits['Indep_var_1'][0] or L114 > RegrFRP.Limits['Indep_var_1'][1]:
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The value of L114 required for the FRP Regression is outside of the regression limits: ' \
                        'the calculated values will be extrapolated'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    # Calculate L50-2 from the L99-1 and L99-2 in mm
    L50_2 = L99_2 - L99_1

    # Retrieve the position of the SgRP2 (in mm) using the previously calculated L115
    SgRP2_X_front_axle = L101 - L115_2

    # Calculation of the L53-2 acc. to the positioning of both the SgRP2 and the FRP
    L53_2 = SgRP2_X_front_axle - FRP_X_front_axle
    # endregion

    # region [3]: Estimation of the limb angles using the previously calculated L53_2 and the input H30_2
    # Calculation of the legroom and the lower limbs angles for the rear manikin
    FRP_to_ankle_point_X = math.cos(math.radians(180 - A47_2 - math.degrees(math.atan(Foot_height/AHP_to_Ankle_Pivot)))) * \
                           math.sqrt(math.pow(Foot_height, 2) + math.pow(AHP_to_Ankle_Pivot, 2))
    FRP_to_ankle_point_Z = math.sin(math.radians(180 - A47_2 - math.degrees(math.atan(Foot_height/AHP_to_Ankle_Pivot)))) * \
                           math.sqrt(math.pow(Foot_height, 2) + math.pow(AHP_to_Ankle_Pivot, 2))

    # Calculate the calf and thigh angles:
    x1 = L53_2 + abs(FRP_to_ankle_point_X)                          # Distance between ankle point and SgRP2 along X in mm
    x2 = H30_2 - FRP_to_ankle_point_Z                               # Distance between ankle point and SgRP2 along Z in mm
    L51_2 = math.sqrt(math.pow(x1, 2) + math.pow(x2, 2))   # L51_2 as defined in SAE J1100 in mm
    alpha_1 = math.degrees(math.asin(x2/L51_2))                     # Angle between L51_2 line and the horizontal in deg

    # Calculate calf angle using the Carnot Theorem and subsequently derive the thigh angle (all in deg)
    calf_angle_2 = math.degrees(math.acos((math.pow(Lower_Leg_length, 2) + math.pow(L51_2, 2) -
                                          math.pow(Thigh_Length, 2))/(2 * Lower_Leg_length * L51_2))) + alpha_1
    thigh_angle_2 = math.degrees(math.acos((x1 - Lower_Leg_length * math.cos(math.radians(calf_angle_2)))/Thigh_Length))

    # Derive A46_2 and A44_2
    A46_2 = 180 - calf_angle_2 - A47_2 + 6.5
    A44_2 = 180 - calf_angle_2 - thigh_angle_2

    # If the resulting A46_2 is higher than 130°, the limb angle need to be set according to the long coupling method
    if A46_2 > 130:
        A46_2 = 130
        calf_angle_2 = 180 - (A46_2 + A47_2 - 6.5)
        thigh_angle_2 = math.degrees(math.asin(-(H30_2 - Lower_Leg_length * math.sin(math.radians(calf_angle_2)) -
                                                 FRP_to_ankle_point_Z)/Thigh_Length))
        A44_2 = 180 - thigh_angle_2 - calf_angle_2
        L51_2 = math.sqrt(math.pow(Lower_Leg_length, 2) + math.pow(Thigh_Length, 2) - 2 * Lower_Leg_length *
                          Thigh_Length * math.cos(math.radians(A44_2)))
        L53_2 = Lower_Leg_length * math.cos(math.radians(calf_angle_2)) + \
                Thigh_Length * math.cos(math.radians(thigh_angle_2)) + FRP_to_ankle_point_X
        FRP_X_front_axle = SgRP2_X_front_axle - L53_2
    # endregion

    # region [4]: Assign Outputs
    # Manikin measurements
    setattr(vehicle.manikin, 'L50_2', L50_2)       # in mm
    setattr(vehicle.manikin, 'L99_2', L99_2)       # in mm
    setattr(vehicle.manikin, 'L53_2', L53_2)       # in mm
    setattr(vehicle.manikin, 'L115_2', L115_2)     # in mm
    setattr(vehicle.manikin, 'L51_2', L51_2)       # in mm

    # Manikin angles
    setattr(vehicle.manikin, 'A40_2', A40_2)                    # in deg
    setattr(vehicle.manikin, 'A47_2', A47_2)                    # in deg
    setattr(vehicle.manikin, 'calf_angle_2', calf_angle_2)      # in deg
    setattr(vehicle.manikin, 'thigh_angle_2', thigh_angle_2)    # in deg
    setattr(vehicle.manikin, 'A44_2', A44_2)                    # in deg

    # Position of the reference points with respect to the front axle (in mm)
    setattr(vehicle.manikin, 'FRP_X_front_axle', FRP_X_front_axle)
    setattr(vehicle.manikin, 'SgRP2_X_front_axle',  SgRP2_X_front_axle)
    # endregion

    return vehicle, parameters
