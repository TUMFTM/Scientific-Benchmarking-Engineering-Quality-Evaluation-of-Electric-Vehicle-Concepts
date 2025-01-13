"""
Description: This function calculates the required power at the battery for allwheel drives.
             For this case, the optimal torque distribution at each timstep is calculated
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
[2] Calculate torque
[3] Calculate eta matrix for the motor
[4] Check that the motor does not leave the allowed overload time
[5] Assign Outputs
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
from scipy.interpolate import RegularGridInterpolator
# Import functions
from _02_LDS.Functions.check_functions import check_overload
# end


def calc_power_all_wheel_drive(vehicle, parameters, directory):
    # region [1] Generate possible Torque matrix from the torque split factor and evaluate gearbox model --> needed mechanical engine power
    # define torque split vector from 0 to 1
    torquesplit = np.arange(0, 1.01, 0.01)

    # For the sign function, only one column instead of the whole matrix T or w is needed
    id_trq = round(np.size(torquesplit)/2)

    #  define gearbox transmission ratios
    i_gearbox_f = vehicle.gearbox['front'].results.i_tot
    i_gearbox_r = vehicle.gearbox['rear'].results.i_tot

    # get quantity of electric machines
    quantity_f = vehicle.e_machine['front'].quantity
    quantity_r = vehicle.e_machine['rear'].quantity

    # Rotational speed of the wheels according to the drive cycle
    n_wheels = directory.n_wheels

    # Torque at the wheels according to the drive cycle
    T_wheels = directory.T_wheels

    # Power at the wheels according to the drive cycle
    P_wheels = directory.P_wheels

    # Rotational speed of motor over cycle in 1/min
    n_mot_f = np.tile(n_wheels * i_gearbox_f, (np.size(torquesplit), 1))
    n_mot_r = np.tile(n_wheels * i_gearbox_r, (np.size(torquesplit), 1))

    # Efficiency of the gearboxes
    eta_gear_f = vehicle.gearbox['front'].eta
    eta_gear_r = vehicle.gearbox['rear'].eta

    # matrix of torque at wheels (computed with outer product to create matrix)
    T_wheel_f = np.outer(torquesplit, T_wheels)         # torque of front wheels in Nm (torque as row in matrix)
    T_wheel_r = np.outer((1 - torquesplit), T_wheels)   # torque of rear wheels in Nm (torque as row in matrix)

    # matrix of power at wheels
    P_wheel_f = np.outer(torquesplit, P_wheels)         # torque of front wheels in Nm (torque as row in matrix)
    P_wheel_r = np.outer((1 - torquesplit), P_wheels)   # torque of rear wheels in Nm (torque as row in matrix)

    # matrix of torque needed for each electric machine in Nm
    T_mot_f = (T_wheel_f/(quantity_f * i_gearbox_f))/np.power(eta_gear_f, np.sign(T_wheel_f[id_trq, :]))    # torque of front motor in Nm
    T_mot_r = (T_wheel_r/(quantity_r * i_gearbox_r))/np.power(eta_gear_r, np.sign(T_wheel_r[id_trq, :]))    # torque of rear motor in Nm

    # calculate mechanical engine power
    P_mot_f = P_wheel_f / (quantity_f * np.power(eta_gear_f, np.sign(P_wheel_f[id_trq, :])))
    P_mot_r = P_wheel_r / (quantity_r * np.power(eta_gear_r, np.sign(P_wheel_r[id_trq, :])))
    # endregion

    # region [2] Calculate eta matrix for the motors
    # find front motor eta for current operating point
    n_scaled_f = vehicle.e_machine['front'].diagram.n_scaled
    T_scaled_f = vehicle.e_machine['front'].diagram.T_scaled
    etages_f = vehicle.e_machine['front'].diagram.etages

    # find rear motor eta for current operating point if there's an efficiency map
    n_scaled_r = vehicle.e_machine['rear'].diagram.n_scaled
    T_scaled_r = vehicle.e_machine['rear'].diagram.T_scaled
    etages_r = vehicle.e_machine['rear'].diagram.etages

    # create interpolation function for front motor
    F_f = RegularGridInterpolator((n_scaled_f, T_scaled_f), etages_f.transpose(), method='linear', bounds_error=False, fill_value=None)

    # create interpolation function for rear motor
    F_r = RegularGridInterpolator((n_scaled_r, T_scaled_r), etages_r.transpose(), method='linear', bounds_error=False, fill_value=None)

    # Initialize efficiency matrix
    eta_mot_f = np.zeros(np.shape(n_mot_f))
    eta_mot_r = np.zeros(np.shape(n_mot_r))

    # Iterative calculation of the etas for both motors
    for i in range(0, np.shape(n_mot_f)[0]):
        eta_mot_f[i, :] = F_f((np.abs(n_mot_f[i, :]), np.abs(T_mot_f[i, :])))
        eta_mot_r[i, :] = F_r((np.abs(n_mot_r[i, :]), np.abs(T_mot_r[i, :])))
    # endregion

    # region [3] Calculate resulting Power matrix and find the optimal distribution

    # Calculate electrical power of the motor for each possible torque distribution (in W)
    P_el_mot_f = P_mot_f / np.power(eta_mot_f, np.sign(P_mot_f[id_trq, :])) * quantity_f
    P_el_mot_r = P_mot_r / np.power(eta_mot_r, np.sign(P_mot_r[id_trq, :])) * quantity_r
    P_el_mot_tot = P_el_mot_f + P_el_mot_r

    # Find the operating point, where to reach the required torque, the resulting electrical power is the lowest
    P_el_min = np.nanmin(P_el_mot_tot, axis=0)
    I_mot = np.nanargmin(P_el_mot_tot, axis=0)

    dim_row_col = np.row_stack((I_mot, np.arange(0, np.shape(P_el_mot_tot)[1], 1)))
    idx = np.ravel_multi_index(dim_row_col, np.shape(P_el_mot_tot))

    # Calculate the minimum Power at the wheels for the Rekuperation Regression
    P_wheels_tot = P_wheel_f + P_wheel_r
    P_wheels_min = np.nanmin(P_wheels_tot, axis=0)

    # Vector of battery power in W over drive cycle
    eta_battery = parameters.LDS.eta_battery
    eta_pe = parameters.LDS.eta_power_electronics

    # Regression Parameters calculated based on real vehicle testing
    a_reku = -1.001
    b_reku = 0.2113
    c_reku = 0.8576
    d_reku = -0.001906

    x = P_wheels_min / 1000  # Power in kW
    regression_reku = a_reku * np.exp(b_reku * x) + c_reku * np.exp(d_reku * x)
    regression_reku[regression_reku < 0] = 0

    condition = P_el_min >= 0
    P_batt = np.where(condition, P_el_min / (eta_battery * eta_pe),
                      P_wheels_min * regression_reku)

    # endregion

    # region [4] Check that the motor does not remain too long in the overload zone
    # Check overload for motor/motors on the front axle
    idx_unravel = np.unravel_index(idx, np.shape(P_el_mot_tot))
    vehicle = check_overload(vehicle, parameters, T_mot_f[idx_unravel], n_mot_f[idx_unravel], 'front')
    # Check overload for motor/motors on the rear axle
    vehicle = check_overload(vehicle, parameters, T_mot_r[idx_unravel], n_mot_r[idx_unravel], 'rear')
    # endregion

    # region [5] Evaluate Torque Distribution
    distr_trq_f, distr_trq_r, distr_trq_rel = calc_torque_distribution(I_mot)
    # endregion

    # region [6] Assign Power Outputs
    # Vector describing the operation points of motor/motors
    setattr(directory, 'eta_mot_f', eta_mot_f[idx_unravel])      # [-]
    setattr(directory, 'eta_mot_r', eta_mot_r[idx_unravel])      # [-]
    setattr(directory, 'T_mot_f', T_mot_f[idx_unravel])          # [Nm]
    setattr(directory, 'T_mot_r', T_mot_r[idx_unravel])          # [Nm]
    setattr(directory, 'n_mot_f', n_mot_f[idx_unravel])          # [1/min]
    setattr(directory, 'n_mot_r', n_mot_r[idx_unravel])          # [1/min]

    # Gear, gear distribution and torque distribution
    # Torque distribution in %
    torque_distribution = {'trq_front': distr_trq_f, 'trq_rear': distr_trq_r, 'trq_sum': distr_trq_f + distr_trq_r}                      # in percent
    setattr(directory, 'torque_distribution', torque_distribution)
    setattr(directory, 'torque_distribution_cycle', distr_trq_rel)       # relative use of front or rear motor referred to total use in cycle

    # Mechanical and electrical power of each machine, as well as battery power. All powers in W:
    setattr(directory, 'P_mech_mot_f', P_mot_f[idx_unravel])
    setattr(directory, 'P_mech_mot_r', P_mot_r[idx_unravel])
    setattr(directory, 'P_el_mot_f', P_el_mot_f/quantity_f)
    setattr(directory, 'P_el_mot_r', P_el_mot_r/quantity_r)
    setattr(directory, 'P_batt', P_batt)
    # endregion

    return vehicle


def calc_torque_distribution(I_mot):
    # region [7] Additional Function
    # distribution torque front - rear
    # calculate distribution between front and rear axle
    distr_trq_f = np.mod(I_mot, 101)

    # "translate" vector to vector with values from 0-100 percent
    distr_trq_f[distr_trq_f == 0] = 101
    distr_trq_f = distr_trq_f - 1

    # create distribution vector for rear axle
    distr_trq_r = 100 - distr_trq_f

    # calculate number of total time steps * 100% and calculate relative motor usage
    sum_step = np.sum(distr_trq_f + distr_trq_r)
    sum_f = np.sum(distr_trq_f)
    sum_r = np.sum(distr_trq_r)

    # relative usage of front/rear motor
    distr_trq_rel = {'rel_front': sum_f/sum_step, 'rel_rear': sum_r/sum_step, 'rel_all': sum_step/sum_step}
    # endregion

    return distr_trq_f, distr_trq_r, distr_trq_rel