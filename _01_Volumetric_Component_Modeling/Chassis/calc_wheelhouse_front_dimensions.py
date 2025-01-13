"""
Description:
           This function calculates the axle distribution for different cases.
           The function calculates the load defined in the ERTRO manual (88% and 100% rule).
           The calculated loads will be used in the following function to dimension the wheels.
           The graphic underneath shows an overview of the wheel with the employed the employed point numeration
           |                  ^X direction            1----------------4
           |                  |                       |                |
           |                  |                       |                |
           |                  ------>Y direction      |                |
           |vehicle center                            |                |
           |                                          |                |
           |                                          |                |
           |                                          |                |
           |                                          |                |
           |                                          |                |
           |                                                                     1----------------4
------------
Sources: (1) Semester Thesis Andrea Romano, Datenbasierte Analyse zur geometrischen Modellierung von Reifen und Felgen, 2020, FTM
         (2) A. Obermüller, „Dynamic All-wheel steering (DAS),“ in 8th International Munich Chassis Symposium, P. Pfeffer, ed. Wiesbaden: Springer Fachmedien Wiesbaden, 2017, pp. 487–498, DOI: 10.1007/978-3-658-18459-9_31.
         (3) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
------------
Input: vehicle: Class element, which stores all the vehicle information
       parameters: Class element, which stores all necessary computation parameters
------------
Output: Dimensions of the front wheelhouse
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Input
[2] Calculate turning diameter (only if not defined in the Excel sheet)
[3] Calculate the front steering angle
[4] Calculate wheelhouse dimensions
[5] Calculate the wheelhouse as point cloud
[6] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
import math
import numpy as np
# Import functions
from .calc_steering_angle import calc_steering_angle
# endregion


def calc_wheelhouse_front_dimensions(vehicle, parameters):
    # region [1] Assign Inputs
    # Inputs for the calculation of the steering angle/angles
    wheelbase = vehicle.dimensions.GX.wheelbase             # in mm
    width = vehicle.dimensions.GY.vehicle_width             # in mm
    track_f = vehicle.dimensions.GY.track_width_f           # in mm
    overhang_f = vehicle.dimensions.GX.vehicle_overhang_f   # in mm

    # Inputs for the calculation of the wheel volume
    tire_diameter = vehicle.dimensions.CX.wheel_f_diameter  # in mm
    tire_width = vehicle.dimensions.CY.wheel_f_width        # in mm

    # turning circle: it may be that the user assigned a turning circle:
    turning_diameter = vehicle.dimensions.GY.turning_diameter            # in m

    # Wheelhouse position
    EX_wheel_wheelhouse = parameters.dimensions.EX.wheel_wheelhouse             # Min offset between wheel and wheelhouse in mm (measured at the max deflected position of the wheelhouse)
    corr_factor_X = parameters.rear_axle.correction_factor_wheelhouse           # Correction factor to recalculate the wheelhouse length at the non deflected height of the wheel in mm
    EY_wheel_wheelhouse = parameters.dimensions.EY.wheel_wheelhouse             # Min offset between wheel and wheelhouse in mm (measured at the max deflected position of the wheelhouse)
    CY_wheelhouse_thickness = parameters.dimensions.CY.wheelhouse_thickness     # Wheelhouse thickness in mm
    # endregion

    # region [2] Calculate turning diameter (only if not defined in the Excel sheet)
    if np.isnan(turning_diameter):
        # Regression turning circle see (1, p.69)
        Regrturning_circle = parameters.regr.exterior.turning_circle

        # Calculate turning diameter in m
        regr_coefficient = Regrturning_circle.coefficients
        turning_diameter = regr_coefficient[0] + regr_coefficient[1] * wheelbase + regr_coefficient[2] * width

        # Ensure that the given wheelbase is within the validity range of the regression
        if wheelbase < Regrturning_circle.Limits['Indep_var_1'][0] or wheelbase > Regrturning_circle.Limits['Indep_var_1'][1]:
            errorlog_list = vehicle.errorlog
            text_errorlog = 'The value of L101, required for the turning diameter regression, ' \
                            'is outside of the regression limits: the calculated values will be extrapolated'
            print(text_errorlog)
            errorlog_list.append(text_errorlog)
            setattr(vehicle, 'errorlog', errorlog_list)

        if width < Regrturning_circle.Limits['Indep_var_2'][0] or width > Regrturning_circle.Limits['Indep_var_2'][1]:
            errorlog_list = vehicle.errorlog
            text_errorlog = 'The value of W103, required for the turning diameter regression, ' \
                            'is outside of the regression limits: the calculated values will be extrapolated'
            print(text_errorlog)
            errorlog_list.append(text_errorlog)
            setattr(vehicle, 'errorlog', errorlog_list)
    # endregion

    # region [3] Calculate the front steering angle
    # Calculation according to (3, p.36-39)
    delta_r_i_deg = vehicle.wheels.steering_angle_r
    delta_f_i_deg, delta_f_o_deg, turning_diameter_sim = \
        calc_steering_angle(turning_diameter, delta_r_i_deg, wheelbase, overhang_f, width, track_f)
    # endregion

    # region [4] Calculate wheelhouse dimensions
    # Length of the wheelhouse at the max deflected wheel: The max deflected wheel is the state of the wheel, which comes the closest to the wheelhouse.
    # Therefore the length at the max deflected wheel center, has to have a minimum offset of 20 mm
    CX_wheelhouse_f = tire_diameter + 2 * EX_wheel_wheelhouse   # in mm

    # Correct the length with the derived length factor at the position DIN0
    CX_wheelhouse_f = CX_wheelhouse_f + 2 * corr_factor_X       # in mm

    # Wheelhouse dimensions in Y direction, depending from the maximum steering angle (front and rear)
    CY_wheelhouse_f = (tire_diameter/2) * math.sin(math.radians(delta_f_i_deg)) + (tire_width/2) * math.cos(math.radians(delta_f_i_deg)) + tire_width/2 + EY_wheel_wheelhouse + CY_wheelhouse_thickness

    # Refer position of the wheelhouse to the center of the vehicle
    EY_wheelhouse_vehicle_center = width/2 - CY_wheelhouse_f
    # endregion

    # region [5] Calculate the wheelhouse as point cloud
    # Calculate the repositioning of the points due to the steering angle
    # Points describing the wheel in the XY plane (see numeration system above)
    x = np.array([tire_diameter/2, -tire_diameter/2, -tire_diameter/2, tire_diameter/2])
    y = np.array([-tire_width/2, -tire_width/2, tire_width/2, tire_width/2])

    # The point 2 is the closest to the battery, therefore the critical point.
    # For the Y direction also consider the wheelhouse thickness
    # For the X direction the thickness is already contained in CX_wheelhouse_f
    basis_point = np.zeros((2, 1))
    basis_point[1, 0] = x[1] + 10  # Add 10 mm minimum distance between wheel and wheelhouse
    basis_point[0, 0] = y[1] - 10  # Add 10 mm minimum distance between wheel and wheelhouse

    # Define a discretized vector from 0 to the max rotation angle
    num_points = 1000
    rot_angles = np.linspace(0, math.radians(delta_f_i_deg), num_points)
    point_path = np.zeros((2, num_points))
    # Calculate the travel path of the point for a rotation until delta_i_max
    for i in range(np.size(rot_angles)):

        rot_matrix = np.array([[math.cos(rot_angles[i]), math.sin(rot_angles[i])], [-math.sin(rot_angles[i]), math.cos(rot_angles[i])]])
        point_path[:, [i]] = np.matmul(rot_matrix, basis_point)

    delta_x = -CX_wheelhouse_f * 0.5 - point_path[1, 0]
    point_path[1, :] = point_path[1, :] + delta_x

    # Shift the travel path in the correct coordinates in Y
    point_path[0, :] = point_path[0, :] + track_f/2
    delta_y = EY_wheelhouse_vehicle_center - np.amin(point_path[0, :])
    point_path[0, :] = point_path[0, :] + delta_y

    # Calculate the other two segments of the wheelhouse
    y_max = np.amax(point_path[0, :])
    segment_1_1 = np.linspace(track_f/2, y_max, 100)
    segment_1_2 = -np.ones((1, 100)) * CX_wheelhouse_f * 0.5
    segment_1 = np.row_stack((segment_1_1, segment_1_2))

    y_min = np.amin(point_path[0, :])
    segment_2_1 = np.ones((1, 100)) * y_min
    segment_2_2 = np.linspace(np.amax(point_path[1, :]), 0, 100)
    segment_2 = np.row_stack((segment_2_1, segment_2_2))

    # Unite the segments and add the Z coordinate
    wheelhouse_f_1 = -np.hstack((segment_1[1, :], point_path[1, :], segment_2[1, :]))
    wheelhouse_f_2 = np.hstack((segment_1[0, :], point_path[0, :], segment_2[0, :]))
    wheelhouse_f_size = np.shape(wheelhouse_f_2)[0]
    wheelhouse_f_3 = np.ones((1, wheelhouse_f_size)) * tire_diameter/2
    wheelhouse_f = np.row_stack((wheelhouse_f_1, wheelhouse_f_2, wheelhouse_f_3))
    # endregion

    # region [6] Assign Outputs
    # Steering angles at front and rear axle in deg
    setattr(vehicle.wheels, 'steering_angle_f_i', delta_f_i_deg)
    setattr(vehicle.wheels, 'steering_angle_f_o', delta_f_o_deg)
    setattr(vehicle.wheels, 'steering_angle_r', delta_r_i_deg)

    # Dimensions of the wheelhouse (The height will be taken from the wheelhouse rear) in mm
    setattr(vehicle.dimensions.CX, 'wheelhouse_f_length', CX_wheelhouse_f)
    setattr(vehicle.dimensions.CY, 'wheelhouse_f_width', CY_wheelhouse_f)
    setattr(vehicle.dimensions.CY, 'wheelhouse_thickness', CY_wheelhouse_thickness)

    # Position the wheelhouse with respect to the front axle
    wheelhouse_f_vehicle_center = EY_wheelhouse_vehicle_center-CY_wheelhouse_thickness
    setattr(vehicle.dimensions.EY, 'wheelhouse_f_vehicle_center', wheelhouse_f_vehicle_center)
    setattr(vehicle.dimensions.EX, 'wheelhouse_f_front_axle', 0)

    # Shape of the front wheelhouse (calculated at point 5) -> Expressed as matrix with the coordinate in X, Y and Z
    setattr(vehicle.wheels, 'wheelhouse_f', wheelhouse_f)

    # Assign the turning diameter in m
    setattr(vehicle.dimensions.GY, 'turning_diameter', turning_diameter_sim)
    # endregion

    return vehicle, parameters
