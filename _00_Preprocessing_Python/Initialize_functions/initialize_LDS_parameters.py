"""
Description: This function initializes all necessary information for the LDS.
             This includes the definition of parameters and settings, the loading of the desired cycle and
             the definition and calculation of the c_r and c_d value
------------
Sources: (1) K. Moller, „Validierung einer MATLAB Längsdynamiksimulation für die Auslegung von Elektrofahrzeugen,“ Bachelor thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2020.
         (2) K. Moller, „Antriebsstrangmodellierung zur Optimierung autonomer Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The vehicle structure updated with the loaded drive cycle
------------

Implementation
[0] Import modules, classes and functions
[1] Vehicle specific settings for the LDS
[2] Simulation settings
[3] Load cycle
[4] Calculate the missing LDS inputs
[5] Calc necessary machine rotational speed
"""

# region [0] Import modules, classes and functions
# Import modules
# Import functions
from _02_LDS.Functions.helper_functions import load_cycle
from _02_LDS.Functions.check_functions import check_n_cycle
from _02_LDS.Functions.calc_functions import calc_missing_inputs
# endregion


def initialize_LDS_parameters(vehicle, parameters):
    # region [1] Vehicle specific settings for the LDS
    # Vehicle mass settings
    axle_load_front = vehicle.masses.optional_extras.front_repartition / 100
    setattr(parameters.LDS, 'axle_load_front', axle_load_front)  # axis load distribution on front axis
    setattr(parameters.LDS, 'axle_load_rear', 1 - axle_load_front)  # axis load distribution on rear axis

    # Assign power auxiliaries
    setattr(vehicle.LDS.settings, 'power_auxiliaries', vehicle.Input.power_auxiliaries)

    # Vehicle Dynamical wheel radius (based on the bigger wheel radius of front and rear wheel)
    wheels_radius = [vehicle.dimensions.CX.wheel_f_diameter/2, vehicle.dimensions.CX.wheel_r_diameter/2]
    r_dyn = max(wheels_radius) * 1.02

    # Vehicle cross-section surface
    A = vehicle.Input.vehicle_width * vehicle.Input.vehicle_height * parameters.LDS.correction_area  # cross-section area in mm ^ 2

    # Vehicle height of center of gravity
    height_COG_coeff = parameters.regr.LDS.height_COG.coefficients
    height_COG = height_COG_coeff[0] + height_COG_coeff[1] * vehicle.Input.vehicle_height   # Height of COG from the ground in mm

    setattr(vehicle.wheels, 'r_dyn', r_dyn)  # Dynamic wheel radius in mm
    setattr(vehicle.LDS.parameters, 'A', A)  # Vehicle cross sectional area
    setattr(vehicle.LDS.parameters, 'height_COG', height_COG)  # Height of the COG compared to ground
    # endregion

    # region [2] Simulation settings
    # modified vehicle class
    setattr(vehicle.LDS.settings, 'v_max_sim', 100)  # max speed in acceleration simulation in km/h
    setattr(vehicle.LDS.settings, 't_sim_max_acc', 25)  # maximum acceleration simulation time in s

    # modified parameters class
    setattr(parameters.LDS, 'delta_t', 0.1)         # step size in acceleration simulation in s
    setattr(parameters.LDS, 'delta_t_con', 0.1)     # step size in consumption simulation in s
    setattr(parameters.LDS, 'slope_angle_sim_acc', 0)  # Slope angle for acceleration simulation in °
    # endregion

    # region [3] Load cycle
    vehicle = load_cycle(vehicle, parameters)
    # endregion

    # region [4] Calculate the missing LDS inputs
    vehicle = calc_missing_inputs(vehicle, parameters)
    # endregion

    # region [5] Calc necessary machine rotational speed
    vehicle = check_n_cycle(vehicle, parameters)
    # endregion

    return vehicle, parameters
