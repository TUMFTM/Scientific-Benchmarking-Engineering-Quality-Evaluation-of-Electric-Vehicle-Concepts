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
Output:  Object element for a machine
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialize all the elements and imports
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import numpy as np
# Import classes
# Import methods
from Planetary.calc_gearbox_position_planetary import calc_gearbox_position_planetary
from Lay_shaft.calc_gearbox_position_layshaft import calc_gearbox_position_layshaft
# endregion


def calc_gearbox_position_Main(gearbox, parameters, key, wheelbase, tire_diameter, gear_orientation, CY_e_machine_length):
    # region [1]: Initialize all the elements and imports
    CX_wheel = np.zeros(2)
    CX_wheel[0] = tire_diameter                      # Wheel diameter at the front axle
    CX_wheel[1] = tire_diameter                      # Wheel diameter at the rear axle

    # Ensure that the user assigned a correct value. Otherwise the gearbox will be positioned wrong (and the e-machine as well)
    if gear_orientation['position'].lower() == 'front' or gear_orientation['position'].lower() == 'coaxial' \
            or gear_orientation['position'].lower() == 'rear':
        pass
    else:
        # v = errorlog(v, 'THE CHOSEN MACHINE DOCUMENTATION IS WRONG! THE POSSIBLE OPTIONS ARE 'front', 'coaxial' or 'rear'', 1);
        return

    # Define the numerical axle identifier to use it in case of array indexing
    if key.lower() == 'front':
        axle_id = 0
    elif key.lower() == 'rear':
        axle_id = 1
    else:
        return

    if gearbox.Input.type.lower() == 'planetary':
        gearbox = calc_gearbox_position_planetary(gearbox, parameters, axle_id, wheelbase, CX_wheel, CY_e_machine_length)
    elif gearbox.Input.type.lower() == 'lay-shaft':
        gearbox = calc_gearbox_position_layshaft(gearbox, parameters, axle_id, gear_orientation, wheelbase, CX_wheel, CY_e_machine_length)
    else:
        return
    print('War erfolgreich')
