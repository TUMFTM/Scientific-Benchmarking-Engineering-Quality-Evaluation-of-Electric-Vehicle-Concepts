"""
Description: This function determines the velocity of the 18m-slalom based on the predetermined regression coefficients
------------
Sources: (1) S. Bogdan, "Weiterentwicklung eines Simulationsmodells zur Bewertung von Elektrofahrzeugkonzepten im Bereich Querdynamik", Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2024.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The calculated velocity for the 18m slalom maneuver
------------

Implementation
[0] Import modules, classes and functions
[1] Assign simulation variables
[2] Calculate the slalom velocity using the predetermined multiple linear regression coefficients
[3] Assign Output
"""

# region [0] Import modules, classes and functions
# Import modules: no modules needed.
# endregion


def calc_slalom(vehicle, parameters, benchmarking):
    # region [1] Assign simulation variables
    # assign regression coefficients
    y_offset = parameters.regr.LDS.lateraldynamics_slalom.coefficients[0]
    coeff_COG_height = parameters.regr.LDS.lateraldynamics_slalom.coefficients[1]
    coeff_tire_fl_height = parameters.regr.LDS.lateraldynamics_slalom.coefficients[2]
    coeff_vehicle_mass = parameters.regr.LDS.lateraldynamics_slalom.coefficients[3]

    # assign vehicle parameters
    track_width_f = vehicle.dimensions.GY.vehicle_width - benchmarking.performance.tire_width_f
    track_width_r = vehicle.dimensions.GY.vehicle_width - benchmarking.performance.tire_width_r
    track_width_avg = 0.5 * (track_width_f + track_width_r)
    vehicle_height = vehicle.dimensions.GZ.vehicle_height
    COG_height_estm = track_width_avg / vehicle_height

    tire_flank_height_f = benchmarking.performance.tire_width_f * 0.01 * benchmarking.performance.tire_flank_height_f
    tire_flank_height_r = benchmarking.performance.tire_width_r * 0.01 * benchmarking.performance.tire_flank_height_r
    tire_flank_height_avg = 0.5 * (tire_flank_height_f + tire_flank_height_r)

    vehicle_mass = 0.001 * vehicle.masses.vehicle_empty_weight_sim
    # endregion

    # region [2] Calculate the slalom velocity based on the regression equation
    v_slalom = y_offset + coeff_COG_height * COG_height_estm + coeff_tire_fl_height * tire_flank_height_avg + coeff_vehicle_mass * vehicle_mass
    # endregion

    # region [3] Assign Output
    # Results slalom velocity:
    setattr(vehicle.Lateral_Dynamics, 'v_slalom', v_slalom)      # struct that stores result: slalom velocity

    # endregion

    return vehicle
