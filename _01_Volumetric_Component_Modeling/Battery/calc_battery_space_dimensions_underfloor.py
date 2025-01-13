"""
Description:  This function calculates the available space in the underfloor. The definition of the underfloor can
              be found at (3, p.52-57 & 4). The function calculates the maximum available installation space of the
              underfloor to be filled with battery cells.
              This function is a combination of the methodes described by (1, p.38-43) and (3, p.52-57).
              The constraints in X-Direction of the vehicle are described in (1) whereas the constraints in Y- and Z-
              Direction are in (3 & 4)

------------
Sources:  (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", P. D. Thesis, Technical University of Munich, Institute of Automotive Technology, 2022
          (2) P. Köhler, „Semi-physikalische Modellierung von Antriebsstrangkomponenten für Elektrofahrzeuge,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021
          (3) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
          (4) Rosenberger et al., "Scientific benchmarking: Engineering quality evaluation of electric vehicle concepts", e-Prime - Advances in Electrical Engineering, Electronics and Energy 9, 2024
------------
Input: vehicle: Class element, which stores all values of the vehicle
       parameters: Class element, which stores all necessary computation parameters
------------
Output: The dimensions of the available space in the underbody of the vehicle
        including - if assigned - the dimensions of the small overlap part of the battery
------------
Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Derive the space constraints for the battery along the X direction for the front axle
[3] Derive the space constraints for the battery along the X direction for the rear axle
[4] Calculate battery width
[5] Calculate battery height
[6] Calculate battery length
[7] Derive the small overlap space
[8] Assign Outputs
------------
"""

# region [0] import modules, classes and functions
# import modules
import numpy as np
import math
# import functions

# endregion


