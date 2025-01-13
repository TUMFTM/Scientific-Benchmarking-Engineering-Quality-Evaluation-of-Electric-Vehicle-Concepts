"""
Description: This function calculates the required power at the battery for one axle driven wheel drives
------------
Sources: More information regarding the implementation of the LDS functions is available at:
         (1) K. Moller, „Validierung einer MATLAB Längsdynamiksimulation für die Auslegung von Elektrofahrzeugen,“ Bachelor thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2020.
         (2) K. Moller, „Antriebsstrangmodellierung zur Optimierung autonomer Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
       axle: Corresponding powered axle
------------
Output: Operating point of motors and their power, as well as the battery power
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Calculate torque
[3] Calculate eta matrix for the motor
[4] Check that the motor does not leave the allowed overload time
[5] Assign Outputs
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
import math
from scipy.interpolate import RegularGridInterpolator
# Import functions
from _02_LDS.Functions.check_functions import check_overload
# endregion


def calc_power_two_wheel_drive(vehicle, parameters, axle, directory):
    # region [1] Assign inputs
    # assign axle variable
    quantity_EM = vehicle.e_machine[axle].quantity          # Number of electric machines at axle
    i_gearbox = vehicle.gearbox[axle].results.i_tot         # Transmission ratio at axle
    transmission_trq = quantity_EM * i_gearbox              # Help variable

    eta_batt = parameters.LDS.eta_battery                   # Efficiency of the battery
    eta_p_e = parameters.LDS.eta_power_electronics          # Efficiency of the power electronic
    # endregion

    # region [2] Calculate torque
    # Rotational speed of motor over cycle in 1/min
    n_mot = directory.n_wheels * i_gearbox

    # Efficiency of the gearbox
    eta_gear = vehicle.gearbox[axle].eta

    # calculate current operating point torque of motor over cycle in Nm
    T_mot = directory.T_wheels/(transmission_trq * np.power(eta_gear, np.sign(directory.T_wheels)))

    # calculate mechanical engine power
    P_mot = directory.P_wheels/(quantity_EM * np.power(eta_gear, np.sign(directory.P_wheels)))
    # endregion

    # region [3] Calculate eta matrix for the motor
    # Assign the values for interpolation
    n_scaled = vehicle.e_machine[axle].diagram.n_scaled
    T_scaled = vehicle.e_machine[axle].diagram.T_scaled
    etages = vehicle.e_machine[axle].diagram.etages

    # create interpolation function
    # F = RegularGridInterpolator((xd, yd), vehicle.e_machine[axle].diagram.etages.transpose(), method='linear', bounds_error=False)
    F = RegularGridInterpolator((n_scaled, T_scaled), etages.transpose(), method='linear', bounds_error=False, fill_value=None)

    # find current eta (efficiency of front motor)
    eta_mot = F((np.abs(n_mot), np.abs(T_mot)))

    P_el_mot = T_mot * n_mot * 2 * math.pi/(60 * np.power(eta_mot, np.sign(T_mot)))
    # endregion

    # region [4] Check that the motor does not leave the allowed overload time
    # Check overload for motor/motors on the front axle
    vehicle = check_overload(vehicle, parameters, T_mot, n_mot, axle)
    # endregion

    # region [5] Assign Outputs
    # Create attribute names
    if axle.lower() == 'front':
        suffix = 'f'
    else:
        suffix = 'r'

    T_mot_str = 'T_mot_' + suffix
    n_mot_str = 'n_mot_' + suffix
    eta_mot_str = 'eta_mot_' + suffix
    P_mech_mot_str = 'P_mech_mot_' + suffix
    P_el_mot_str = 'P_el_mot_' + suffix

    # operating points
    setattr(directory, T_mot_str, T_mot)         # [Nm]
    setattr(directory, n_mot_str, n_mot)         # [1/min]
    setattr(directory, eta_mot_str, eta_mot)     # [-]

    # Mechanical and electrical power of each machine, as well as battery power. All powers in W:
    # P_mech (right side of engine - output)
    setattr(directory, P_mech_mot_str, P_mot)

    # P_el (left side of engine - input)
    setattr(directory, P_el_mot_str, P_el_mot)

    # P_batt

    # Regression Parameters calculated based on real vehicle testing
    a_reku = -1.001
    b_reku = 0.2113
    c_reku = 0.8576
    d_reku = -0.001906

    x = directory.P_wheels / 1000   #Power in kW
    regression_reku = a_reku * np.exp(b_reku * x) + c_reku * np.exp(d_reku * x)

    regression_reku[regression_reku < 0] = 0

    condition = directory.P_wheels >= 0
    P_batt = np.where(condition, (P_el_mot * quantity_EM) / (eta_batt * eta_p_e),
                      directory.P_wheels * regression_reku)
    setattr(directory, 'P_batt', P_batt)

    # endregion

    return vehicle