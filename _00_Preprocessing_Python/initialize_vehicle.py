"""
Description: This function initializes the vehicle class and the Parameter struct. The
             given Input from the Excel-table are assigned to the vehicle class.
             Then the e-machine and the battery cells will be assigned
------------
Sources:  (1) SAE J1100, https://www.sae.org/standards/content/j1100_200911/
------------
Input: vehicle: Stores the calculated component volumes and masses
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: Updated vehicle class with the initialized dimensions, e-machine and battery class
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialize Inputs
[2] Initialize the drive topology
[3] Initialize the vehicles weight
[4] Initialize the e-machine for both axles
[5] Initialize the battery
[6] Initialize wheels
[7] Initialize the driving cycle
"""

# region [0] Import all necessary modules, classes and methods
# Import methods
from .Initialize_functions.initialize_inputs import initialize_inputs
from .Initialize_functions.initialize_topology import initialize_topology
from .Initialize_functions.initialize_weight_options import initialize_weight_options
from .Initialize_functions.initialize_e_machine import initialize_e_machine
from .Initialize_functions.initialize_battery import initialize_battery
from .Initialize_functions.initialize_wheels import initialize_wheels
from .Initialize_functions.initialize_LDS_parameters import initialize_LDS_parameters
# endregion


def initialize_vehicle(vehicle, parameters):

    # region [1] Initialize Inputs
    vehicle = initialize_inputs(vehicle)
    # endregion

    # region [2] Initialize the drive topology
    vehicle, parameters = initialize_topology(vehicle, parameters)
    # endregion

    # region [3] Initialize the vehicles weight
    vehicle, parameters = initialize_weight_options(vehicle, parameters)
    # endregion

    # region [4] Initialize the e-machine for both axles
    vehicle, parameters = initialize_e_machine(vehicle, parameters)
    # endregion

    # region [5] Initialize the battery
    vehicle = initialize_battery(vehicle, parameters)
    # endregion

    # region [6] Initialize wheels
    vehicle = initialize_wheels(vehicle, parameters)
    # endregion

    # region [7] Initialize the driving cycle
    vehicle, parameters = initialize_LDS_parameters(vehicle, parameters)
    # endregion

    return vehicle