def calc_battery_space_dimensions_underfloor(vehicle, parameters):
    # region [1] Assign Inputs
    wheelbase = vehicle.dimensions.GX.wheelbase
    Padim = parameters.dimensions
    CZ_battery_cell = vehicle.dimensions.CZ.CZ_batt_underfloor

    GZ_H156 = vehicle.dimensions.GZ.H156                       # Groundclearance in mm
    bottom_cover = vehicle.dimensions.CZ.batt_bottom_cover     # Thickness of the battery bottom cover along the Z direction in mm (2, p. 76)

    # Get the position parameter of the battery cells width
    design_approach = vehicle.Input.design_approach            # Get the design approach of the vehicle (3, p.53-54 & 4)
    battery_position_in_y = vehicle.battery.position_in_y      # Referenced to the position of the rear wheels (3, p.53-54 & 4)
    vehicle_width = vehicle.dimensions.GY.vehicle_width        # Get the vehicle width
    tire_width = vehicle.dimensions.CY.wheel_r_width           # Get the tire width at the rear axle

    # Get the spacetable of the battery
    spacetable = vehicle.battery.spacetable
    # endregion

    # region [2] Derive the space constraints for the battery along the X direction for the front axle
    # For more information regarding the battery_topology see Chapter 2.2.2 of (1)
    if vehicle.topology.battery_topology.lower() == 'mixedfloor':
        # Mixed floor battery. The maximum batt is influenced by the position of the driver's AHP
        AHP_X = vehicle.manikin.AHP_X_front_axle       # Position of the AHP of the driver in mm
        EX_AHP_batt = Padim.EX.AHP_battery             # Length of the driver's footwell in mm
        EX_battery_front_axle_min = AHP_X+EX_AHP_batt  # Minimum distance between battery and front axle

    else:   # The battery is a lowfloor or highfloor topology
        if vehicle.topology.filled_axles['front']:     # -> there is a machine at the front axle
            critical_pos_e_machine = vehicle.e_machine['front'].EX_machine + vehicle.e_machine['front'].CX_e_machine_diameter/2
            critical_pos_gearbox = np.amax(vehicle.gearbox['front'].position.EX_gearbox_housing)
            critical_pos_drive_unit_f = max(critical_pos_e_machine, critical_pos_gearbox)
            EX_battery_front_axle_min = Padim.EX.battery_drive_unit_f + critical_pos_drive_unit_f
        else:
            EX_battery_front_axle_min = Padim.EX.battery_drive_unit_f
    # endregion

    # region [3] Derive the space constraints for the battery along the X direction for the rear axle
    if vehicle.topology.filled_axles['rear']:     # -> there is a machine at the rear axle
        critical_pos_e_machine = vehicle.e_machine['rear'].EX_machine - vehicle.e_machine['rear'].CX_e_machine_diameter/2
        critical_pos_gearbox = np.amin(vehicle.gearbox['rear'].position.EX_gearbox_housing)
        critical_pos_drive_unit_r = wheelbase-min(critical_pos_e_machine, critical_pos_gearbox)
        EX_battery_rear_axle_min = Padim.EX.battery_drive_unit_r+critical_pos_drive_unit_r
    else:
        EX_battery_rear_axle_min = Padim.EX.battery_drive_unit_r
    # endregion

    # region [4] Calculate battery width
    # This is done by an estimated correction factor: the factor is calculated with the following formula:
    # correction_factor = (vehicle_width,real - battery_width,real)/ (2 * tire_width) (3, p.53-54 & 4)
    if design_approach.lower() == 'purpose':
        match battery_position_in_y:
            case 1:
                correction_factor = parameters.dimensions.EY.battery_width_factor.purpose_large
            case 0:
                correction_factor = parameters.dimensions.EY.battery_width_factor.purpose_medium
            case -1:
                correction_factor = parameters.dimensions.EY.battery_width_factor.purpose_small
            case _:
                raise Exception("No valid entry for battery width factor: Only '1', '0' or '-1' are possible")
    elif design_approach.lower() == 'conversion':
        correction_factor = parameters.dimensions.EY.battery_width_factor.conversion
    else:
        raise Exception("The design approach is invalid. Only 'Purpose' or 'Conversion' are possible")

    CY_batt_underfloor = vehicle_width - correction_factor * 2 * tire_width
    # endregion

    # region [5] Calculate battery height
    # Internal dimensional chain to derive effective cell space (space for exactly one battery cell in Z-direction, 3. 55 & 4)
    CZ_batt_underfloor = CZ_battery_cell
    # endregion

    # region [6] Calculate battery length
    # Find the X position, where the battery width is costrained by the small overlap requirements (1, p.40-41)
    EX_battery_max_width_front_axle, limit_line_small_ov = calc_small_overlap_limit(vehicle, parameters, CY_batt_underfloor)

    # Derive corresponding distance from front axle. Consider constraints
    # imposed by electric machine and small overlap and take the worst
    EX_battery_front_axle_underfloor_space = max(EX_battery_max_width_front_axle, EX_battery_front_axle_min)

    # Resulting MAXIMUM battery length in mm
    CX_batt_underfloor = wheelbase-EX_battery_rear_axle_min-EX_battery_front_axle_underfloor_space

    # Make sure that the calculated spaces are bigger than zero, otherwise set zero:
    CX_batt_underfloor = max(CX_batt_underfloor, 0)
    CY_batt_underfloor = max(CY_batt_underfloor, 0)
    CZ_batt_underfloor = max(CZ_batt_underfloor, 0)
    # endregion

    # region [7] Derive the small overlap space
    if vehicle.settings.fill_smalloverlapspace == 1:     # The vehicle has a filled smalloverlap at the front (1, p. 40-41)
        # get size of the limit matrix
        size_limit = np.shape(limit_line_small_ov)[1]

        # Find the Y coordinate of limit small overlap, that comes the closer to the battery width
        # -> Retrieve the position of this coordinate in the vector
        id_batt = np.argmin(np.absolute(limit_line_small_ov[1, :] - CY_batt_underfloor/2))

        # Filter out the Y coordinate which are larger than half of the battery width
        limit_line_small_ov = np.delete(limit_line_small_ov, np.arange(id_batt+1, size_limit), axis=1)

        # Filter out the X coordinates which are smaller than the minimum axle distance
        check_x = np.where(limit_line_small_ov[0, :] < EX_battery_front_axle_min)[0]
        if np.shape(check_x) != 0:
            limit_line_small_ov = np.delete(limit_line_small_ov, check_x, axis=1)
        # limit_line_small_ov(find((limit_line_small_ov(:,1)<EX_battery_front_axle_min)),:)=[];
        if np.shape(limit_line_small_ov)[1] == 0:
            # Fill errorlog list
            errorlog_list = vehicle.errorlog
            text_errorlog = 'There is no cell fitting in the small overlap area: The option will be deactivated'
            print(text_errorlog)
            errorlog_list.append(text_errorlog)
            setattr(vehicle, 'errorlog', errorlog_list)

            # Set small overlap areas to zeros
            CY_batt_small_overlap = 0
            CX_batt_small_overlap = 0
            CZ_batt_small_overlap = 0
            EX_batt_small_overlap = np.zeros(1)  # Necessary as numpy array for the definition of the spacetable in line 183

            #  deactivate small overlap
            setattr(vehicle.settings, 'fill_smalloverlapspace', 0)
        else:
            # The corresponding relevant part of the small overlap limit is limit_line_small_ov(id_batt:end,:)
            EX_batt_small_overlap = limit_line_small_ov[0, :]                           # X Coordinates of the limiting line for the battery in the small overlap area
            CY_batt_small_overlap = limit_line_small_ov[1, :] * 2                       # Corresponding Y coordinates of the limiting line -> The battery width
            CX_batt_small_overlap = EX_batt_small_overlap - EX_battery_front_axle_min   # Length of the small overlap section
            CZ_batt_small_overlap = CZ_batt_underfloor * np.ones(np.size(CX_batt_small_overlap))

    else:
        # No small overlap battery area. Set the small overlap dimensions to 0
        CX_batt_small_overlap = 0
        CY_batt_small_overlap = 0
        CZ_batt_small_overlap = 0
        EX_batt_small_overlap = np.zeros(1)  # Necessary as numpy array for the definition of the spacetable in line 183
    # endregion

    # region [8] Assign Outputs
    # Dimensions and position small overlap
    setattr(vehicle.battery.installationspace, 'CX_batt_underfloor', CX_batt_underfloor)
    setattr(vehicle.battery.installationspace, 'EX_batt_underfloor', EX_battery_front_axle_underfloor_space)
    setattr(vehicle.battery.installationspace, 'CX_batt_small_overlap', CX_batt_small_overlap)
    setattr(vehicle.battery.installationspace, 'CY_batt_small_overlap', CY_batt_small_overlap)
    setattr(vehicle.battery.installationspace, 'CZ_batt_small_overlap', CZ_batt_small_overlap)
    setattr(vehicle.battery.installationspace, 'EX_batt_small_overlap_front_axle', EX_battery_front_axle_underfloor_space)
    setattr(vehicle.battery.installationspace, 'EX_batt_small_overlap_discretized', EX_batt_small_overlap)

    # Battery dimensional chain in X (in mm)
    # Minimum distance between the total battery (small overlap and underfloor) and the front axle
    setattr(vehicle.dimensions.EX, 'battery_front_axle_min', EX_battery_front_axle_min)

    # Store the underfloor dimensions
    underfloor_spacetable = np.array([CX_batt_underfloor, CY_batt_underfloor, CZ_batt_underfloor,
                                      EX_battery_front_axle_underfloor_space, GZ_H156 + bottom_cover])
    spacetable['underfloor'] = underfloor_spacetable

    # Store the small overlap dimensions
    # Ensure that CX, CY, and CZ do not take negative values
    CX_batt_small_overlap = np.maximum(np.amax(CX_batt_small_overlap), 0)
    CY_batt_small_overlap = np.maximum(np.amin(CY_batt_small_overlap), 0)
    CZ_batt_small_overlap = np.maximum(np.amax(CZ_batt_small_overlap), 0)
    small_overlap_spacetable = np.array([CX_batt_small_overlap, CY_batt_small_overlap, CZ_batt_small_overlap,
                                         EX_batt_small_overlap[0], GZ_H156 + bottom_cover])
    spacetable['small_overlap'] = small_overlap_spacetable

    # Assign in the spacetable
    setattr(vehicle.battery, 'spacetable', spacetable)
    # endregion
    return vehicle


