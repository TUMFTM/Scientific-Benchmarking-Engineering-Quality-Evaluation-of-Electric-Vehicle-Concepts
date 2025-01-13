"""
Description:  This function calculates the maximum attainable speed of the vehicle
------------
Sources: More information regarding the implementation of the LDS functions is available at:
         (1) K. Moller, „Validierung einer MATLAB Längsdynamiksimulation für die Auslegung von Elektrofahrzeugen,“ Bachelor thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2020.
         (2) K. Moller, „Antriebsstrangmodellierung zur Optimierung autonomer Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: vehicle struct with v_max of vehicle
------------
Implementation
[0] Import modules, classes and functions
[1] Inertia factor for given Input
[2] Calculate speed at the axles
[3] Calculate max speed
[4] Assign Outputs
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
import math
from scipy.interpolate import RegularGridInterpolator
# Import functions
# endregion


def calc_max_speed(vehicle, parameters):
    # region [1] Initialize needed Inputs:
    # Number of speed and rotational speed steps
    steps = 100

    # Initialize vehicle specific parameters
    c_d = vehicle.LDS.parameters.c_d                    # drag coefficient in [-]
    c_r = vehicle.LDS.parameters.c_r                    # roll resistance coefficient in [-]
    A = vehicle.LDS.parameters.A/math.pow(1000, 2)      # cross sectional area in m^2
    m = vehicle.masses.vehicle_empty_weight_EU_sim      # empty weight with driver in kg

    # Initialize general parameters
    rho = parameters.LDS.rho_L                          # air density in kg/m^3
    g = parameters.LDS.g                                # gravitational acceleration in m/s^2
    # endregion

    # region [2] Calculate speed at the axles
    # Find which axles are filled: [front_axle, rear_axle]
    filled_axles = vehicle.topology.filled_axles
    topology_drive = vehicle.topology.drive

    # Preallocate variables for speed
    F_d_base = np.zeros((2, steps))
    v_axle = np.zeros((2, steps))

    for axle, (key, value) in enumerate(filled_axles.items()):
        if value is True:

            # Motor moment (in Nm) and Motor speed (in 1/s):
            T_mot = vehicle.e_machine[key].characteristic[:, 0] * vehicle.e_machine[key].quantity
            n_mot = vehicle.e_machine[key].characteristic[:, 1]

            # Efficiency of the gearbox
            eta_gear = vehicle.gearbox[key].eta

            # Wheel moment (in Nm) and wheel speed (in rad/s):
            T_wheel_base = T_mot * eta_gear * vehicle.gearbox[key].results.i_tot
            n_wheel_base = n_mot/vehicle.gearbox[key].results.i_tot

            # Interpolate
            F = RegularGridInterpolator((n_wheel_base, ), T_wheel_base, method='linear', bounds_error=False)

            # Actualize rotational wheel speed and torque:
            n_wheel = np.linspace(1, max(n_wheel_base), steps)
            T_wheel = F(n_wheel)

            # Calculate driving force in N
            F_d_base[axle, :] = T_wheel/(vehicle.wheels.r_dyn/1000)

            # Calculate v at the axle in m/s
            v_axle[axle, :] = n_wheel * 2 * math.pi/60 * (vehicle.wheels.r_dyn/1000)
    # endregion

    # region [3] Calculate max speed
    # In the AWD case the max speed corresponds to the smallest reachable speed between front and rear axle, i.e. the speed when one of the two axes reaches its power limit.
    if topology_drive == 'AWD':
        v_max = np.min(np.max(v_axle, axis=1))
    elif topology_drive == 'FWD':
        v_max = np.max(v_axle[0, :])
    else:
        v_max = np.max(v_axle[1, :])

    # Actualize vector with max possible speed in m/s
    v = np.linspace(0, v_max, steps)
    F_d = np.zeros((2, steps))

    # Calculate total driving force (sum between driving force at the front and the rear axle:
    for axle, (key, value) in enumerate(filled_axles.items()):
        if value is True:
            F2 = RegularGridInterpolator((v_axle[axle, :], ), F_d_base[axle, :], method='linear', bounds_error=False)

            # Axle driving force in N
            F_d[axle, :] = F2(v)

    # Total driving force in N (both rear and front axle)
    if topology_drive == 'AWD':     # all wheel drive
        F_d_tot = np.sum(F_d, axis=0)
    elif topology_drive == 'FWD':   # front wheel drive
        F_d_tot = F_d[0, :]
    else:                           # rear wheel drive
        F_d_tot = F_d[1, :]

    # Calculate vehicle resistance
    F_m = 0                                     # No acceleration at v_max, i.e. no acceleration resistance
    F_a = 0.5 * c_d * rho * A * np.square(v)    # Air resistance in N
    F_g = 0                                     # Slope resistance is considered as 0 (no slope)
    F_r = m * g * c_r * np.ones((1, len(v)))    # Rolling resistance in N
    F_tot = F_m + F_a + F_g + F_r               # Total resistance in N

    # Find the point when the difference between driving force and resistance is the smallest (i.e. close to power limit)
    # Ignore the first nan which is caused by the Interpolation with initial speed of 0
    i_vmax = np.nanargmin(np.absolute(F_d_tot - F_tot))

    # Maximum vehicle speed in km / h
    v_max_output = v[i_vmax] * 3.6
    # endregion

    # region [4] Assign Outputs
    setattr(vehicle.LDS.sim_speed, 'max_speed_is', v_max_output)
    # endregion

    return vehicle
