"""
Description: This function calculates the dimensions of shock absorbers, coils, wheels and wheelhouses.
------------
Sources: (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", Technical University of Munich, Institute of Automotive Technology, 2022
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The vehicle structure updated with the mass and package information
------------

Implementation
[0] Import modules, classes and functions
[1] Calculate the dimensions of the front wheelhouse, considering the required steering angle
[2] Calculate the dimensions of the rear wheelhouse, considering the axis kinematics
[3] Calculate the dimensions of the shock absorber at the rear axle
[4] Position the shock absorber
[5] Calculate coaxial spring layout
------------
"""

# region [0] Import modules, classes and functions
# Import functions
from .calc_wheelhouse_front_dimensions import calc_wheelhouse_front_dimensions
from .calc_wheelhouse_rear_dimensions import calc_wheelhouse_rear_dimensions
from .calc_shock_absorber_dimensions import calc_shock_absorber_dimensions
from .calc_shock_absorber_position import calc_shock_absorber_position
from .calc_pneumatic_spring_coaxial import calc_pneumatic_spring_coaxial
# Import modules
import numpy as np
# endregion


def calc_chassis_dimensions(vehicle, parameters):

    # region [1] Calculate the dimensions of the front wheelhouse, considering the required steering angle
    vehicle, parameters = calc_wheelhouse_front_dimensions(vehicle, parameters)
    # endregion

    # region [2] Calculate the dimensions of the rear wheelhouse, considering the axis kinematics
    vehicle, parameters = calc_wheelhouse_rear_dimensions(vehicle, parameters)
    # endregion

    # region [3] Calculate the dimensions of the shock absorber at the rear axle
    # (required for the definition of the luggage compartment space)
    vehicle, parameters = calc_shock_absorber_dimensions(vehicle, parameters)
    # endregion

    # region [4] Position the shock absorber
    vehicle, parameters = calc_shock_absorber_position(vehicle, parameters)
    # endregion

    # region [5] Calculate coaxial spring layout
    # If there is a coaxial spring, the calculation has to be repeated!
    # Idea the spring depends from the position of the shock absorber and vice versa -> Iterative calculation required
    if vehicle.topology.spring_layout_r.lower() == 'coaxial':

        # Starting upper diameter of the shock absorber (should correspond to the diameter of the coaxial spring)
        upper_diameter = np.array([vehicle.dimensions.CX.upper_bearing_diameter_shock_absorber])
        delta = 1
        while delta > 0.1:

            # Calculate the required air spring diameter according to the shock absorber position
            vehicle, parameters = calc_pneumatic_spring_coaxial(vehicle, parameters)

            # Update the upper diameter -> corresponding to the air spring diameter
            upper_diameter_iter = vehicle.dimensions.CX.upper_bearing_diameter_shock_absorber
            upper_diameter = np.append(upper_diameter, upper_diameter_iter)

            # Since the shock absorber has a new diameter, it has to be repositioned to avoid collision with the wheelhouse
            vehicle, parameters = calc_shock_absorber_position(vehicle, parameters)

            # Difference between the air diameter and the diameter of the previous loop
            delta = abs(upper_diameter[-1] - upper_diameter[-2])
    # endregion
    return vehicle, parameters
