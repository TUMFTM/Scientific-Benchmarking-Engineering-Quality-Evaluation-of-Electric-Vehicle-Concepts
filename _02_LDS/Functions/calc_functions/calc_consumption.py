"""
Description: This function determines the vehicle's energy consumption according to the chosen driving cycle
------------
Sources: More information regarding the implementation of the LDS functions is available at:
         (1) K. Moller, „Validierung einer MATLAB Längsdynamiksimulation für die Auslegung von Elektrofahrzeugen,“ Bachelor thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2020.
         (2) K. Moller, „Antriebsstrangmodellierung zur Optimierung autonomer Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: -energy consumption in driving cycle
        -distance in driving cycle
        -velocity in dc
        -acceleration
        -battery power
------------

Implementation
[0] Import modules, classes and functions
[1] Initialize variables from driving cycle
[2] Calculate resistance
[3] Calculate Power requirements, according to the topology
[4] Check traction limit
[5] Calculate consumption outputs
[6] Assign Outputs
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
import math
# Import functions
from .calc_resistance import calc_resistance
from .calc_power_two_wheel_drive import calc_power_two_wheel_drive
from .calc_power_all_wheel_drive import calc_power_all_wheel_drive
from _02_LDS.Functions.check_functions import check_torque_sim_cons
from _02_LDS.Functions.calc_functions.calc_traction_lim import calc_traction_lim
# endregion


def calc_consumption(vehicle, parameters, direction):
    # region [1] Initialize variables from driving cycle
    # Assign time, timestep, velocity and acceleration

    directory = getattr(vehicle.LDS, direction)

    delta_t = directory.delta_t      # time step in s
    v = directory.v                  # speed vector in m/s
    a = directory.a                  # acceleration vector in m/s^2
    alpha = directory.alpha          # slope vector in %
    topology_drive = vehicle.topology.drive     # AWD, RWD, FWD
    # endregion

    # region [2] Calculate resistance
    # Calculate resistance according to loaded cycle:
    resistance, T_wheels, n_wheels = calc_resistance(v, a, alpha, vehicle, parameters, directory)
    setattr(directory, 'resistance', resistance)
    setattr(directory, 'T_wheels', T_wheels)
    setattr(directory, 'n_wheels', n_wheels)
    # endregion

    # region [3] Calculate Power requirements, according to the topology
    # Needed Power at the wheels in W
    P_wheels = T_wheels * n_wheels * 2 * math.pi/60
    setattr(directory, 'P_wheels', P_wheels)

    if topology_drive == 'AWD':
        calc_power_all_wheel_drive(vehicle, parameters, directory)
    elif topology_drive == 'FWD':
        axle = 'front'
        vehicle = calc_power_two_wheel_drive(vehicle, parameters, axle, directory)
    else:           # RWD
        axle = 'rear'
        vehicle = calc_power_two_wheel_drive(vehicle, parameters, axle, directory)

    # Check if the motor torque is sufficient for the cycle
    check_torque, vehicle = check_torque_sim_cons(vehicle, directory)
    # endregion

    # region [4] Check traction limit
    # From this point there are no more iterations through sim_acc, which is why the traction limit is checked here:
    # Checking it inside acceleration_sim could cause an ErrorLog every time the function is called.

    # a) Check traction limit during acceleration from 0 to v_max:
    if vehicle.LDS.sim_acc.exceeded_traction_limit:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The installed power causes a traction loss during the acceleration from 0 to ' + str(
            vehicle.LDS.settings.v_max_sim) + ' km/h'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    # b) Check traction limit sim_cons:
    traction_limit = calc_traction_lim(vehicle, parameters, directory.resistance.F_a, alpha, FTM_characteristic=True)
    setattr(directory, 'traction_limit', traction_limit)

    # check if acceleration is surpassed in any time step during the cycle
    if np.any(a > directory.traction_limit):
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The given acceleration in the driving cycle is above traction limit'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)
    # endregion

    # region [5] Calculate consumption outputs
    # P_batt vector without auxiliaries in kW
    P_batt = directory.P_batt/1000

    # calculate P_batt with auxiliaries if activated in kW
    if hasattr(vehicle.LDS.settings, 'power_auxiliaries'):
        power_auxiliaries = vehicle.LDS.settings.power_auxiliaries
    else:
        power_auxiliaries = 0
    P_batt = P_batt + power_auxiliaries

    # Calculate energy values
    E_bat_step = P_batt * delta_t / 3600            # consumed energy per time step kW h
    E_bat_cum = np.nancumsum(E_bat_step)            # cumulated energy vector in kW.h
    E_bat_sum = E_bat_cum[-1]                       # required total energy in kW h (scalar)
    dist_vec = np.cumsum(v * delta_t)/1000          # distance vector of driving cycle in km
    dist = dist_vec[-1]                             # total distance of driving cycle in km
    consumption100km = E_bat_sum / dist * 100       # power consumption of 100km

    # Set the range of the vehicle in the corresponding cycle
    range = vehicle.battery.energy_is_net_in_kWh / consumption100km * 100
    # endregion

    # region [6] Assign Outputs
    setattr(directory, 'P_batt', P_batt)

    # Assign battery Energy to sim_cons
    setattr(directory, 'E_bat_step', E_bat_step)
    setattr(directory, 'E_bat_cum', E_bat_sum)
    setattr(directory, 'E_bat_sum', E_bat_sum)
    setattr(directory, 'dist_vec', dist_vec)
    setattr(directory, 'dist', dist)
    setattr(directory, 'consumption100km', consumption100km)
    setattr(directory, 'range', range)
    # endregion

    return vehicle
