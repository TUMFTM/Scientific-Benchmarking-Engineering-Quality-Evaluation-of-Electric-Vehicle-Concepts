"""
Description:    This function calculates the trunk dimensions. Therefore the available values
                in all the three directions are estimated based on mean values and regressions.
                In the end the available volume is computed
------------
Sources: (1) SAE J826 - https://www.sae.org/standards/content/j1100_200911/
         (2) Kühberger Moritz, "Further development of a simulation model for the evaluation
         of electric vehicle concepts in the field of package", Semester Thesis, FTM, 2023
------------
Input:   vehicle: Class element, which stores all the vehicle information
         parameters: Class element, which stores all necessary computation parameters
------------
Output:  Updated classes vehicle and parameters with the trunk dimensions and its volume
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Local input declaration
[2] Compute the lower z-front of the trunk (H252)
[3] Compute the lower x-front of the trunk
[4] Compute the higher z-front of the trunk (H297_2)
[5] Compute the higher x-front of the trunk (L209_2)
[6] Compute the width of the trunk (W201)
[7] Compute the Trunkcontur from a2mac1 in the right position and scale it to the size of the modeled trunk
[8] Compute the area under the rear seats z-front of the trunk (H252)
[9] Compute the volume of the trunk underneath the real Contur
[10] Assign the Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import numpy as np
import math
import os
import json
# Import classes
# Import methods
# endregion


def calc_dimension_trunk(vehicle, parameters):
    # region [1]: Local input declaration

    # Distance between motor and begin of trunk compartment
    distance_z_power_trunk = parameters.dimensions.EZ.distance_z_power_trunk
    SgRP2_Z = vehicle.manikin.H5_2              # Distance from the SgPR2 to the ground
    angle_torso = 25                            # rotational angle of the torso in the second seat row [1,page 9]
    torso_length = 594.9                        # total length of the torso in mm [1,page 5]
    SgRP2_to_seat = 98.0                        # total length of the distance between SgRP2 and the seating area [1,page 5]
    H252 = vehicle.Input.H252                   # real H252 from a2mac1/Excel to use for FWD cars
    H252_real_vehicle = H252                    # real H252 from a2mac1/Excel and use for scaling factor 1
    H297_2_real_vehicle = vehicle.Input.H297_2  # real H297_2 from a2mac1/Excel and use for scaling factor 1

    wheelbase = vehicle.dimensions.GX.wheelbase                     # Wheelbase in mm
    overhang_rear = vehicle.dimensions.GX.vehicle_overhang_r        # Rear overhang in mm
    SgRP2_X = vehicle.manikin.SgRP2_X_front_axle                    # Distance between front axle and SgRP_1 of seats(L114 + L50_2)

    # Lost luggage space at the rear overhang due to bumpers, trunk frame etc. in mm
    EX_L105_2_luggage = parameters.dimensions.EX.L105_to_luggage
    SGRP2_to_Seatback = parameters.dimensions.EX.SGRP2_to_Seatback  # Longitudinal distance SgRP_2 to backseat in mm
    SL14_2 = parameters.manikin.SL14_2                              # Thickness of the backseat along the X direction in mm

    # Distance from the upper point of the shock absorber to the vehicle center
    upp_sa_y = vehicle.dimensions.EY.upper_point_shock_absorber_vehicle_center
    # Diameter of the upper bearing
    upper_bearing_diameter_shock_absorber = vehicle.dimensions.CX.upper_bearing_diameter_shock_absorber
    # Rotation angle of the shock absorber around the x
    angle_shock_absorber = vehicle.wheels.angle_shock_absorber_r
    # Distance between trunk & end of shock absorber
    distance_y_sa_trunk = parameters.dimensions.EY.distance_y_sa_trunk

    # get the trunk contur given as an input
    path_project = os.getcwd()
    path_characteristics = os.path.join(path_project, '_04_Visualization', 'trunkframe')
    vehicle_name = vehicle.Input.vehicle_name
    full_path = os.path.join(path_characteristics, vehicle_name)

    # if no trunk contur is given, use a default one
    if not os.path.exists(full_path):
        vehicle_name = 'Unknown Vehicle'
        full_path = os.path.join(path_characteristics, vehicle_name)

    full_path = os.path.join(full_path, 'Trunkform_Contur.json')
    with open(full_path, "r") as file:
        Trunkform_Contur = json.load(file)

    Trunkform_Contur = np.array(Trunkform_Contur['Trunkform_Contur'])
    # endregion

    # region [2]: Compute the lower z-front of the trunk (H252)
    # Note that in case of two motors on the rear axle it is sufficient considering just one of them because of the
    # assumption that they have the same size

    # if hasattr(vehicle.gearbox[axle].Input, 'gear_orientation'):  # RWD or AWD
    if vehicle.topology.drive != 'FWD':
        axle = 'rear'  # Store the axle if there is a motor on the rear axle
        gearbox = vehicle.gearbox[axle]
        EZ_shaft_1_front_axle = gearbox.position.EZ_shaft_1_front_axle  # Get the height of the rear axle
        # Get the coordinates of the highest point of the gearbox housing
        if gearbox.Input.type == 'planetary':
            EZ_gearbox_housing = EZ_shaft_1_front_axle + gearbox.position.EZ_gearbox_housing[1]
        else:
            EZ_gearbox_housing = gearbox.position.EZ_gearbox_housing[0] + gearbox.dimension_house.h_gearbox

        # Get the coordinates of the highest point of the machine housing
        radius_motor = 0.5 * vehicle.e_machine[axle].CX_e_machine_diameter
        EZ_motor_housing = EZ_shaft_1_front_axle + radius_motor
        # Compare the heights of motor and gearbox
        EZ_height_powertrain = max(EZ_gearbox_housing, EZ_motor_housing)
        # Compute lower front by adding the tire_radius, the motor_radius and a constant value
        H252 = EZ_height_powertrain + distance_z_power_trunk
    # endregion

    # region [3]: Compute the lower x-front of the trunk
    # Begin of the luggage line on the same height as the SgRP2
    EX_luggage_start_SgRP2 = SgRP2_X + SGRP2_to_Seatback + SL14_2
    # Compute the cross-section of lower x-front and lower z-front
    EX_diff_SgRP2_luggage_start = (SgRP2_Z - H252) * math.tan(angle_torso * math.pi / 180)
    EX_luggage_start_front_axle = EX_luggage_start_SgRP2 - EX_diff_SgRP2_luggage_start
    # endregion

    # region [4]: Compute the higher z-front of the trunk (H297_2)
    # Compute the difference between SgRP-2 and torso height in z-direction
    torso_length_SgRP2 = torso_length - SgRP2_to_seat
    EZ_SgRP2_to_torso = torso_length_SgRP2 * math.cos(angle_torso * math.pi / 180)
    EZ_ground_to_torso = SgRP2_Z + EZ_SgRP2_to_torso
    H297_2 = EZ_ground_to_torso - H252  # Compute the height of the trunk compartment

    # Compute the length of the triangular space underneath the rear seat
    EX_luggage_top_start_front_axle = EX_luggage_start_front_axle + H297_2 * math.sin(angle_torso * math.pi / 180)
    # endregion

    # region [5]: Compute the higher x-front of the trunk (L209_2)
    # Derive the length of the luggage compartment. Consider that it is not possible to use the entire rear overhang
    # length due to components like the trunk frame

    # length of trunk to rear side of seats in 2nd row
    L209_2 = wheelbase - EX_luggage_start_front_axle + overhang_rear - EX_L105_2_luggage
    EX_luggage_end_front_axle = EX_luggage_start_front_axle + L209_2
    # endregion

    # region [6]: Compute the width of the trunk (W201)
    # Calculate the y-coordinate of the innermost point of the shock absorber
    EY_innermost_shock_absorber = upper_bearing_diameter_shock_absorber * math.cos(angle_shock_absorber * math.pi / 180)

    # Calculate the beginning end of the trunk in y-direction
    W201 = upp_sa_y - EY_innermost_shock_absorber - distance_y_sa_trunk
    # endregion

    # region [7]: Compute the Trunkcontur from a2mac1 in the right position and scale it to the size of the modeled trunk
    # Get distance from center KoSy Trunk_Contur to center rear wheel
    distance_center_rear_wheel_center_KoSy = Trunkform_Contur[0, :]  # get position of CoSy of contour
    Trunkform_Contur = np.delete(Trunkform_Contur, 0, 0)  # delete the value of the CoSy

    # get Trunkform_Contur in the position of the real trunk from a2mac1
    Trunkform_Contur[:, 0] = Trunkform_Contur[:, 0] + wheelbase
    Trunkform_Contur[:, 1] = Trunkform_Contur[:, 1] + vehicle.Input.tire_diameter / 2
    Trunkcontur_Positioned = Trunkform_Contur - distance_center_rear_wheel_center_KoSy

    # compile the scaling factors in x & y direction to adapt to model
    # scaling factor in x direction
    scale_factor_1 = (EX_luggage_end_front_axle - EX_luggage_top_start_front_axle) / (max(Trunkcontur_Positioned[:, 0])
                                                                                      - min(
                Trunkcontur_Positioned[:, 0]))
    # scaling factor in y direction
    scale_factor_2 = (H252 - (H252 + H297_2)) / (min(Trunkcontur_Positioned[:, 1]) - max(Trunkcontur_Positioned[:, 1]))

    # take the positioned Contur and scale it to the model
    scaled_contur = np.array((Trunkcontur_Positioned[:, 0] - Trunkcontur_Positioned[0, 0]) * scale_factor_1 + EX_luggage_top_start_front_axle)

    # take the x values for the scaled trunk contur and reshape to a nx1 array
    scaled_contur = scaled_contur.reshape((len(scaled_contur), 1))

    scaled_contur_y = 0
    # scale in y direction in 2 ways (5 due to deviations in contur form a2mac1)
    if max(Trunkcontur_Positioned[:, 1]) > Trunkcontur_Positioned[0, 1] + 5:
        # if first point in scaled_contur is not the highest point (max)
        scaled_contur_y = (Trunkcontur_Positioned[:, 1] - (H252_real_vehicle + H297_2_real_vehicle)) * scale_factor_2 + (H252 + H297_2)
    else:
        # first point in scaled_contur is the highest point
        scaled_contur_y = (Trunkcontur_Positioned[:, 1] - Trunkcontur_Positioned[0, 1]) * scale_factor_2 + (H252 + H297_2)

    scaled_contur = np.hstack((scaled_contur, np.expand_dims(scaled_contur_y, axis=1)))

    # new length due to scaled trunkdata - rear end shows deviations due to loading edge, ...
    if max(scaled_contur[:, 0]) > scaled_contur[len(scaled_contur)-1, 0] + 5:
        L209_2 = scaled_contur[len(scaled_contur)-1, 0] - EX_luggage_start_front_axle
    # endregion

    # region [8]: Compute the area under the rear seats
    # Area of the triangular underneath the rear seat (XZ-plane)
    if max(scaled_contur[:, 1]) > scaled_contur[0, 1] + 5:
        # Get intersect between rear seat 2nd row and horizontal line of first point of trunkcontur

        # 1st: horizontal line equals trunk floor
        c1 = scaled_contur[0, 1]
        # 2nd: rear seat line with the lower & upper point
        m2 = H297_2 / (EX_luggage_top_start_front_axle - EX_luggage_start_front_axle)
        c2 = H252 - m2 * EX_luggage_start_front_axle

        x_section = (c2 - c1) / (0 - m2)
        z_section = c1

        # compute the "triangular area" as the real triangle and the small area between the triangle and the volume
        # under the trunkcontur [2]
        area_triang = 0.5 * (x_section - EX_luggage_start_front_axle) * (z_section - H252) + \
                      (EX_luggage_top_start_front_axle - x_section) * (z_section - H252)

    else:
        area_triang = 0.5 * (EX_luggage_top_start_front_axle - EX_luggage_start_front_axle) * H297_2
    # endregion

    # region [9]: Compute the volume of the trunk underneath the real Contur
    # Area underneath the trunkform from a2mac1
    x_axis = np.array(scaled_contur[:, 0])

    y_values = np.array(scaled_contur[:, 1])

    #  area from the trunkform till the road complete but only trunk needed
    area_under_trunkform_complete = np.trapz(y_values, x_axis)

    #  area which is under the trunkfloor till the road which is not needed
    area_under_trunkform_not_needed = (np.max(scaled_contur[:, 0]) - np.min(scaled_contur[:, 0])) * scaled_contur[-1, 1]

    area_under_trunkform = area_under_trunkform_complete - area_under_trunkform_not_needed

    # total area new design with correct trunkform
    area_complete = area_triang + area_under_trunkform

    # Calculate the volume (complete with real trunkform) in l
    volume_complete = area_complete * W201 * 2 / 1e6
    # endregion

    # region [10]: Assign the Outputs
    setattr(vehicle.dimensions.EX, 'EX_luggage_start_front_axle', EX_luggage_start_front_axle)
    setattr(vehicle.dimensions.EX, 'EX_luggage_end_front_axle', EX_luggage_end_front_axle)
    setattr(vehicle.dimensions.EX, 'EX_luggage_top_start_front_axle', EX_luggage_top_start_front_axle)
    setattr(vehicle.dimensions.EX, 'L209_2', L209_2)  # length of the trunk

    setattr(vehicle.dimensions.EY, 'W201', W201*2)  # width of the trunk

    setattr(vehicle.dimensions.EZ, 'H252', H252)
    setattr(vehicle.dimensions.EZ, 'H297_2', H297_2)  # height of the trunk

    setattr(vehicle.dimensions, 'volume_trunk', volume_complete)  # height of the trunk

    return vehicle, parameters
    # endregion
