"""
Description: This function determines the max. acceleration due to the traction limit
------------
Sources: More information regarding the implementation of the LDS functions is available at:
         (1) R. Hefele, „Implementierung einer MATLAB Längsdynamiksimulation für Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2019.
         (2) L. v. Hacken, "Grundlagen der Kraftfahrzeugtechnik", ISBN: 9783446426047, 2011
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
       F_L: Air resistance
       alpha: Slope angle
       FTM_characteristic: FTM engine characteristic for traction limit or ideal characteristic (see calc_GGV_diagram)
------------
Output: vector containing the max. acceleration at each timestep of the acceleration sim
------------

# Implementation
# [0] Import modules, classes and functions
# [1] Assign Inputs
# [2] Calculate traction limit
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
# Import functions
# endregion


def calc_traction_lim(vehicle, parameters, F_L, alpha, FTM_characteristic):
    # region [1] Assign Inputs
    # Initialize variables to make the equation shorter:
    if FTM_characteristic:
        m = vehicle.masses.vehicle_empty_weight_EU_sim  # simulated Vehicle mass in kg (empty weight + driver)
    else:
        m = vehicle.masses.vehicle_empty_weight_EU  # real vehicle mass in kg (empty weight + driver)
    h_COG = vehicle.LDS.parameters.height_COG       # height COG in mm
    wb = vehicle.dimensions.GX.wheelbase            # wheelbase in mm
    c_r = vehicle.LDS.parameters.c_r                # roll resistance coefficient
    drive_topology = vehicle.topology.drive         # Front-, rear-, or all-wheel-drive

    # General parameters
    g = parameters.LDS.g                            # gravitational acceleration in m / s ^ 2
    mu = parameters.LDS.mue_max                     # driving traction coefficient

    # Convert slope angle into radians
    alpha_rad = np.radians(alpha)
    # endregion

    # region [2] Calculate traction limit
    if drive_topology == 'RWD':
        load_f = vehicle.masses.optional_extras.front_repartition / 100
        load_r = 1 - load_f
        traction_limit = (g * (mu * (load_f * np.cos(alpha_rad) + (h_COG/wb) * np.sin(alpha_rad)) -
                               c_r * (load_r * np.cos(alpha_rad) - (h_COG/wb) * np.sin(alpha_rad)) -
                               np.sin(alpha_rad)) - (F_L/m))/(1 - (h_COG/wb) * (mu + c_r))
    elif drive_topology == 'FWD':
        load_f = vehicle.masses.optional_extras.front_repartition / 100
        load_r = 1 - load_f
        traction_limit = (g * (mu * (load_r * np.cos(alpha_rad) - (h_COG/wb) * np.sin(alpha_rad)) -
                               c_r * (load_f * np.cos(alpha_rad) + (h_COG/wb) * np.sin(alpha_rad)) -
                               np.sin(alpha_rad)) - (F_L/m))/(1 + (h_COG/wb) * (mu+c_r))
    else:
        traction_limit = g * (mu * np.cos(alpha_rad) - np.sin(alpha_rad)) - (F_L / m)
    # endregion

    return traction_limit
