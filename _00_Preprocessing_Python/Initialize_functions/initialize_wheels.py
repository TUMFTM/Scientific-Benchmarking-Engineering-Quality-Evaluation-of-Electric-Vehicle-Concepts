"""
Description: This function calculates the tire dimensions based on its identifier
             and stores them in the respective nested class
             Example: Wheel Identifier: 235/40R20
             235: Defines the width of the tire
             40: Defines the aspect-ratio between width and diameter of the wheel in percent
             R: Defines the wheel construction (R=Radial-wheel and D=Diagonal-Wheel, not relevant for calculations)
             20: Defines the diameter of the rim in inch
             Calculation: wheel-diameter = width * aspect-ratio * 2 + rim-diameter * 25.4  (in mm)
------------
Sources: None
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: Expanded dimension class with the attributes of the wheels
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Calculate tire dimensions
[3] Calculate break diameter
[4] Set saving paths for the parameters
[5] Assign Wheel Outputs
[6] Calculate and assign track width
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
import re
import math
# endregion


def initialize_wheels(vehicle, parameters):
    # region [1] Assign Inputs
    # Wheel denotations for the front and rear wheels (might be different)
    wheels_notation = np.array([vehicle.Input.tire_size_f, vehicle.Input.tire_size_r])
    allocation = ['f', 'r']                 # Allocation necessary for front and rear wheel

    vehicle_width = vehicle.dimensions.GY.vehicle_width     # Get width of the vehicle

    # Parameters for calculating the disc diameter based on a linear regression with mass and acceleration time
    mass_max = vehicle.masses.vehicle_max_weight                        # max vehicle weight in kg with payload, extra equipment and passengers in kg
    acceleration = vehicle.Input.acceleration_time                      # Required acceleration time 0-100 in s
    regr_brake_disc = parameters.regr.wheel.brake_disc_f_diameter       # Brake disc diameter regression
    EX_min_offset_front = parameters.dimensions.EX.offset_brake_to_rim  # Minimum clearance between rim and brake disc expressed as difference between rim and brake diameter (in mm)
    # endregion

    # Iterate through the wheels of front and rear axle
    for idx, wheel_notation in enumerate(wheels_notation):

        # region [2] Calculate tire dimensions
        # Identify all numbers in the string of the wheel identifier
        wheel_numbers = re.findall(r"[-+]?\d*\.\d+|\d+", wheel_notation)

        # Extract the respective values from the string
        try:
            wheel_width = int(wheel_numbers[0])         # Get the wheel width in mm
        except ValueError:
            wheel_width = float(wheel_numbers[0])
        try:
            aspect_ratio = int(wheel_numbers[1]) * 0.01     # Get the aspect-ratio of the wheel
        except ValueError:
            aspect_ratio = float(wheel_numbers[1]) * 0.01
        try:
            rim_diameter_inch = int(wheel_numbers[2])   # Get the rim diameter in inch
        except ValueError:
            rim_diameter_inch = float(wheel_numbers[2])

        wheel_diameter = rim_diameter_inch * 25.4 + 2 * aspect_ratio * wheel_width

        # Calculate the estimated volume of the tire
        tire_volume = math.pi * wheel_width * 0.25 * math.pow(wheel_diameter - rim_diameter_inch * 25.4, 2)
        # endregion

        # region [3] Calculate brake diameter
        coeff = regr_brake_disc.coefficients
        CX_brake_disc_diameter = coeff[0] + coeff[1] * mass_max + coeff[2] * acceleration

        # calculate rim dimension without collision with brake system
        rim_diameter_min = round((EX_min_offset_front + CX_brake_disc_diameter)/25.4)
        if rim_diameter_min > rim_diameter_inch:
            errorlog_list = vehicle.errorlog
            text_errorlog = 'The rim diameter is to small to fit the breaks and has therefore to be increased'
            print(text_errorlog)
            errorlog_list.append(text_errorlog)
            setattr(vehicle, 'errorlog', errorlog_list)
            rim_diameter_inch = rim_diameter_min

            # Adapt the wheel diameter
            wheel_diameter = rim_diameter_inch * 25.4 + 2 * aspect_ratio * wheel_width
        # endregion

        # region [4] Set the saving paths for the variables (distinguish between front and rear axle)
        rim_diameter_path = 'rim_diameter_' + allocation[idx] + '_inch'
        wheel_diameter_path = 'wheel_' + allocation[idx] + '_diameter'
        wheel_width_path = 'wheel_' + allocation[idx] + '_width'
        aspect_ratio_path = 'side_wall_' + allocation[idx]
        tire_volume_path = 'tire_volume_' + allocation[idx]
        disc_diameter_path = 'brake_disc_' + allocation[idx] + '_diameter'
        # endregion

        # region [5] Assign Wheel Outputs
        setattr(vehicle.dimensions.CX, rim_diameter_path, rim_diameter_inch)
        setattr(vehicle.dimensions.CX, wheel_diameter_path, wheel_diameter)
        setattr(vehicle.dimensions.CX, disc_diameter_path, CX_brake_disc_diameter)
        setattr(vehicle.dimensions.CY, wheel_width_path, wheel_width)
        setattr(vehicle.wheels, aspect_ratio_path, aspect_ratio)
        setattr(vehicle.wheels, tire_volume_path, tire_volume)
        # endregion

    # region [6] Calculate and assign track width
    track_width_f = vehicle_width - vehicle.dimensions.CY.wheel_f_width
    track_width_r = vehicle_width - vehicle.dimensions.CY.wheel_r_width
    setattr(vehicle.dimensions.GY, 'track_width_f', track_width_f)
    setattr(vehicle.dimensions.GY, 'track_width_r', track_width_r)
    # endregion

    return vehicle
