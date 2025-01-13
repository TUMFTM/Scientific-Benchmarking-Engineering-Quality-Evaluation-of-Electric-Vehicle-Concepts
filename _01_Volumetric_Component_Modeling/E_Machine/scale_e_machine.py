"""
Description:  This function scales the torque and rotational speed of the selected e-machine
              Implementation of the scaling function described in (1).
              k_length describes the scaling factor alpha in (1)
              After that it is check if the e-machine can absolve the loaded drive cycle. For the computation of
              the consumption of All-wheel-drives it is necessary that both machines have sufficient rotational
              speed
------------
Sources:   (1) Pries and Hofmann, "Magnetic and thermal scaling of electric machines", 2013
           (2) Rosenberger et al., "Scientific benchmarking: Engineering quality evaluation of electric vehicle concepts", e-Prime - Advances in Electrical Engineering, Electronics and Energy 9, 2024
           (3) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
------------
Input: vehicle: Class element, which stores all values of the vehicle
       key: Key describing the concerned axles (front or rear)
------------
Output: Scaled electric machine values
------------
Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Scale the characteristics
[3] Scale the diagram function
[4] Check motor speed
[5] Assign Output
------------
"""

# region [0] Import modules, classes and functions
# import modules
import math
import numpy as np
# import functions
# endregion


def scale_e_machine(vehicle, key):
    # region [1] Assign Inputs
    e_machine = vehicle.e_machine[key]

    # Target values
    if key.lower() == 'front':
        T_max = vehicle.Input.T_max_Mot_f
    else:
        T_max = vehicle.Input.T_max_Mot_r

    # values of e-machine
    characteristic = e_machine.characteristic
    T_unscaled = e_machine.diagram.T_unscaled
    n_unscaled = e_machine.diagram.n_unscaled

    # Comparison values from the driving cycle
    i_gearbox = vehicle.gearbox[key].Input.i_tot                    # transmission at corresponding axle
    n_wheel_max = vehicle.LDS.parameters.n_wheel_max_cycle          # maximum wheel speed by the cycle

    # Especially for machines with high torque the scaling approach may lead into a low rotational speed. To avoid that
    # the vehicle won't pass the driving cycle a deviation is added in case the rotational speed is too low.
    deviation_n_wheel = 0.035           # Deviation to overcome potentially low rotational speed [3, p.49-50]
    # endregion

    # region [2] Scale the characteristics
    # Find detailed description in [1] and [3, p. 44-50]
    trq_origin = characteristic[:, 0]
    rpm_origin = characteristic[:, 1]
    pwr_origin = characteristic[:, 2]

    T_max_origin = max(trq_origin)  # Maximum torque of the reference machine

    # Calculate scaling factor k_length: T_new = (k_length^3) * T_old
    k_dimensions = T_max/T_max_origin
    k_length = math.pow(k_dimensions, (1/3))

    # Scale torque and rotational speed
    trq_rescaled = k_dimensions * trq_origin
    rpm_rescaled = rpm_origin * 1/math.pow(k_length, 2)

    # Scale power
    pwr_rescaled = 2 * math.pi * trq_rescaled * rpm_rescaled * 1/(60 * math.pow(10, 3))

    n_max = max(rpm_rescaled)
    # endregion

    # region [3] Scale the diagram function
    n_scaled = n_unscaled * 1/math.pow(k_length, 2)
    T_scaled = T_unscaled * math.pow(k_length, 3)
    # endregion

    # region [4] Check motor speed
    # Check if n_max of the motor is sufficient for absolving the cycle [3, p.48-50]
    n_mot_cycle_max = n_wheel_max * i_gearbox                           # Maximum motor speed of the cycle

    n_mot_cycle_max = n_mot_cycle_max * (1 + deviation_n_wheel)         # Consider the deviation

    if n_mot_cycle_max > n_max:
        # Rescale the e_machine such that the maximum cycle speed can be achieved
        k_dimensions = n_max/n_mot_cycle_max
        k_length_rescale = math.sqrt(k_dimensions)

        # Rescale rotational speed and torque
        rpm_rescaled = rpm_rescaled * 1/math.pow(k_length_rescale, 2)
        trq_rescaled = trq_rescaled * math.pow(k_length_rescale, 3)

        # Rescale machine power
        pwr_rescaled = 2 * math.pi * trq_rescaled * rpm_rescaled * 1/(60 * math.pow(10, 3))

        n_max = max(rpm_rescaled)

        # Scale the diagram function
        n_scaled = n_scaled * 1/math.pow(k_length_rescale, 2)
        T_scaled = T_scaled * math.pow(k_length_rescale, 3)

        # Compute total k_length by considering the necessary downsacling factor
        k_length = k_length * k_length_rescale
    # endregion

    # region [5] Assign Output
    T_max = max(trq_rescaled)                           # Define maximum torque
    P_max_mech = max(pwr_rescaled)                      # Define maximum electric machine power
    characteristic = np.column_stack((trq_rescaled, rpm_rescaled, pwr_rescaled))

    # Set attributes
    setattr(e_machine, 'characteristic', characteristic)
    setattr(e_machine, 'n_max', n_max)
    setattr(e_machine, 'T_max', T_max)
    setattr(e_machine, 'P_max_mech', P_max_mech)

    setattr(e_machine.diagram, 'n_scaled', n_scaled)
    setattr(e_machine.diagram, 'T_scaled', T_scaled)
    setattr(e_machine, 'k_length', k_length)
    # endregion
    return e_machine
