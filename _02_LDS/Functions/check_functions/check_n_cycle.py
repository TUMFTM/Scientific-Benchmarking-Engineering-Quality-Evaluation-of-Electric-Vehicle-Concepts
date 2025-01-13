"""
Description: This function calculates the rotational speed of the wheels for the given driving cycle.
             The function uses the same method as the function calc_resistance
             Because some vehicle values are not known yet they are either assumed (e_i) or used from the real
             vehicle (mass)
------------
Sources: More information regarding the implementation of the LDS functions is available at:
         (1) K. Moller, „Validierung einer MATLAB Längsdynamiksimulation für die Auslegung von Elektrofahrzeugen,“ Bachelor thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2020.
         (2) K. Moller, „Antriebsstrangmodellierung zur Optimierung autonomer Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: Operating point of motors and their power, as well as the battery power
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Calculation of resistance, torque and rotational speed
[3] Assign Output
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
import math
# Import functions
# endregion


def check_n_cycle(vehicle, parameters):
    # region [1] Assign Inputs
    # Assign cycle values
    v = vehicle.LDS.sim_cons.v
    a = vehicle.LDS.sim_cons.a
    alpha = vehicle.LDS.sim_cons.alpha

    # Assign vehicle specific parameters
    c_d = vehicle.LDS.parameters.c_d  # Vehicle Drag Coefficient
    c_r = vehicle.LDS.parameters.c_r  # rolling resistance coefficient
    e_i = parameters.LDS.e_i          # Not yet known so general e_i factor is assumed
    A = vehicle.LDS.parameters.A  # cross-section area in mm^2
    vehicle_weight = vehicle.masses.vehicle_empty_weight_EU     # Real Vehicle mass in kg (empty weight + driver)

    # Assign simulation parameters
    rho_L = parameters.LDS.rho_L  # Air density in m*kg^-3
    g = parameters.LDS.g  # Gravitational constant in m^3kg^-2s^-1
    # endregion

    # region [2] Calculation of resistance, torque and rotational speed
    # Calculation of resistance - all forces in N (fundamental equation of longitudinal dynamics)
    F_a = 0.5 * rho_L * c_d * A / math.pow(1000, 2) * np.square(v)  # air resistance in N
    F_r = vehicle_weight * g * c_r * np.cos(alpha)  # roll resistance in N
    F_g = vehicle_weight * g * np.sin(alpha)  # slope resistance in N
    F_m = vehicle_weight * e_i * a  # acceleration resistance in N

    # If the speed or the acceleration is 0, i. e. vehicle is not moving, F_r is set to 0
    F_r[v < 1e-2] = 0

    # Calculate total resistance in N
    F_tot = F_a + F_r + F_g + F_m

    # Torque at the wheels in Nm
    T_wheels = F_tot * vehicle.wheels.r_dyn / 1000
    T_wheel_max_cycle = np.max(T_wheels)

    # Rotational speed of wheels in 1/min
    n_wheels = v / (vehicle.wheels.r_dyn / 1000) * 60 / 2 / math.pi
    n_wheel_max_cycle = np.max(n_wheels)
    # endregion

    # region [3] Assign Outputs
    # store resistance values in resistance struct
    setattr(vehicle.LDS.parameters, 'n_wheel_max_cycle', n_wheel_max_cycle)
    setattr(vehicle.LDS.parameters, 'T_wheel_max_cycle', T_wheel_max_cycle)
    # endregion
    return vehicle
