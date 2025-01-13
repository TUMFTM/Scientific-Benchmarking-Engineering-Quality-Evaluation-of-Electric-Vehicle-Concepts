"""
Description:    This function positions the gearbox with parallel axles according to the
                calculated gearbox dimensions and the chosen topology. The position of
                the gearbox is furthermore required to position the electric machine (see
                function calc_EM_position)
------------
Sources:    None
------------
Input:   vehicle: Class element which stores all the vehicle information
         parameters: Class element which stores all necessary computation parameters
         key: Switch between the front and the rear axle
------------
Output:  Gearbox Class element where the relativ position of the gearbox is stored
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialize all the elements and imports
[2] Compute the position of the gearbox
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import numpy as np
# Import classes
# Import methods
from .Planetary import calc_gearbox_position_planetary
from .Lay_shaft import calc_gearbox_position_layshaft
# endregion


def calc_gearbox_position(vehicle, parameters, key):
    # region [1]: Initialize all the elements and imports
    wheelbase = vehicle.dimensions.GX.wheelbase             # Wheelbase of the vehicle in mm
    CX_wheel = np.zeros(2)
    CX_wheel[0] = vehicle.dimensions.CX.wheel_f_diameter    # Wheel diameter at the front axle
    CX_wheel[1] = vehicle.dimensions.CX.wheel_r_diameter    # Wheel diameter at the rear axle

    # Length of the e_machine
    CY_e_machine_length = vehicle.e_machine[key].CY_e_machine_length

    # Gearbox orientation Dictionary with position and ID ('front', 'coaxial', 'rear')
    gear_orientation = vehicle.gearbox[key].Input.gear_orientation

    # Ensure that the user assigned a correct value. Otherwise the gearbox will be positioned wrong (and the e-machine as well)
    if gear_orientation['position'].lower() == 'front'\
            or gear_orientation['position'].lower() == 'coaxial' or gear_orientation['position'].lower() == 'rear':
        pass
    else:
        raise Exception('THE CHOSEN MACHINE DOCUMENTATION IS WRONG! THE POSSIBLE OPTIONS ARE \'front\', \'coaxial\' or \'rear\'')

    # Define the numerical axle identifier to use it in case of array indexing
    if key.lower() == 'front':
        axle_id = 0
    elif key.lower() == 'rear':
        axle_id = 1
    else:
        raise Exception("THE IDENTIFICATION KEYS FOR THE GEARBOX ARE NOT VALID. OPTIONS ARE \'front\' and \'rear\'")
    # endregion

    # region [2]: Compute the position of the gearbox
    # Extract the gearbox class from the vehicle class
    gearbox = vehicle.gearbox[key]

    if gearbox.Input.type.lower() == 'planetary':
        # Compute position of a planetary gearbox
        gearbox = calc_gearbox_position_planetary(gearbox, parameters, axle_id, wheelbase, CX_wheel, CY_e_machine_length)

    elif gearbox.Input.type.lower() == 'lay-shaft':
        # Compute the position of  a lay-shaft gearbox
        gearbox = calc_gearbox_position_layshaft(gearbox, parameters, axle_id, gear_orientation, wheelbase, CX_wheel, CY_e_machine_length)

    else:
        raise Exception("THE GEARBOX TYPE IS NOT VALID. OPTIONS ARE \'planetary\' and \'lay-shaft\'")
    # endregion
    return gearbox
