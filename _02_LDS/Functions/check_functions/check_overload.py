"""
Description: This function identifies the time steps, where the motor is in overload.
             This function also calculates the maximum time, where the motor is in
             overload and compares it with the motor overload duration.
------------
Sources: More information regarding the implementation of the LDS functions is available at:
         (1) K. Moller, „Validierung einer MATLAB Längsdynamiksimulation für die Auslegung von Elektrofahrzeugen,“ Bachelor thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2020.
         (2) K. Moller, „Antriebsstrangmodellierung zur Optimierung autonomer Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
       T_mot: Torque at the motor (in Nm)
       n_mot: rotational speeed (in 1/min) at the motor
       axle: Axle identifier ('front' for front and 'rear' for rear)
------------
Output: Operating point of motors and their power, as well as the battery power
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Calculate the highest overload duration
[3] Check overload duration
[3.1] Create the vector to plot the  overload duration
[4] Error log and assign Output
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
from scipy import interpolate as ip
# Import functions
# endregion


def check_overload(vehicle, parameters, T_mot, n_mot, axle):
    # region [1] Assign Inputs
    # Assign overload factor and duration from Par
    machine_type = vehicle.e_machine[axle].type

    # Only overload factors for ASM and PSM are available. Because of the similarities between PSM and FSM, there
    # overload factor is assumed to be equal.
    if machine_type == 'ASM':
        overload_type = 'ASM'
    else:
        overload_type = 'PSM'

    overload_factor = getattr(parameters.LDS.overload_factor, overload_type)
    overload_duration = getattr(parameters.LDS.overload_duration, overload_type)
    # endregion

    # region [2] Calculate the highest overload duration
    # Max amount of timestep where the motor can be in overload
    max_time_steps = overload_duration/vehicle.LDS.sim_cons.delta_t

    # Interpolate to find the characteristic line of the motor when not overloaded
    n_characteristic = vehicle.e_machine[axle].characteristic[:, 1]
    T_characteristic = vehicle.e_machine[axle].characteristic[:, 0]

    F = ip.interp1d(n_characteristic, T_characteristic/overload_factor, kind='linear', axis=0)

    # Calculate maximum torque in the no-overload zone
    T_max = F(n_mot)

    # If the required torque is bigger than T_max, the motor is in overload
    Is_overload = T_mot > T_max

    # Convert into the Trues into 1 and the False into 0
    Is_overload = Is_overload.astype(int)

    # Vector which resume how many zeros and ones are contained and in which sequence
    help_array = np.where(np.diff(Is_overload))[0]

    # The -1 is necessary to because of the Python zero indexing
    overload_seq = np.diff(np.concatenate(([-1], help_array, [np.size(Is_overload)-1])))

    # Get size of overload sequence (necessary for the np.arrange module to include the last step)
    if np.size(overload_seq) == 1:
        size_seq = 1
    else:
        size_seq = np.size(overload_seq)
    if Is_overload[0] == 0:

        overload_id = np.arange(1, size_seq, 2)
        overload_vec = np.zeros(overload_seq[0])
    else:
        overload_id = np.arange(0, size_seq, 2)
        overload_vec = np.ones(overload_seq[0])
    # endregion

    # region [3] Check overload duration
    # Find maximum amount of time steps where the motor is continuously in overload
    if np.size(overload_id) == 0:
        max_time = 0
    else:
        max_time = np.max(overload_seq[overload_id])

    if max_time > max_time_steps:     # Check if the motor does not exceed the allowed overload duration

        # overload Vec is assigned, needed in clear_struct
        overload_vec = np.nan
        # The motor has been in overload for an amount of time, which is higher than the overload duration
        if axle == 'front':
            # Define errorlog
            errorlog_list = vehicle.errorlog
            text_errorlog = 'The motor at the front axle is in overload for an amount of time, which is higher than the permitted overload duration'
            print(text_errorlog)
            errorlog_list.append(text_errorlog)
            setattr(vehicle, 'errorlog', errorlog_list)

        else:
            # Define errorlog
            errorlog_list = vehicle.errorlog
            text_errorlog = 'The motor at the rear axle is in overload for an amount of time, which is higher than the permitted overload duration'
            print(text_errorlog)
            errorlog_list.append(text_errorlog)
            setattr(vehicle, 'errorlog', errorlog_list)

    else:   # Check more precisely that the motor does not exceed overload point, see explanation section 2)

        # region [3.1] Create the vector to plot the  overload duration
        # While the motor is in overload, it gradually gets warmer. For this reason,
        # if the motor stays for 30s in overload (30s being the max overload duration) and
        # then one second in non overload, it does not mean that then it can stay
        # other 30s in overload, as that one second is not sufficient to cool the motor down.
        # Here the authors suppose that every second of
        # "heating", i.e. overload, can be compensated by one second of cooling,
        # i.e. non overload. This vector is needed to evaluate this characteristic:
        # At every overload point a +1 is assigned, at every non overload point a -1 is
        # assigned, then the cumulative sum is created, while the total sum cannot go
        # under 0.

        for ii in overload_id:

            overload_vec = np.concatenate((overload_vec, np.ones(overload_seq[ii])))

            cum_overload = np.cumsum(overload_vec)

            overload_is = cum_overload[-1]

            try:

                if overload_is - overload_seq[ii + 1] > 0:

                    overload_vec = np.concatenate((overload_vec, np.ones(overload_seq[ii + 1]) * (-1)))

                else:
                    overload_vec = np.concatenate((overload_vec, (-1) * np.ones(int(overload_is)), np.zeros(int(overload_seq[ii + 1] - overload_is))))
            except IndexError:
                break

        # Cumulative sum of the overload vec
        overload_vec = np.cumsum(overload_vec)

        # Maximum time, taking into account the required cooling time!
        max_time = np.max(overload_vec)

        if max_time > max_time_steps:     # Check if the motor does not exceed the allowed overload duration

            # The motor has been in overload for an amount of time, which is higher than the overload duration
            if axle == 'front':
                # Define errorlog
                errorlog_list = vehicle.errorlog
                text_errorlog = 'The motor at the front axle is in overload for an amount of time, which is higher than the permitted overload duration'
                print(text_errorlog)
                errorlog_list.append(text_errorlog)
                setattr(vehicle, 'errorlog', errorlog_list)

            else:
                # Define errorlog
                errorlog_list = vehicle.errorlog
                text_errorlog = 'The motor at the rear axle is in overload for an amount of time, which is higher than the permitted overload duration'
                print(text_errorlog)
                errorlog_list.append(text_errorlog)
                setattr(vehicle, 'errorlog', errorlog_list)
        # endregion
    # endregion

    # region [4] Assign Outputs:
    if axle == 'front':
        str_time = 'max_overload_time_in_cycle_mot_f'
        str_vec = 'overload_vector_mot_f'
    else:
        str_time = 'max_overload_time_in_cycle_mot_r'
        str_vec = 'overload_vector_mot_r'

    setattr(vehicle.LDS.sim_cons, str_time, max_time)           # in s
    setattr(vehicle.LDS.sim_cons, str_vec, overload_vec)        # in [-]
    # endregion

    return vehicle