def calc_small_overlap_limit(vehicle, parameters, CY_batt_underfloor):
    """"
    Description:
    This function ensure that, depending on the battery width, the battery is
    always position so, that the minimum distance between battery and
    wheelhouse in X direction is always higher than the minimum value Par.dimensions.EX.wheelhouse_f_battery
    Fore a more detailed description, check (1, section 3.4.5)

    Output:
    EX_battery_max_width_front_axle: The position in X direction, where the battery cannot keep its maximum width
                                     and has to change to a small overlap shape
    limit_line_small_ov: The discretized small overlap shape of the battery as vector
                         with the X (first column) and y (second column) coordinates
    """

    # region Implementation:
    # Load point cloud of the wheelhouse
    wheelhouse = vehicle.wheels.wheelhouse_f

    # The minimum distance which has to be kept between battery and wheelhouse in mm
    EXY_wheelhouse_f_battery = parameters.dimensions.EX.wheelhouse_f_battery

    # Include only the point with different y_coordinates (otherwise interp1 won't work)
    wheelhouse_y_all = wheelhouse[1, :]
    wheelhouse_y_unique, idx = np.unique(wheelhouse_y_all, return_index=True)

    # Retrieve the corresponding x coordinates
    x = wheelhouse[0, idx]

    # The discretized battery limit (required for the small overlap space)
    limit_line_small_ov = np.row_stack((x, wheelhouse_y_unique))

    # Generate the small overlap limit for the battery by shifting the wheelhouse line by EXY_wheelhouse_f_battery
    limit_line_small_ov[0, :] = limit_line_small_ov[0, :] + EXY_wheelhouse_f_battery/math.sqrt(2)
    limit_line_small_ov[1, :] = limit_line_small_ov[1, :] - EXY_wheelhouse_f_battery/math.sqrt(2)

    y_target_value = CY_batt_underfloor * 0.5
    if y_target_value < np.amin(wheelhouse_y_unique):
        # The battery is so thin, that it fits through the wheelhouses -> No small overlap safety required
        EX_battery_max_width_front_axle = 0

    else:
        # The battery is so wide, that it could collide with the wheelhouse. Set the EX to avoid this
        y_interp = limit_line_small_ov[1, :]
        x_interp = limit_line_small_ov[0, :]
        EX_battery_max_width_front_axle = np.interp(y_target_value, y_interp, x_interp)

    return EX_battery_max_width_front_axle, limit_line_small_ov
