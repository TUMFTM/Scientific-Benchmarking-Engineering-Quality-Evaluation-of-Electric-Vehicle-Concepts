"""
Description: This function determines the time of the vehicle concept for acceleration from 0-100 km/h
             Acceleration simulation uses only the first gear
------------
Sources: More information regarding the implementation of the LDS functions is available at:
         (1) K. Moller, „Validierung einer MATLAB Längsdynamiksimulation für die Auslegung von Elektrofahrzeugen,“ Bachelor thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2020.
         (2) K. Moller, „Antriebsstrangmodellierung zur Optimierung autonomer Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The acceleration time and further results of the acceleration simulation
------------

Implementation
[0] Import modules, classes and functions
[1] Assign simulation variables
[2] Calculate the maximum Torque on the wheels
[3] Calculate acceleration time
[4] Error log and assign Output
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
import math
from scipy.interpolate import RegularGridInterpolator
from scipy import interpolate as ip
# Import functions
from _02_LDS.Functions.calc_functions.calc_traction_lim import calc_traction_lim
# endregion


def calc_acceleration(vehicle, parameters):
    # region [1] Assign simulation variables
    # maximum simulation time in s and maximum step value in s
    t_max = vehicle.LDS.settings.t_sim_max_acc
    delta_t = parameters.LDS.delta_t

    # define velocity vector in km/h
    v = np.arange(0, vehicle.LDS.settings.v_max_sim + 1, 1)

    # Start timer
    i = 0

    # Assign elevation value in °
    alpha = parameters.LDS.slope_angle_sim_acc

    # Traction limit marker. It will be set to 1, if the traction limit is exceeded for at least one timestep
    exceeded_traction_limit_sim_acc = 0
    # endregion

    # region [2] Calculate the maximum Torque on the wheels
    # preallocating of vectors for speed
    n_motor = np.zeros((2, len(v)))
    T_motors = np.zeros((2, len(v)))
    T_wheels = np.zeros((2, len(v)))

    for axle, (key, value) in enumerate(vehicle.topology.filled_axles.items()):
        if value is True:

            # calculate the motor speed at each vehicle speed in 1/min - only gear 1 is used
            n_wheel = v/3.6/(vehicle.wheels.r_dyn/1000) * 60/2/math.pi
            n_motor[axle, :] = n_wheel * vehicle.gearbox[key].results.i_tot

            # interpolate values from the T_max motor curve
            characteristic = vehicle.e_machine[key].characteristic

            # interpolate values from the T_max motor curve
            F = ip.interp1d(characteristic[:, 1], characteristic[:, 0], kind='linear')

            # Find torque of all motors on the axle in Nm
            T_motors[axle, :] = F(n_motor[axle, :])

            # Efficiency of the gearbox
            eta_gear = vehicle.gearbox[key].eta

            # torque of wheels in Nm
            T_wheels[axle, :] = vehicle.e_machine[key].quantity * T_motors[axle, :] * vehicle.gearbox[key].results.i_tot * eta_gear

    # Find torque of all motors on both axes in Nm
    T_wheels_sum = np.sum(T_wheels, axis=0)
    # endregion

    # region [3] Calculate acceleration time
    # define T (in Nm) which is available wheel torque dependant on rotational speed of motor (at timestep 1)
    T = np.array([T_wheels_sum[0]])

    # interpolation of torque
    F1 = RegularGridInterpolator((v, ), T_wheels_sum, method='linear', bounds_error=False)

    # precalculate vector of air resistance force (in N) before loop. Needed for traction limit
    F_a = 0.5 * parameters.LDS.rho_L * vehicle.LDS.parameters.c_d * vehicle.LDS.parameters.A/math.pow(1000, 2) * \
          np.square(np.arange(0, vehicle.LDS.settings.v_max_sim + 1, 1)/3.6)

    # run function and calculate traction limit vector
    traction_limit = calc_traction_lim(vehicle, parameters, F_a, alpha, FTM_characteristic=True)

    # interpolate F_a and the traction limit
    F2 = RegularGridInterpolator((F_a, ), traction_limit, method='linear', bounds_error=False)

    # preallocate velocity in km/h
    v_actual = np.zeros(int(math.pow(10, 4)))

    # Preallocate the other vectors
    F_d = np.zeros(1)
    F_a = np.zeros(1)
    F_r = np.zeros(1)
    F_g = np.zeros(1)
    F_m = np.zeros(1)
    acc = np.zeros(1)
    traction_limit_vec = np.zeros(1)
    acc_limited = np.zeros(1)
    # start acceleration maneuver while velocity is smaller than max velocity and simulation time is
    while v_actual[i] < max(v) and (delta_t * (i-1)) < t_max:

        # count timer up in s
        i = i+1

        # maximum available torque (Nm) at wheels from all motors dependent on velocity
        T_step = F1(np.array([v_actual[i-1]]))
        T = np.append(T, T_step)          # use interpolation function to interpolate

        # calculate drive force in N from the T of the previous timestep
        F_d_step = T[i-1] / (vehicle.wheels.r_dyn/1000)
        F_d = np.append(F_d, F_d_step)

        # calculate air resistance in N
        F_a_step = 0.5 * parameters.LDS.rho_L * vehicle.LDS.parameters.c_d * \
                   vehicle.LDS.parameters.A/math.pow(1000, 2) * np.square(v_actual[i-1]/3.6)
        F_a = np.append(F_a, F_a_step)

        # calculate roll resistance in N
        F_r_step = vehicle.masses.vehicle_empty_weight_EU_sim * parameters.LDS.g * \
                   vehicle.LDS.parameters.c_r * math.cos(math.radians(alpha))
        F_r = np.append(F_r, F_r_step)

        # calculate slope resistance in case of alpha is not zero in N
        F_g_step = vehicle.masses.vehicle_empty_weight_EU_sim * parameters.LDS.g * math.sin(math.radians(alpha))
        F_g = np.append(F_g, F_g_step)

        # calculate acceleration resistance in N
        F_m_step = F_d[i] - F_a[i] - F_r[i] - F_g[i]
        F_m = np.append(F_m, F_m_step)

        # resulting acceleration of vehicle in m/s^2
        acc_step = F_m[i]/(vehicle.masses.vehicle_empty_weight_EU_sim * vehicle.LDS.parameters.e_i)
        acc = np.append(acc, acc_step)

        # interpolate max acceleration due to traction in m/s^2
        traction_limit_vec_step = F2(np.array([F_a[i]]))
        traction_limit_vec = np.append(traction_limit_vec, traction_limit_vec_step)

        # if the acceleration is above the traction limit, assign the traction limit as max acceleration!
        acc_limited_step = min(acc[i], traction_limit_vec[i])
        acc_limited = np.append(acc_limited, acc_limited_step)  # vector with the acceleration of each simulation step in m/s^2

        # resulting velocity of next time step
        v_actual[i] = v_actual[i - 1] + acc_limited[i] * 3.6 * delta_t  # vector with the velocity of each simulation step in km/h
    # endregion

    # region [4] Error log and assign Output
    # Check traction limit:
    if np.any(acc > traction_limit_vec):
        # Traction limit has been exceeded at least once
        exceeded_traction_limit_sim_acc = 1

    # Results acceleration simulation:
    setattr(vehicle.LDS.sim_acc, 'a', acc)                          # struct that stores result: acceleration vector in m/s^2
    setattr(vehicle.LDS.sim_acc, 'a_limited', acc_limited)         # Vector containing the point where the acceleration time has to be limited due to traction loss
    setattr(vehicle.LDS.sim_acc, 'v', v_actual[0:i])                            # velocity vector in km/h
    setattr(vehicle.LDS.sim_acc, 't', np.arange(0, delta_t * i + 1, delta_t))     # time vector in s
    setattr(vehicle.LDS.sim_acc, 'acc_time_is', delta_t * i)                # t_max_acc in s

    # Resistance and max torque:
    T = np.append(T, F1(np.array([v_actual[i]])))
    setattr(vehicle.LDS.sim_acc, 'T_wheels', T)                 # torque at the wheels in Nm
    setattr(vehicle.LDS.sim_acc.resistance, 'F_a', F_a[0:i])    # air resistance in N
    setattr(vehicle.LDS.sim_acc.resistance, 'F_r', F_r)         # roll resistance in N
    setattr(vehicle.LDS.sim_acc.resistance, 'F_g', F_g)         # gradient resistance in N
    setattr(vehicle.LDS.sim_acc.resistance, 'F_m', F_m)         # acceleration resistance in N
    setattr(vehicle.LDS.sim_acc.resistance, 'F_tot', F_d)       # driving force in N

    # Marker traction limit:
    setattr(vehicle.LDS.sim_acc, 'traction_lim', traction_limit_vec[0:i])                       # Vector with the traction limits
    setattr(vehicle.LDS.sim_acc, 'exceeded_traction_limit', exceeded_traction_limit_sim_acc)    # Marker, to be used later for ErrorLog

    # endregion

    return vehicle
