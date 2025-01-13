"""
Description: Aim of the function is to identify the case and calculate missing parameters
------------
Sources: More information regarding the implementation of the LDS functions is available at:
         (1) K. Moller, „Validierung einer MATLAB Längsdynamiksimulation für die Auslegung von Elektrofahrzeugen,“ Bachelor thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2020.
         (2) K. Moller, „Antriebsstrangmodellierung zur Optimierung autonomer Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: vehicle class with calculated missing values
------------

Implementation
[0] Import modules, classes and functions
[1] Assign the drag coefficient
[2] Load or calculate the c_r value
[3] Assign output
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
import math
# endregion


def calc_missing_inputs(vehicle, parameters):
    # region [1] Assign the drag coefficient
    # This function calculates the c_r value from Inputparameters --> see (2) for more information
    # load c_d
    if hasattr(vehicle.Input, 'c_d') and not np.isnan(vehicle.Input.c_d):

        c_d = vehicle.Input.c_d

    else:    # if c_d is no input, the value from Fixparameters will be chosen

        c_d = parameters.LDS.c_d

    # region [2] Load or calculate the c_r value
    if hasattr(vehicle.Input, 'c_r') and not np.isnan(vehicle.Input.c_r):  # User has given a c_r -> Use the User Input

        c_r = vehicle.Input.c_r

    elif hasattr(vehicle.dimensions.CX, 'wheel_f_diameter') and hasattr(vehicle.dimensions.CY, 'wheel_f_width'):
        # The tire are calculated and there is no user input -> Estimate c_r from tire size
        width_tires = [vehicle.dimensions.CY.wheel_f_width, vehicle.dimensions.CY.wheel_r_width]
        radius_tires = [vehicle.dimensions.CX.wheel_f_diameter/2, vehicle.dimensions.CX.wheel_r_diameter/2]
        width = max(width_tires)
        radius = max(radius_tires
                     )
        if width > 270:
            # If the width is to high, it will be set to 270 mm (see (2))
            width = 270
            # Define errorlog
            errorlog_list = vehicle.errorlog
            text_errorlog = 'Tire Width is out of boundary and is set to 270 mm (upper bound) for ' \
                            'rolling resistance coefficient calculation. Results could be distorted!'
            print(text_errorlog)
            errorlog_list.append(text_errorlog)
            setattr(vehicle, 'errorlog', errorlog_list)

        elif width < 125:
            # If the width is to low, it will be set to 270 mm (see (2))
            width = 125
            # Define errorlog
            errorlog_list = vehicle.errorlog
            text_errorlog = 'Tire Width is out of boundary and is set to 125 mm (lower bound) for ' \
                            'rolling resistance coefficient calculation. Results could be distorted!'
            print(text_errorlog)
            errorlog_list.append(text_errorlog)
            setattr(vehicle, 'errorlog', errorlog_list)

        if radius > 420:
            # If the radius is to high, it will be set to 420 mm (see (2))
            radius = 420

            # Define errorlog
            errorlog_list = vehicle.errorlog
            text_errorlog = 'Tire Radius is out of boundary and is set to 420 mm (upper bound) for ' \
                            'rolling resistance coefficient calculation. Results could be distorted!'
            print(text_errorlog)
            errorlog_list.append(text_errorlog)
            setattr(vehicle, 'errorlog', errorlog_list)

        elif radius < 250:
            # If the radius is to low, it will be set to 250 mm (see (2))
            radius = 250

            # Define errorlog
            errorlog_list = vehicle.errorlog
            text_errorlog = 'Tire Radius is out of boundary and is set to 250 mm (lower bound) for ' \
                            'rolling resistance coefficient calculation. Results could be distorted!'
            print(text_errorlog)
            errorlog_list.append(text_errorlog)
            setattr(vehicle, 'errorlog', errorlog_list)

        # Equation taken from (1) in kg/ton
        c_r = 0.034565063636242926 + width * (1.72623336 * math.pow(10, -4)) + radius * (-2.25929942 * math.pow(10, -4)) + \
              math.pow(width, 2) * (-3.21249605 * math.pow(10, -7)) + math.pow(radius, 2) * (2.59714227 * math.pow(10, -7))

    else:   # There is no user Input but the tire have not been calculated -> Use constant value (realistic value)
        c_r = parameters.LDS.c_r
    # endregion

    # region [3] Assign outputs
    setattr(vehicle.LDS.parameters, 'c_d', c_d)     # Assign the c_d value
    setattr(vehicle.LDS.parameters, 'c_r', c_r)     # Assign the c_r value
    # endregion

    return vehicle
