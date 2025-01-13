"""
Description: This function calculates the positioning of the shock absorber. The upper point of the shock absorber
             is placed as closed as possible to the wheelhouse (in Y-direction).
             The lower point of the shock absorber is also placed as close as possible with the wheel.
             The reference system of this function has the following characteristics:
                X0: located at the front axle
                 Y0: located to the vehicle center
                 Z0: located at the height of the wheel center
------------
Sources: (1) M. Spreng, "Maßkettenanalyse am Hinterwagen zur Erstellung von Ersatzmodellen",“Bachelor thesis, Faculty of Mechanical Engineering, Ostbayerische Technische Hochschule Regensburg, Regensburg, 2020.
         More information to the shock absorber sizing can be found at (1)
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The vehicle structure updated with the shock absorber position
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Position upper part of the shock absorber
[3] Position lower part of the shock absorber
[4] Iterate to correct the position of the upper part
[5] Check if there is a contact between the shock absorber and the complete rebounded wheel
[6] Calculate the shock absorber position along X, depending on the topology
[7] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
import math
import copy
# endregion


def calc_shock_absorber_position(vehicle, parameters):
    # region [1] Assign Inputs
    # topology of the vehicle, required to shift the shock absorber in X direction in case the rear axle has a machine
    topology = vehicle.topology.drive

    # Wheel dimensions, wheelbase, track width
    tire_side_wall = vehicle.wheels.side_wall_r                 # in %
    tire_radius = vehicle.dimensions.CX.wheel_r_diameter/2      # in mm
    wheelbase = vehicle.dimensions.GX.wheelbase                 # in mm
    track_width = vehicle.dimensions.GY.track_width_r           # in mm

    # Axis Type and ground clearance
    H156 = vehicle.dimensions.GZ.H156
    axis_type = vehicle.topology.axis_type_r

    # shock absorber dimensions in mm
    upper_bearing_diameter_shock_absorber = vehicle.dimensions.CX.upper_bearing_diameter_shock_absorber
    height_upper_bearing_shock_absorber = vehicle.dimensions.CZ.height_upper_bearing_shock_absorber
    piston_diameter = vehicle.dimensions.CX.piston_diameter

    # Wheelhouse dimensions in mm
    EY_wheelhouse_vehicle_center = vehicle.dimensions.EY.wheelhouse_r_vehicle_center

    # Wheelhouse height referred to the position of the rear axle
    wheelhouse_height = vehicle.dimensions.CZ.wheelhouse_r_height - tire_radius

    # Points describing the position of the DIN0, max deflection and max rebound wheel
    # Copy is necessary for not changing the objects attribute
    points_wheel_max_rebound = copy.deepcopy(vehicle.wheels.points_wheel_max_rebound_yz)

    # Values required to position the lower axis in mm
    CY_wheelcarrier = vehicle.dimensions.EY.lower_axis_r_wheelcenter
    distance_z_wheelmiddle_bearing = vehicle.dimensions.EZ.lower_axis_r_wheelcenter
    # endregion

    # region [2] Position upper part of the shock absorber
    # The angle of the shock absorber is not known so for the first positioning we suppose an angle of 0°
    if H156 > 200:  # This corresponds to a highfloor ground clearance
        # Z-coordinate of the upper shock absorber point is at the wheel radius height
        upper_point_sa_z = tire_radius

    else:   # This correspond to a lowfloor ground clearance
        # Z-coordinate of the upper shock absorber point is at the height of the z-coordinate wheelhouse
        upper_point_sa_z = wheelhouse_height

    upper_point_sa_y = EY_wheelhouse_vehicle_center - (upper_bearing_diameter_shock_absorber/2)
    # endregion

    # region [3] Position lower part of the shock absorber
    EY_sa_wheelcarrier = 0                  # Initialize to avoid python warning
    match axis_type:
        case 'trapezoidal_link':
            EY_sa_wheelcarrier = 72        # [mm] Average after categorisation conducted in (1)
        case 'sword_arm_link':
            EY_sa_wheelcarrier = 89.24     # [mm] Average after categorisation conducted in (1)
        case 'five_link':
            EY_sa_wheelcarrier = 78.22     # [mm] Average after categorisation conducted in (1)

    if axis_type.lower() == 'torsion_beam':
        # torsion_beam normally position the shock absorber vertically, i.e. with a 0° angle
        # -> upper and lower point have the same Y-position!
        lower_point_sa_z = 0
        lower_point_sa_y = upper_point_sa_y

    else:
        # calculates the z-coordinate of the lower shock absorber bearing(reference DIN0) [mm]
        lower_point_sa_z = -distance_z_wheelmiddle_bearing
        # calculates the y-coordinate of the lower shock absorber bearing(reference DIN0) [mm]
        lower_point_sa_y = (track_width/2) - CY_wheelcarrier - EY_sa_wheelcarrier

    # The upper point cannot have an y value higher than the lower point:
    # If that is the case set the shock absorber to an angle of 0°
    upper_point_sa_y = min(upper_point_sa_y, lower_point_sa_y)
    # endregion

    # region [4] Iterate to correct the position of the upper part
    # Having positioned the lower part, the shock absorber angle can be derived. Therefore the upper point
    # (which was initially positioned using an inclination angle of 0°) has to be shifted in order
    # to avoid collision with the wheelhouse
    delta = 1                               # Deviation between two consecutive shock absorber positions, in mm
    pos_y = np.array([upper_point_sa_y])    # Position of shock absorber at the first iteration in mm

    # Iterate to find the correct position
    if upper_point_sa_y == lower_point_sa_y:

        angle_shock_absorber = 0
    else:
        while delta > 0.01:

            # Calculate angle between the shock absorber and the XZ Level in [rad]
            angle_shock_absorber = math.atan(abs(lower_point_sa_y - upper_point_sa_y) /
                                             (upper_point_sa_z - lower_point_sa_z))

            # Reposition the shock upper point using the calculated angle
            pos_y_loop = EY_wheelhouse_vehicle_center - \
                         (upper_bearing_diameter_shock_absorber/2) * math.cos(angle_shock_absorber) - \
                         height_upper_bearing_shock_absorber * math.sin(angle_shock_absorber)
            pos_y = np.append(pos_y, pos_y_loop)

            # Test the delta y from the position of the previous loop
            delta = abs(pos_y[-1] - pos_y[-2])

        # Corrected y-coordinate of the upper_bearing_shock_absorber
        upper_point_sa_y = pos_y[-1] - 27.1

        # Angle needs to be corrected too after the shifting!
        angle_shock_absorber = math.atan(abs(lower_point_sa_y - upper_point_sa_y) /
                                         (upper_point_sa_z - lower_point_sa_z))
    # endregion

    # region [5] Check if there is a contact between the shock absorber and the complete rebounded wheel
    # Load the reference point of the wheels in max rebound and reposition them according to the reference system:
    points_wheel_max_rebound[1, :] = points_wheel_max_rebound[1, :] - tire_radius

    # Find the Y and Z coordinates of the critical point of the max rebounded wheel.
    # This point shall not collide with the shock absorber!
    critical_point_rebound_y = points_wheel_max_rebound[0, 0]
    critical_point_rebound_z = points_wheel_max_rebound[1, 1] - tire_side_wall * 100

    # Calculate the Y coordinate of the outer surface of the shock absorber at the height
    # of the critical point of the max rebounded wheel
    outer_critic_point_y = lower_point_sa_y - critical_point_rebound_z * math.tan(angle_shock_absorber) + \
                          (piston_diameter/2) * math.cos(angle_shock_absorber)

    # Check that the shock absorber does not collide with the wheel
    if outer_critic_point_y > critical_point_rebound_y:

        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'Collision between shock absorber and wheel. The shock absorber will be shifted'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

        # If there is collision shift the shock absorber in Y direction
        offset = outer_critic_point_y - critical_point_rebound_y
        upper_point_sa_y = upper_point_sa_y-offset
        lower_point_sa_y = lower_point_sa_y-offset
    # endregion

    # region [6] Calculate the shock absorber position along X, depending on the topology
    # Idea: If there is a machine on the rear axle, the X position of the shock
    # absorber has to be changed, to avoid collision with the side shaft of the machine.
    # The damper can be shifted behind or in front of the driveshaft,
    # this can vary depending on the axle type and the manufacturer
    if not topology == 'FWD':   # There is a machine on the rear axle

        # Estimate a driveshaft radius of 30 mm, which should be above any possible driveshaft radius
        driveshaft_radius = 30

        # position the shock absorber 20 mm far away to the driveshaft
        # -> This ensures there is no collision between driveshaft and shock absorber
        lower_point_sa_x = wheelbase - driveshaft_radius - piston_diameter/2 - 20
        upper_point_sa_x = wheelbase - driveshaft_radius - piston_diameter/2 - 20
    else:
        # Position the driveshaft at the very center of the rear axle:
        lower_point_sa_x = wheelbase
        upper_point_sa_x = wheelbase
    # endregion

    # region [7] Assign Outputs
    lower_point_sa_z_front_axle = lower_point_sa_z + tire_radius
    upper_point_sa_z_front_axle = upper_point_sa_z + tire_radius
    # Position lower point (middle axis of the shock absorber) -> refer the z position to the ground
    setattr(vehicle.dimensions.EX, 'lower_point_shock_absorber_front_axle', lower_point_sa_x)               # in mm
    setattr(vehicle.dimensions.EY, 'lower_point_shock_absorber_vehicle_center', lower_point_sa_y)           # in mm
    setattr(vehicle.dimensions.EZ, 'lower_point_shock_absorber_front_axle', lower_point_sa_z_front_axle)    # in mm

    # Position upper point (middle axis of the shock absorber)-> refer the z position to the ground
    setattr(vehicle.dimensions.EX, 'upper_point_shock_absorber_front_axle', upper_point_sa_x)               # in mm
    setattr(vehicle.dimensions.EY, 'upper_point_shock_absorber_vehicle_center', upper_point_sa_y)           # in mm
    setattr(vehicle.dimensions.EZ, 'upper_point_shock_absorber_front_axle', upper_point_sa_z_front_axle)    # in mm

    # Inclination angle of the shock absorber (in DEG)
    setattr(vehicle.wheels, 'angle_shock_absorber_r', math.degrees(angle_shock_absorber))
    # endregion

    return vehicle, parameters
