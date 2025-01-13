"""
Description:
        This function calculates the the dimensions of the wheelhouse. To do so, it simulates the extreme wheel position.
        Starting from the normal wheel position (here defined as DIN0 position) the wheel with the maximum deflection
        is simulated to derive the required wheelhouse height and width. We also simulate the wheel with the max rebound,
        as this is needed later to define the position of the shock absorber. We suppose for the wheel in DIN0 position
        a camber angle of 1°, for the wheel in max deflection an angle of 4° and for the wheel in max rebound an angle of 0°.

        The first reference system used in this function lays in the XY-plane. This reference system is used to
        calculate the required space in Y direction in case of steering at the rear axle. We suppose that the wheel
        turns at its middle point (situated at tire_radius/2 and tire_width/2.
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
        |                                          2----------------3

        The second system employed in this function lays at the point in the ZY plane, where the wheel can rotate.
        This point lays at tire_width/2+rim_inset. The graphic underneath shows an overview of the wheel with the
        employed reference system as well as the employed point numeration.
        |                                                           2----------------3
        |                                                           |                |
        |                                                           |                |
        |                                                           |         ^Z     |
        |                                      axis at wheel center |         |      |
        | vehicle center                        --------------------|         o -->Y |
        |                                                           |                |
        |                                                           |                |
        |                                       --------------------|                |
        |                                        lower axis         |                |
        |                                                           1----------------4
------------
Sources: (1) M. Spreng, „Maßkettenanalyse am Hinterwagen zur Erstellung von Ersatzmodellen,“Bachelor thesis, Faculty of Mechanical Engineering, Ostbayerische Technische Hochschule Regensburg, Regensburg, 2020.
         (2) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", Technical University of Munich, Institute of Automotive Technology, 2022
         More information to the wheelhouse sizing can be found at (1) and in Chapter 3.4.5 of (2)
------------
Input: vehicle: Class element, which stores all the vehicle information
       parameters: Class element, which stores all necessary computation parameters
------------
Output: Initialized tire dimensions based on the given tire diameter
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Calculate X Dimensions (wheelhouse length)
[3] Calculate Y Dimensions (wheelhouse width)
[3.1] Initialize the variables
[3.2] Calculate the displacement caused by the camber effect
[3.3] Calculate the displacement caused by the lower axis
[3.4] Calculate the position for the wheel with the max rebound
[3.5] Recalculate the wheelhouse width if steering angle is given
[4] Calculate Z Dimensions (wheelhouse height)
[5] Calculate Lower axis position
[6] Plot the results
[7] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
import math
import numpy as np
# Import functions
# endregion


def calc_wheelhouse_rear_dimensions(vehicle, parameters):
    # region [1] Assign Inputs
    tire_width = vehicle.dimensions.CY.wheel_r_width
    tire_radius = vehicle.dimensions.CX.wheel_r_diameter/2
    vehicle_width = vehicle.dimensions.GY.vehicle_width

    # camber angles are converted in RAD
    camber_middle = parameters.rear_axle.middle_camber_angle/180 * math.pi
    camber_def = parameters.rear_axle.deflected_camber_angle/180 * math.pi

    # Other measures:
    axistype = vehicle.topology.axis_type_r
    track_width = vehicle.dimensions.GY.track_width_r   # in mm

    # Minimum Offsets between wheel and wheelhouse in mm
    EX_wheel_wheelhouse = parameters.dimensions.EX.wheel_wheelhouse
    EY_wheel_wheelhouse = parameters.dimensions.EY.wheel_wheelhouse
    EZ_wheel_wheelhouse = parameters.dimensions.EZ.wheel_wheelhouse
    corr_factor_X = parameters.rear_axle.correction_factor_wheelhouse

    # Max rebound and max deflection in Z-direction in mm:
    max_def = vehicle.dimensions.EZ.max_deflection_r
    max_reb = 3 * max_def/4

    # Steering angle at the rear axle in GRAD
    delta_r = vehicle.wheels.steering_angle_r
    # endregion

    # region [2] Calculate X Dimensions (wheelhouse length)
    # Length of the wheelhouse at the max deflected wheel: The max deflected wheel is the state of the wheel,
    # which comes the closest to the wheelhouse. Therefore the length at the max deflected wheel center, has to have
    # a minimum offset of 20 mm
    wheelhouse_length = 2 * tire_radius + 2 * EX_wheel_wheelhouse   # in mm

    # Correct the length with the derived length factor at the position DIN0
    wheelhouse_length = wheelhouse_length + 2 * corr_factor_X     # in mm
    # endregion

    # region [3] Calculate Y Dimensions (wheelhouse width)
    # According to the axis type, assign the typical axis length, as well as the position of the lower axis
    # which is described by the variables CY_wheelcarrier and CZ_wheelcarrier.
    # For torsion_beam both variable are 0, as the axis is koaxial to the wheel center.

    # region [3.1] Initialize the variables
    match axistype:
        # axis_len_lower_axis: Average after categorisation in mm
        # CY_wheelcarrier: Average of the y difference between the coilaxis bearing and the outside of the wheelcarrier after categorisation in mm
        # ax_len_wheelaxis: Axis length, which will be used for the wheelhouse calculation in mm
        # CZ_wheelcarrier: Average after categorisation
        case 'trapezoidal_link':
            ax_len_lower_axis = parameters.dimensions.CY.axis_length_rear.trapezoidal_link
            CY_wheelcarrier = parameters.dimensions.CY.wheel_carrier.trapezoidal_link
            ax_len_wheelaxis = ax_len_lower_axis+CY_wheelcarrier
            CZ_wheelcarrier = parameters.dimensions.CZ.wheel_carrier.trapezoidal_link
        case 'sword_arm_link':
            ax_len_lower_axis = parameters.dimensions.CY.axis_length_rear.sword_arm_link
            CY_wheelcarrier = parameters.dimensions.CY.wheel_carrier.sword_arm_link
            ax_len_wheelaxis = ax_len_lower_axis+CY_wheelcarrier
            CZ_wheelcarrier = parameters.dimensions.CZ.wheel_carrier.sword_arm_link

        case 'five_link':
            ax_len_lower_axis = parameters.dimensions.CY.axis_length_rear.five_link
            CY_wheelcarrier = parameters.dimensions.CY.wheel_carrier.five_link
            ax_len_wheelaxis = ax_len_lower_axis+CY_wheelcarrier
            CZ_wheelcarrier = parameters.dimensions.CZ.wheel_carrier.five_link

        case _:     # torsion_beam
            ax_len_lower_axis = parameters.dimensions.CY.axis_length_rear.torsion_beam
            ax_len_wheelaxis = track_width/2
            CZ_wheelcarrier = 0
            CY_wheelcarrier = 0
    # endregion

    # region [3.2] Calculate the displacement caused by the camber effect
    # Position where the lower axis is flanged to the wheel with respect to the origin of the wheel (camber angle still 0° in this state)
    pos_lower_axis = np.array([-CY_wheelcarrier, -CZ_wheelcarrier])  # in mm

    # Initialize the four points of the wheel in the ZY plane, consider the rim_inset (camber angle still 0° in this state)
    y = np.zeros(4)
    z = np.zeros(4)
    y[0] = -(tire_width/2)
    y[1] = y[0]
    y[2] = tire_width/2
    y[3] = y[2]
    z[0] = -tire_radius
    z[1] = tire_radius
    z[2] = z[1]
    z[3] = z[0]

    # Calculate the repositioning of the points caused by the camber angle (1° for the DIN0 position)
    rot_angle = camber_middle                                                 # in rad
    rot_matrix = np.array([[math.cos(rot_angle), -math.sin(rot_angle)], [math.sin(rot_angle), math.cos(rot_angle)]])
    wheel_points = np.row_stack((y, z))
    points_wheel_DIN0 = np.matmul(rot_matrix, wheel_points)                 # in mm

    # Shift the origin of the wheel at the DIN0 position in Z direction for the radius height
    points_wheel_DIN0[1, :] = points_wheel_DIN0[1, :] + tire_radius           # in mm

    # Reposition the lower axis considering the effect of the camber angle (1° for the DIN0 position)
    pos_lower_axis_DIN0 = np.matmul(rot_matrix, pos_lower_axis.transpose())   # in mm
    pos_lower_axis_DIN0[1] = pos_lower_axis_DIN0[1] + tire_radius             # in mm

    # Calculate the repositioning of the points caused by the camber angle (4° for the max deflected wheel)
    rot_angle = camber_def                                                  # in rad
    rot_matrix = np.array([[math.cos(rot_angle), -math.sin(rot_angle)], [math.sin(rot_angle), math.cos(rot_angle)]])
    points_wheel_max_defl = np.matmul(rot_matrix, wheel_points)              # in mm

    # Shift the points of the max deflected wheel in Z direction for the radius and the max deflection
    points_wheel_max_defl[1, :] = points_wheel_max_defl[1, :] + tire_radius + max_def

    # Reposition the lower axis considering the effect of the camber angle (4° for the max deflected wheel)
    pos_lower_axis_max_defl = np.matmul(rot_matrix, pos_lower_axis.transpose())         # in mm
    pos_lower_axis_max_defl[1] = pos_lower_axis_max_defl[1] + tire_radius + max_def     # in mm
    # endregion

    # region [3.3] Calculate the displacement caused by the lower axis (the point where the lower axis is flanged has to move on a circle with a radius equal to the axis length).
    if axistype.lower() == 'torsion_beam':
        # torsion beam axes are rigid and therefore we suppose that there is no displacement in Y direction
        Y_displacement_lower_axis = 0
        # pos_lower_axis_max_defl = [0,tire_radius+max_def]
    else:
        # Z-displacement between the lower axis at DIN 0 and at the max deflection
        Z_displacement_lower_axis = abs(pos_lower_axis_max_defl[1] - pos_lower_axis_DIN0[1])    # in mm

        # Calculate the angle of the lower axis
        angle_lower_axis = math.asin(Z_displacement_lower_axis/ax_len_lower_axis)               # in rad

        # Calculate the displacement caused by the camber effect of 4°. Compare it with the wheel with 1° camber angle
        Y_displacement_lower_axis = ax_len_lower_axis - ax_len_lower_axis * math.cos(angle_lower_axis)  # in mm

    # Shift the wheel with max deflection of an offset equal to the y displacement of the lower axis
    points_wheel_max_defl[0, :] = points_wheel_max_defl[0, :] - Y_displacement_lower_axis         # in mm
    points_wheel_max_defl[1, :] = points_wheel_max_defl[1, :]                                     # in mm

    # The extreme point in Y-direction for the max deflected wheel with consideration of the Y-displacement
    y_displacement_def = abs(points_wheel_max_defl[0, 1])                                          # in mm

    # Wheelhouse values: For this calculation we have to consider the whole wheel, which means we cannot use the reference system which is located at tire_width/2 + rim_inset!
    wheelhouse_width = y_displacement_def + tire_width/2 + EY_wheel_wheelhouse

    # Calculate the distance between wheelhouse and vehicle center
    EY_wheelhouse_vehicle_center = track_width/2 - y_displacement_def - EY_wheel_wheelhouse
    # endregion

    # region [3.4] Calculate the position for the wheel with the max rebound
    # Points of the wheel in max rebound
    points_wheel_max_rebound = np.zeros((2, 4))
    points_wheel_max_rebound[0, :] = y
    points_wheel_max_rebound[1, :] = z + tire_radius - max_reb

    # Position of the lower axis with max rebound
    pos_lower_axis_max_rebound = np.zeros(2)
    pos_lower_axis_max_rebound[0] = pos_lower_axis[0]
    pos_lower_axis_max_rebound[1] = pos_lower_axis[1] - max_reb

    if axistype.lower() == 'torsion_beam':
        Y_displacement_lower_axis_max_rebound = 0

    else:
        # Z-displacement between the lower axis at DIN 0 and at the max deflection
        Z_displacement_lower_axis_max_rebound = abs(abs(pos_lower_axis_max_rebound[1]) -
                                                    abs((pos_lower_axis_DIN0[1])))              # in mm

        # Calculate the angle of the lower axis
        angle_lower_axis = math.asin(Z_displacement_lower_axis_max_rebound/ax_len_lower_axis)   # in rad

        # Calculate the displacement caused by the camber effect of 4°. Compare it with the wheel with 1° camber angle
        Y_displacement_lower_axis_max_rebound = ax_len_lower_axis - ax_len_lower_axis * math.cos(angle_lower_axis)  # in mm

    # Recalculate the position of the wheel while considering also the axle displacement
    points_wheel_max_rebound[0, :] = points_wheel_max_rebound[0, :] - Y_displacement_lower_axis_max_rebound
    # endregion

    # region [3.5] Recalculate the wheelhouse width if steering angle is given
    # Points describing the wheel in the XY plane (see numeration system underneath)
    x = np.zeros(4)
    x[0] = tire_radius
    x[1] = -tire_radius
    x[2] = -tire_radius
    x[3] = tire_radius
    y[0] = -tire_width/2
    y[1] = -tire_width/2
    y[2] = tire_width/2
    y[3] = tire_width/2
    points_wheel_no_rotation = np.row_stack((y, x))

    if delta_r > 0:  # The vehicle has a steering angle at the rear axle
        # Calculate the repositioning of the points caused by the camber angle (1° for the DIN0 position)
        rot_angle = -math.radians(delta_r)                                         # in rad
        rot_matrix = np.array([[math.cos(rot_angle), math.sin(rot_angle)], [-math.sin(rot_angle), math.cos(rot_angle)]])
        points_wheel_max_rotation = np.matmul(rot_matrix, points_wheel_no_rotation)

        # Refer the points to the vehicle center
        points_wheel_no_rotation[0, :] = points_wheel_no_rotation[0, :] + track_width/2
        points_wheel_max_rotation[0, :] = points_wheel_max_rotation[0, :] + track_width/2

        # As the wheel has a steering angle, the width of the wheelhouse needs to be corrected
        EY_wheelhouse_vehicle_center_rear_angle_steering = abs(points_wheel_max_rotation[0, 0]) - EY_wheel_wheelhouse
        wheelhouse_width_rear_angle_steering = vehicle_width/2 - EY_wheelhouse_vehicle_center_rear_angle_steering

        # Choose for the wheelhouse width the case (between max wheel displacement and max wheel steering) that requires more space
        wheelhouse_width = max(wheelhouse_width, wheelhouse_width_rear_angle_steering)

        # Choose for the EY_wheelhouse_vehicle_center (i.e. the available space at the rear axle) the case (between max wheel displacement and max
        # wheel steering) that generates the lower available space
        EY_wheelhouse_vehicle_center = min(EY_wheelhouse_vehicle_center, EY_wheelhouse_vehicle_center_rear_angle_steering)

    else:
        points_wheel_max_rotation = np.zeros((2, 4))
    # endregion
    # endregion

    # region [4] Calculate Z Dimensions (wheelhouse height)
    # The extreme point in Z-direction for the max deflected wheel
    Z_max = points_wheel_max_defl[1, 2]

    # Add at the highest point, the minimum offset for the skid_chain
    wheelhouse_height = Z_max + EZ_wheel_wheelhouse
    # endregion

    # region [5] Calculate Lower axis position
    # Calculate back to find the relative position of the axle with respect to the motor, thus deriving the motor space in Y
    coilaxis_inner_bearing_y_coordinate = track_width/2 - ax_len_wheelaxis
    coilaxis_inner_bearing_z_coordinate = -CZ_wheelcarrier
    # endregion

    # region [6] Plot the results
    # Refer the position of the Points to the vehicle center
    points_wheel_DIN0[0, :] = points_wheel_DIN0[0, :] + track_width/2
    points_wheel_max_defl[0, :] = points_wheel_max_defl[0, :] + track_width/2
    points_wheel_max_rebound[0, :] = points_wheel_max_rebound[0, :] + track_width/2
    # endregion

    # region [7] Assign the required Outputs
    # Wheelhouse dimensions and coordinate expressed in mm
    setattr(vehicle.dimensions.CX, 'wheelhouse_r_length', wheelhouse_length)
    setattr(vehicle.dimensions.CY, 'wheelhouse_r_width', wheelhouse_width)
    setattr(vehicle.dimensions.CZ, 'wheelhouse_r_height', wheelhouse_height)
    setattr(vehicle.dimensions.EY, 'wheelhouse_r_vehicle_center', EY_wheelhouse_vehicle_center)
    setattr(vehicle.dimensions.EY, 'axis_vehicle_center', coilaxis_inner_bearing_y_coordinate)
    setattr(vehicle.dimensions.EZ, 'axis_wheel_center', coilaxis_inner_bearing_z_coordinate)
    setattr(vehicle.dimensions.CY, 'axis_length_r', ax_len_lower_axis)

    # Wheelcarrier dimensions in mm
    setattr(vehicle.dimensions.EZ, 'lower_axis_r_wheelcenter', CZ_wheelcarrier)     # Needed for positioning the shock absorber
    setattr(vehicle.dimensions.EY, 'lower_axis_r_wheelcenter', CY_wheelcarrier)

    # Point cloud describing the wheels in mm
    setattr(vehicle.wheels, 'points_wheel_max_rebound_yz', points_wheel_max_rebound)
    setattr(vehicle.wheels, 'points_wheel_DIN0_yz', points_wheel_DIN0)
    setattr(vehicle.wheels, 'points_wheel_max_deflection_yz', points_wheel_max_defl)
    setattr(vehicle.wheels, 'points_wheel_r_no_rotation', points_wheel_no_rotation)
    setattr(vehicle.wheels, 'points_wheel_r_max_rotation', points_wheel_max_rotation)

    # Assign the Y_displacement required later for the plot
    setattr(vehicle.dimensions.EY, 'axis_displacement_max_rebound_r', Y_displacement_lower_axis)

    # Angle of the wheel in the maximum deflected position (required for the plotting)
    setattr(vehicle.wheels, 'camber_angle_max_defl_r', camber_def)
    # endregion

    return vehicle, parameters
