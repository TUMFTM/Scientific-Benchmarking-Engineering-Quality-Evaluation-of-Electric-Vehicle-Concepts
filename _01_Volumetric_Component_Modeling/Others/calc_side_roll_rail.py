"""
Description: In a first step this function assigns the Y and Z dimensions of the side roll rail and the
             Crash Management System (CMS). These values are constant values which were calculated from an
             evaluation of empirical data by Nicoletti

             In a second step the side roll rails will be positioned in Y and Z direction.
             The Y position is estimated according to the width of the wheelhouse.
             For the Z position the function ensures that (if there is a motor on the front axle) no collision
             between side roll rail and drive shaft occurs.
             In the case of the side roll rail at the rear axle, the position is determined based on
             the position of the rear damper (and not based on the width of the wheelhouse)
------------
Sources: (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", Technical University of Munich, Institute of Automotive Technology, 2022
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The dimensions and position of the side roll rail and the Crash management system
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Set dimensions of the side roll rail
[3] Determine Z position of side roll rail
[4] Determine Y position of side roll rail
[5] Determine X position of side roll rail
[6] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
# endregion


def calc_side_roll_rail(vehicle):
    # region [1] Assign Inputs
    machine_axle_f = vehicle.topology.filled_axles['front']     # Is there a machine at the front axle? (True or False)
    machine_axle_r = vehicle.topology.filled_axles['rear']      # Is there a machine at the rear axle? (True or False)

    # Wheel dimensions and vehicle width and wheelbase
    CX_wheel_f = vehicle.dimensions.CX.wheel_f_diameter         # Diameter of the front wheel in mm
    CX_wheel_r = vehicle.dimensions.CX.wheel_r_diameter         # Diameter of the rear wheel in mm
    width = vehicle.dimensions.GY.vehicle_width                 # Vehicle width in mm
    wheelbase = vehicle.dimensions.GX.wheelbase                 # Wheelbase in mm

    # Further dimensions for the positioning of the front side roll rail
    EY_wheelhouse_f = vehicle.dimensions.CY.wheelhouse_f_width      # Wheelhouse width at the front axle in mm

    # Further dimensions for the positioning of the front side roll rail
    low_sa_y = vehicle.dimensions.EY.lower_point_shock_absorber_vehicle_center  # Distance between vehicle centre and lowest point of the damper along the Y direction in mm
    piston_diameter = vehicle.dimensions.CX.piston_diameter                     # Diameter of the damper in mm
    # endregion

    # region [2] Set dimensions of the side roll rail
    # Set the Z and Y dimensions of the front Crash Management System (CMS) and side roll rail
    CY_side_roll_rail_f = 70                    # in mm
    CZ_side_roll_rail_f = 120                   # in mm
    CY_CMS_f = 74                               # in mm
    CZ_CMS_f = 102                              # in mm

    # Set the Z and Y dimensions of the rear CMS and side roll rail. Assumed to be equal as the ones at the front axle
    CZ_side_roll_rail_r = CZ_side_roll_rail_f   # in mm
    CY_side_roll_rail_r = CY_side_roll_rail_f   # in mm
    CY_CMS_r = CY_CMS_f                         # in mm
    CZ_CMS_r = CZ_CMS_f                         # in mm
    # endregion

    # region [3] Determine Z position of side roll rail
    # If there is a front machine, consider the space required by the driveshaft when positioning the side roll rail
    if machine_axle_f:
        # Retrieve the diameter of the driveshaft (in mm)
        CX_driveshaft = vehicle.gearbox['front'].driveshaft.CX_driveshaft

        # Ensure that the side roll rail has a minimum distance of 20 mm form the driveshaft
        EZ_side_roll_rail_f = (CX_wheel_f + CX_driveshaft) * 0.5 + 20
    else:
        # There is no machine on the front axle. Position the side roll rail at the same height as the front axle
        EZ_side_roll_rail_f = CX_wheel_f * 0.5

    # If there is a rear machine, consider the space required by the driveshaft when positioning the side roll rail
    if machine_axle_r:
        # Retrieve the diameter of the driveshaft (in mm)
        CX_driveshaft = vehicle.gearbox['rear'].driveshaft.CX_driveshaft

        # Ensure that the side roll rail has a minimum distance of 20 mm form the driveshaft
        EZ_side_roll_rail_r = (CX_wheel_r + CX_driveshaft) * 0.5 + 20
    else:
        # There is no machine on the front axle. Position the side roll rail at the same height as the front axle
        EZ_side_roll_rail_r = CX_wheel_r * 0.5
    # endregion

    # region [4] Determine Y position of side roll rail
    # Front Axle: --> Assumption: The side roll rail is placed in contact with the front wheelhouse
    EY_side_roll_rail_f = width * 0.5 - EY_wheelhouse_f - CY_side_roll_rail_f

    # Rear Axle: --> Assumption: The side roll rail is placed 20 mm away from the lowest point of the damper
    EY_side_roll_rail_r = low_sa_y - piston_diameter * 0.5 - 20
    # endregion

    # region [5] Determine X position of side roll rail
    EX_side_roll_rail_r = wheelbase     # Assume that it starts at the center of the rear wheel in mm
    EX_side_roll_rail_f = 0             # Assume that it starts at the center of the front wheel in mm
    # endregion

    # region [6] Assign Outputs
    # Assign side roll rail Dimensions (All dimensions are expressed in mm)
    setattr(vehicle.dimensions.CY, 'side_roll_rail_f', CY_side_roll_rail_f)
    setattr(vehicle.dimensions.CZ, 'side_roll_rail_f', CZ_side_roll_rail_f)
    setattr(vehicle.dimensions.CY, 'CMS_f', CY_CMS_f)
    setattr(vehicle.dimensions.CZ, 'CMS_f', CZ_CMS_f)

    setattr(vehicle.dimensions.CZ, 'side_roll_rail_r', CZ_side_roll_rail_r)
    setattr(vehicle.dimensions.CY, 'side_roll_rail_r', CY_side_roll_rail_r)
    setattr(vehicle.dimensions.CY, 'CMS_r', CY_CMS_r)
    setattr(vehicle.dimensions.CZ, 'CMS_r', CZ_CMS_r)

    # Assign side roll rail position (All dimensions are expressed in mm)
    setattr(vehicle.dimensions.EX, 'side_roll_rail_r', EX_side_roll_rail_r)
    setattr(vehicle.dimensions.EY, 'side_roll_rail_r_vehicle_centre', EY_side_roll_rail_r)
    setattr(vehicle.dimensions.EZ, 'side_roll_rail_r', EZ_side_roll_rail_r)
    setattr(vehicle.dimensions.EX, 'side_roll_rail_f', EX_side_roll_rail_f)
    setattr(vehicle.dimensions.EY, 'side_roll_rail_f_vehicle_centre', EY_side_roll_rail_f)
    setattr(vehicle.dimensions.EZ, 'side_roll_rail_f', EZ_side_roll_rail_f)
    # endregion

    return vehicle
