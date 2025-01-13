"""
Description: Load the selected cycle
------------
Sources: More information regarding the implementation of the LDS functions is available at:
         (1) K. Moller, „Validierung einer MATLAB Längsdynamiksimulation für die Auslegung von Elektrofahrzeugen,“ Bachelor thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2020.
         (2) K. Moller, „Antriebsstrangmodellierung zur Optimierung autonomer Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The vehicle structure updated with the loaded drive cycle
------------

# Implementation
# [0] Import modules, classes and functions
# [1] Load desired driving cycle
# [2] Adapt the drive_cycles parameters
# [3] Assign output
"""

# region [0] Import modules, classes and functions
# Import modules
import os
import json
import numpy as np
from scipy.interpolate import RegularGridInterpolator
# endregion


def load_cycle(vehicle, parameters):
    # region [1] Load desired driving cycle
    # Load cycle variable:
    list_cycle = vehicle.Input.list_cycle

    for cycle_name in list_cycle:
        path_project = os.getcwd()
        path_cycle = os.path.join(path_project, '_02_LDS', 'Drive_Cycle')

        suffix_file = cycle_name + '.json'
        file_cycle = os.path.join(path_cycle, suffix_file)   # Loading path

        # Open the json file
        with open(file_cycle, "r") as f:
            drive_cycle = json.load(f)
        # endregion

        # region [2] Adapt the drive_cycles parameters
        # Convert all of the dictionary entries into a numpy array
        for key, value in drive_cycle.items():
            value_array = np.array(value)
            drive_cycle[key] = value_array

        # if no Slope is available create empty vector, needed for further checks
        if 'S' not in drive_cycle:
            drive_cycle['S'] = np.zeros(len(drive_cycle['t']))

        while drive_cycle['t'][0] < 0:  # time steps <0 are cut off
            drive_cycle['t'] = np.delete(drive_cycle['t'], 0)
            drive_cycle['v'] = np.delete(drive_cycle['v'], 0)
            drive_cycle['S'] = np.delete(drive_cycle['S'], 0)

        if drive_cycle['t'][0] != 0:    # cycle has to start at timestep 0
            drive_cycle['t'] = np.insert(drive_cycle['t'], 0, 0, axis=0)
            drive_cycle['v'] = np.insert(drive_cycle['v'], 0, 0, axis=0)
            drive_cycle['S'] = np.insert(drive_cycle['S'], 0, 0, axis=0)

        # Assign the timestep in s
        if np.isnan(parameters.LDS.delta_t_con):
            delta_t = drive_cycle['t'][1] - drive_cycle['t'][0]     # no delta_t input available
        else:
            delta_t = parameters.LDS.delta_t_con

        # create t vector
        t = np.arange(0, drive_cycle['t'][-1] + delta_t, delta_t)

        # Assign the cycle speed in m/s
        v = drive_cycle['v'] / 3.6

        # create Interpolation for speed
        F_v = RegularGridInterpolator((drive_cycle['t'], ), v, method='linear')

        # Assign interpolated cycle speed in m/s
        v = F_v(t)

        # Assign the cycle acceleration in m/s²
        a = np.concatenate((np.zeros(1), np.diff(v)))/delta_t

        # Assign slope S in %
        alpha = drive_cycle['S']
        F_S = RegularGridInterpolator((drive_cycle['t'], ), alpha, method='linear')
        alpha = F_S(t)
        # endregion

        if cycle_name.lower() == 'wltp':
            direction = vehicle.LDS.sim_cons
        elif cycle_name.lower() == 'ecotest':
            direction = vehicle.LDS.sim_range
        else:
            raise Exception('This cylce is not available')

        # region [3] Assign output
        # As the cycle has already been loaded, the values are saved, so, that it does not have to be loaded again
        setattr(direction, 't', t)               # time vector in s
        setattr(direction, 'delta_t', delta_t)   # time step in s
        setattr(direction, 'v', v)               # speed vector in m/s
        setattr(direction, 'a', a)               # acceleration vector in m/s^2
        setattr(direction, 'alpha', alpha)       # slope vector in %
        # endregion

    return vehicle
