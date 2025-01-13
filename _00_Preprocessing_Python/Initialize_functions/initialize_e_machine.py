"""
Description: This function has the task to load the basis characteristic of the electric machine based on their type
------------
Sources: (1) K. Moller, „Validierung einer MATLAB Längsdynamiksimulation für die Auslegung von Elektrofahrzeugen,“ Bachelor thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2020.
         (2) K. Moller, „Antriebsstrangmodellierung zur Optimierung autonomer Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
         (3) MDL, "Performance Analysis of Electric Motor Technologies for an Electric Vehicle Powertrain", White Paper, 2019
------------
Input: vehicle: Stores all the information of the computed vehicle
       parameters: Stores the constant values and regressions for volume and mass models
------------
Output: Vehicle class with the loaded basis characteristic of the desired machine type
------------

Implementation
[0] Import modules, classes and functions
[1] Define characteristics path
[2] Load the characteristic
[3] Adapt characteristic line
[4] Get the efficiency_map
[5] Assign all the attributes to the e_machine class
"""

# region [0] Import modules, classes and functions
# Import the modules
import json
import os
import numpy as np
# endregion


def initialize_e_machine(vehicle, parameters):

    # region [1] Define characteristics path
    path_project = os.getcwd()
    path_characteristics = os.path.join(path_project, '_02_LDS', 'Characteristics')
    # endregion

    # Iterate through both axles
    for key, value in vehicle.topology.filled_axles.items():
        if value is True:   # Only necessary when a machine is placed on the respective axle

            # region [2] Load the characteristic
            type_machine = vehicle.e_machine[key].type          # Get the type of the machine
            suffix_file = type_machine + '_MDL.json'
            file_characteristics = os.path.join(path_characteristics, suffix_file)   # Loading path

            # Open the json file
            with open(file_characteristics, "r") as f:
                machine_characteristic = json.load(f)
            # endregion

            # region [3] Adapt characteristic line
            # Set the attributes of the characteristic
            trq = np.array(machine_characteristic['Mot']['Kennlinie']['trq'])
            rpm = np.array(machine_characteristic['Mot']['Kennlinie']['rpm'])
            pwr = np.array(machine_characteristic['Mot']['Kennlinie']['pwr'])

            # Merge all three characteristic elements
            characteristic = np.column_stack((trq, rpm, pwr))

            # Ensure that the rotational speed starts with first entry gives row the second the column
            characteristic[0][1] = 0

            # Get the T_max right now
            T_max = max(characteristic[:][0])
            # endregion

            # region [4] Get the efficiency_map
            n = np.array(machine_characteristic['n'], dtype=float)
            n = np.flipud(n)
            T = np.array(machine_characteristic['M'], dtype=float)
            T = np.flipud(T)
            eta = np.array(machine_characteristic['eta'])

            # Only the first quadrant(positiven and T) is considered
            # Find columns with allnegative or allzero elements for n matrix
            n_ind = np.array(np.where(np.nansum(n, axis=0) <= 0))
            T_ind = np.array(np.where(np.nansum(T, axis=1) <= 0))

            # clear columns and rows with negative or zero rotational speed, torque and negative efficiency
            # eta = eta[n_ind[0].max() + 1:][T_ind[0].max() + 1:]
            eta = np.delete(eta, n_ind, axis=0)
            eta = np.delete(eta, T_ind, axis=1)

            # clear contents smaller zero in torque and rotational speed vector
            T = np.linspace(0, max(T[:, 1]), len(eta))
            n = np.linspace(0, max(n[1, :]), len(eta))
            # endregion

            # region [5] Assign all the attributes to the e_machine class
            setattr(vehicle.e_machine[key], 'characteristic', characteristic)       # Characteristic with torque and rpm
            setattr(vehicle.e_machine[key], 'T_max', T_max)                         # Maximum torque
            setattr(vehicle.e_machine[key].diagram, 'n_unscaled', n)                # rotational speed in 1/min
            setattr(vehicle.e_machine[key].diagram, 'T_unscaled', T)                # torque in Nm
            setattr(vehicle.e_machine[key].diagram, 'etages', eta)                  # efficiencies
            # endregion
    return vehicle, parameters
