"""
Description: For the sim_acc the torque is automatically scaled according to the
             required acceleration time or the max simulation time. In the case of the
             consumption simulation it has to be checked whether the cycle is doable for
             the motor or not. If not, the motor torque has to be scaled.
             Regarding the rotational speed, the function check_n_max makes sure, that
             the motor has the required rotational speed for the cycle, i.e. only the
             torque has to be checked in the function check_torque_sim_cons.
------------
Sources: More information regarding the implementation of the LDS functions is available at:
         (1) K. Moller, „Validierung einer MATLAB Längsdynamiksimulation für die Auslegung von Elektrofahrzeugen,“ Bachelor thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2020.
         (2) K. Moller, „Antriebsstrangmodellierung zur Optimierung autonomer Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
------------
Output: vehicle struct with checked torque
------------

Implementation
[0] Import modules, classes and functions
[1] Implementation
[2] Assign Output
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
import math
# Import functions
# endregion


def check_torque_sim_cons(vehicle, directory):
    # region [1] Implementation
    # Find which axles are filled: [front_axle, rear_axle]
    filled_axles = vehicle.topology.filled_axles

    check_torque = list()

    for axle, (key, value) in enumerate(filled_axles.items()):
        if value is True:

            if key.lower() == 'front':

                # torque and speed of a single motor (calculated in calc_power)
                n_mot = directory.n_mot_f
                T_mot = directory.T_mot_f

            else:
                # torque and speed of a single motor (calculated in calc_power)
                n_mot = directory.n_mot_r
                T_mot = directory.T_mot_r

            # Mechanical Power needed for the motor:
            P_mech_required = np.abs((n_mot * math.pi/30) * T_mot * math.pow(10, -3))

            # Maximum mechanical power provided by the machine
            P_max_mot = vehicle.e_machine[key].P_max_mech

            # Find operation points where the needed power is higher than the provided power
            idx = np.where(P_mech_required > P_max_mot)

            if np.size(idx) != 0:
                # Define Errorlog
                errorlog_list = vehicle.errorlog
                text_errorlog = 'The machine at the' + key + 'axle can\'t generate the necessary mechanical power for the driving cycle'
                print(text_errorlog)
                errorlog_list.append(text_errorlog)
                setattr(vehicle, 'errorlog', errorlog_list)


                check_torque.append(0)
            else:
                check_torque.append(1)
    # endregion

    # region [2] Assign Outputs
    if sum(check_torque) == len(check_torque):
        # Every motor has sufficient power to successfully complete the drive cycle
        check_output = 1
    else:
        # There is at least one motor which does not provide enough power to complete the drive cycle
        check_output = 0
    # endregion

    return check_output, vehicle
