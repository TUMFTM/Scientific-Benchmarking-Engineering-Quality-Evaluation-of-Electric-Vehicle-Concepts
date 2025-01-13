"""
Description:    This function calculates the widths (i.e., Y Dimensional Chain) of the passenger compartment
                and the resulting available room for a mid-vehicle tunnel.
------------
Sources:   (1) SAE J1100 - https://www.sae.org/standards/content/j1100_200911/
           (2) E. Elagamy, "Creation of a Parametric Model for the Derivation of the Conceptual Dimensions for Battery Electric Vehicle", Master thesis, 2020
           (3) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Design", Ph.D. Thesis, 2022
------------
Input:   vehicle: Class element, which stores all the vehicle information
         parameters: Class element, which stores all necessary computation parameters
------------
Output:  Updated vehicle and parameter classes with the dimensions in y direction of the passenger compartment
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Assign Inputs
[2] Select SW16-1
[3] Calculation of the passenger compartment in Y direction
[4] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
# Import classes
# Import methods
# endregion


def calc_passenger_compartment_y(vehicle, parameters):
    # region [1]: Assign Inputs
    # The majority of these measures are defined in (1)
    W103 = vehicle.dimensions.GY.vehicle_width                  # Vehicle width in mm
    L101 = vehicle.dimensions.GX.wheelbase                      # Vehicle wheelbase in mm
    L115_2 = vehicle.manikin.L115_2                             # rear axle CP to SgRP-2 in mm
    CX_wheelhouse = vehicle.dimensions.CX.wheelhouse_r_length   # Dimensions of the wheelhouse along X in mm

    # Distance between the rear wheelhouses in Y direction in mm; 29 mm is the trunk trim to wheelhouse edge thickness
    W201 = vehicle.dimensions.EY.wheelhouse_r_vehicle_center * 2 - 2 + 29

    manikin_width_elbow2elbow = parameters.manikin.manikinwidth  # Elbow to elbow width, see Chapter 3.4.5 of (3)
    RegrW31 = parameters.regr.interior.W31fromW103               # Regression to estimate the elbow room
    SW16_1 = parameters.manikin.SW16_1                           # Structure containing the SW16_1 for the different segments (this measure is defined in (1))
    delta_elbow = parameters.manikin.deltaelbow                  # Empirical derived distance, between the elbow of the driver, and the inner side of the door frame. Defined in (2)
    # endregion

    # region [2] Select SW16-1
    # Approximation of the vehicles classification according to the wheelbase. See (2)
    # All the given measures are in mm
    if L101 < 2493:
        delta = delta_elbow.segment_A
        SW16 = SW16_1.segment_A
    elif L101 < 2640:
        delta = delta_elbow.segment_B
        SW16 = SW16_1.segment_B
    elif L101 < 2750:
        delta = delta_elbow.segment_C
        SW16 = SW16_1.segment_C
    elif L101 < 2927:
        delta = delta_elbow.segment_D
        SW16 = SW16_1.segment_D
    elif L101 < 2992:
        delta = delta_elbow.segment_E
        SW16 = SW16_1.segment_E
    else:
        delta = delta_elbow.segment_F
        SW16 = SW16_1.segment_F
    # endregion

    # region [3] Calculation of the passenger compartment in Y direction
    # Calculate the elbow room for the first seating row W31-1 from the W103. See (2)
    coefficients = RegrW31.coefficients
    W31_1 = coefficients[0] + coefficients[1] * W103    # in mm

    # Check if the W103 is in the given regression limits
    if W103 < RegrW31.Limits['Indep_var_1'][0] or W103 > RegrW31.Limits['Indep_var_1'][1]:
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The value of W103, required for the W31 regression, is outside of the regression limits: ' \
                        'the calculated values will be extrapolated'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    # With the empirical derived elbow freeroom, and the manikin width, derive the W20-1 in mm (2, page 82)
    W20_1 = W31_1/2 - delta - manikin_width_elbow2elbow/2

    # From the calculated W201, derive an estimation for a realistic W20 in mm
    W20_2 = -112.655 + 0.119*L115_2 + 0.073*W201 + 0.164*W103 + 0.015*L101 - 0.006*CX_wheelhouse
    # endregion

    # region [4] Assign Outputs
    # Assign measures in Y direction:
    setattr(vehicle.manikin, 'W20_1', W20_1)
    setattr(vehicle.manikin, 'W20_2', W20_2)
    setattr(vehicle.manikin, 'SgRP_Y_vehicle_center', W20_1)
    setattr(vehicle.manikin, 'SgRP2_Y_vehicle_center', W20_2)
    setattr(vehicle.manikin, 'H95th_Y_vehicle_center', W20_1)
    setattr(vehicle.manikin, 'elbow2elbow_ANSURII', manikin_width_elbow2elbow)
    setattr(vehicle.manikin, 'W31_1', W31_1)
    setattr(vehicle.manikin, 'W201', W201)
    setattr(vehicle.manikin, 'SW16_1', SW16)
    # endregion

    return vehicle, parameters
