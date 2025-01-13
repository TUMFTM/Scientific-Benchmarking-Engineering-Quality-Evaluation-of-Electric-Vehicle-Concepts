"""
Description: This function positions the electric machine according to the chosen topology, and the calculated
             gearbox dimensions. To position the machine, the function uses the results from the gearbox positioning
             (see function calc_gearbox_position)
------------
Sources: None
------------
Input: e_machine: Class element, which stores all the necessary e-machine information
       gearbox: Class element, which stores all the gearbox information
------------
Output: The position of the E-Machine (expressed in the reference system of the vehicle)
------------

Implementation
[0] Import modules, classes and functions
[1] Calc E-Machine position
[2] Assign Output
------------
"""

# region [0] Import modules, classes and functions
# endregion

def calc_EM_position(e_machine, gearbox):
    # region [1] Calc E-Machine position
    EX_machine = gearbox.position.EX_shaft_1_front_axle
    EY_machine = gearbox.position.EY_gearbox_housing[0]
    EZ_machine = gearbox.position.EZ_shaft_1_front_axle
    # endregion

    # region [2] Assign Outputs
    setattr(e_machine, 'EX_machine', EX_machine)
    setattr(e_machine, 'EY_machine', EY_machine)
    setattr(e_machine, 'EZ_machine', EZ_machine)
    # endregion

    return e_machine
