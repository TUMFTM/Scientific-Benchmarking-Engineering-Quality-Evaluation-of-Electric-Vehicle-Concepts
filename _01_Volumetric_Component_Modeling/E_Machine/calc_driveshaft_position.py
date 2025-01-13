"""
Description: This function positions the driveshafts according to the position of the
             electric machine and the position of the differential.
------------
Sources: None
------------
Input: vehicle: Class element, which stores all values of the vehicle
       key: Key describing the concerned axles (front or rear)
------------
Output: The position of the driveshaft (expressed in the reference system of the vehicle)
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Calculate position of the side shafts
[3] Assign Output
------------
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
# endregion


def calc_driveshaft_position(vehicle, key):
    # region [1] Assign Inputs
    EY_driveshaft_gearbox_side = np.zeros(2)
    CY_wheel = np.zeros(2)
    CX_wheel = np.zeros(2)

    gearbox = vehicle.gearbox[key]
    wheelbase = vehicle.dimensions.GX.wheelbase             # in mm
    width = vehicle.dimensions.GY.vehicle_width             # vehicle width in mm
    CY_wheel[0] = vehicle.dimensions.CY.wheel_f_width       # Front wheel width in mm
    CY_wheel[1] = vehicle.dimensions.CY.wheel_r_width       # Rear wheel width in mm
    CX_wheel[0] = vehicle.dimensions.CX.wheel_f_diameter    # Front wheel diameter in mm
    CX_wheel[1] = vehicle.dimensions.CX.wheel_r_diameter    # Rear wheel diameter in mm

    if key.lower() == 'front':
        axle_id = 0
    elif key.lower() == 'rear':
        axle_id = 1
    else:
        raise Exception("The vehicle must have at least one filled axle")
    # endregion

    # region [2] Calculate position of the side shafts

    # Calculate the distance from the front axle in X direction
    EX_driveshaft = wheelbase * axle_id

    # Calculate the diameter of the shaft
    CX_driveshaft = gearbox.shafts.d_sh_3

    # Calculate the position in Y direction of the shaft connection with the wheels
    EY_driveshaft_wheel_side = (width-CY_wheel[axle_id]) * 0.5

    # Calculate the position in Y direction of the shaft connection with the gearbox
    EY_driveshaft_gearbox_side[0] = gearbox.position.EY_gearbox_housing[1]

    # Calculate the distance from the front axle in Z direction
    EZ_driveshaft = CX_wheel[axle_id] * 0.5

    # Calculate the Y position of the second shaft (the one on the left side)
    if vehicle.e_machine[key].quantity == 1:     # Only one machine at the selected axle
        EY_driveshaft_gearbox_side[1] = gearbox.position.EY_gearbox_housing[0]

    else:   # Two machines at the selected axle
        EY_driveshaft_gearbox_side[1] = -EY_driveshaft_gearbox_side[0]
    # endregion

    # region [3] Assign Output
    setattr(gearbox.driveshaft, 'EX_driveshaft', EX_driveshaft)
    setattr(gearbox.driveshaft, 'CX_driveshaft', CX_driveshaft)
    setattr(gearbox.driveshaft, 'EY_driveshaft_wheel_side', EY_driveshaft_wheel_side)
    setattr(gearbox.driveshaft, 'EY_driveshaft_gearbox_side', EY_driveshaft_gearbox_side)
    setattr(gearbox.driveshaft, 'EZ_driveshaft', EZ_driveshaft)
    # endregion

    return gearbox
