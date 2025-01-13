"""
Description: This function sizes and positions further components of exterior, frame, and interior
------------
Sources: (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", Technical University of Munich, Institute of Automotive Technology, 2022
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The vehicle structure updated with the position and dimensions of frame, interior, and exterior components
------------

Implementation
[0] Import modules, classes and functions
[1] Calc the frame form
[2] Calculate the dimension and position of the crossmembers at rear and front axle
[3] Calculate the dimension and position of the side roll rails at rear and front axle
[4] Calculate dimensions and position of front wall
[5] Calculate the position of the cooling system
------------
"""

# region [0] Import modules, classes and functions
# Import functions
from .calc_frame_form import calc_frame_form
from .calc_crossmember import calc_crossmember
from .calc_side_roll_rail import calc_side_roll_rail
from .calc_front_wall import calc_front_wall
from .calc_cooling_system import calc_cooling_system
# Import modules
# endregion


def calc_remaining_components(vehicle, parameters):
    # region [1] Calc the frame form
    # Discretized dimensions of the frame form of the vehicle -> Only for plot purposes
    vehicle = calc_frame_form(vehicle)
    # endregion

    # region [2] Calculate the dimension and position of the crossmembers at rear and front axle
    vehicle = calc_crossmember(vehicle)
    # endregion

    # region [3] Calculate the dimension and position of the side roll rails at rear and front axle
    vehicle = calc_side_roll_rail(vehicle)
    # endregion

    # region [4] Calculate dimensions and position of front wall
    vehicle = calc_front_wall(vehicle)
    # endregion

    # region [5] Calculate the position of the cooling system
    vehicle = calc_cooling_system(vehicle)
    # endregion

    return vehicle, parameters
