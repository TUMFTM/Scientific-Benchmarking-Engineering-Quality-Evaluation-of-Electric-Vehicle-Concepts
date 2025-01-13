"""
Description: According to the given topology (front-, rear-, or all-wheel-drive),
             the needed values for the dimensioning of the E-Machine and the gearbox
             are stored in the respective classes.
             On each axle there is the opportunity for zero, one or two machines
             -'X'   : Zero machines at the corresponding axle
             -'GM'  : One machine at the corresponding axle
             -'2G2M': Two machines at the corresponding axle
------------
Sources: (1) K. Moller, „Validierung einer MATLAB Längsdynamiksimulation für die Auslegung von Elektrofahrzeugen,“ Bachelor thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2020.
         (2) K. Moller, „Antriebsstrangmodellierung zur Optimierung autonomer Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
------------
Input: vehicle: Stores all the information of the computed vehicle
       parameters: Stores the constant values and regressions for volume and mass models
------------
Output: Updated vehicle class with necessary information assigned to the gearbox and e-machine class
------------

Implementation
[0] Import modules, classes and functions
[1] General function of computing the machines topology
[1.1] Calculate number of machines per axle
[1.2] Call the respective functions
[2] Computation of rear-axle topology
[2.1] Assign in gearbox transmission and efficiency
[2.2] Assign efficiency of gearbox
[2.3] Check transmission and efficiency
[2.4] Set attributes for rear axle
[3] Computation of front-axle topology
[3.1] Assign in gearbox transmission and efficiency
[3.2] Assign efficiency of gearbox
[3.3] Check transmission and efficiency
[3.4] Set attributes for rear axle
"""

# region [0] Import modules, classes and functions
# Import the modules
import numpy as np
# endregion


# region [1] General function of computing the machines topology
def initialize_topology(vehicle, parameters):
    # Assign the necessary inputs for allocating the correct function
    drive_topology = vehicle.topology.drive  # Front-, rear-, or all-wheel-drive
    topology = vehicle.topology.topology     # e.g. 'GM_X' for a front-wheel-drive with ohne machine at the front axle

    # region [1.1] Calculate number of Machines per axle
    split_topology = str.split(topology, '_')       # Divide the topology into front and rear axle
    axles = ['front', 'rear']                       # Define the axles
    num_EM = {'front': 0, 'rear': 0}                # Initialize the number of machines for both axles

    if len(split_topology) == len(axles):
        for i in range(0, len(split_topology)):
            if split_topology[i] != 'X':                    # An 'X' means that there is no machine
                count_GM = split_topology[i].count('2')     # Count the number of machines
                if count_GM > 0:
                    num_EM[axles[i]] = 2
                else:
                    num_EM[axles[i]] = 1
    else:  # There is something wrong with the topology
        raise Exception("THIS IS NOT A POSSIBLE POWERTRAIN TOPOLOGY: PLEASE CHECK IN THE EXCEL SHEET")
    # endregion

    # region [1.2] Call the respective functions
    if drive_topology == 'RWD':         # Rear-wheel-drive
        vehicle, parameters = initialize_topology_RWD(vehicle, parameters, num_EM['rear'])
        filled_axles = {'front': False, 'rear': True}
    elif drive_topology == 'FWD':       # Front-Wheel-drive
        vehicle, parameters = initialize_topology_FWD(vehicle, parameters, num_EM['front'])
        filled_axles = {'front': True, 'rear': False}
    elif drive_topology == 'AWD':       # All-Wheel-drive
        vehicle, parameters = initialize_topology_RWD(vehicle, parameters, num_EM['rear'])
        vehicle, parameters = initialize_topology_FWD(vehicle, parameters, num_EM['front'])
        filled_axles = {'front': True, 'rear': True}
    else:
        raise Exception("NO VALID DRIVE TOPOLOGY WAS USED: HAS TO BE EITHER: \'RWD\', \'FWD\' or \'AWD\'")
    setattr(vehicle.topology, 'filled_axles', filled_axles)
    # endregion

    return vehicle, parameters
# endregion


# [2] Computation of rear-axle topology
def initialize_topology_RWD(vehicle, parameters, num_EM):
    # Designed by: Lorenzo Nicoletti (FTM, Technical University of Munich), Korbinian Moller, Ruben Hefele
    # Updated by: Moritz Fundel
    # -------------
    # Created on: 09.05.2023
    # ------------
    # Description: This function initializes a powertrain configuration on the rear axle.
    # ------------
    # Input: vehicle: Stores all the information of the computed vehicle
    #        parameters: Stores the constant values and regressions for volume and mass models
    #        num_EM: Number of E-Machines on the rear_axle
    # ------------
    # Output: Filled gearbox and e-machine classes for the rear axle of the vehicle
    # ------------

    # Implementation:
    # region [2.1] Assign in gearbox transmission and efficiency
    if num_EM == 1:
        # A topology with only one central E-Machine needs a differential
        i_differential = parameters.LDS.i_differential
        eta_differential = parameters.LDS.eta_differential
        quantity = 1            # Number of electrical machines
    elif num_EM == 2:
        # In a topology with an E-Machine per wheel the differential is not necessary (differential function can be executed by the machine)
        i_differential = 1      # Not necessary, can be set to 1 for the multiplication
        eta_differential = 1    # Not necessary, can be set to 1 for the multiplication
        quantity = 2            # Number of electrical machines
    else:   # Not a valid entry
        raise Exception("NOT A VALID NUMBER OF ELECTRICAL MASCHINES. HAS TO BE EITHER \'1\' or \'2\'")
    setattr(vehicle.gearbox['rear'].Input, 'i_tot', vehicle.Input.i_gearbox_r * i_differential)   # gear ratio
    # endregion

    # region [2.2] Assign efficiency of gearbox
    if hasattr(vehicle.Input, 'eta_gearbox_r') and not np.isnan(vehicle.Input.eta_gearbox_r):
        eta_gearbox = vehicle.Input.eta_gearbox_r * eta_differential
    else:
        eta_gearbox = parameters.LDS.eta_gearbox * eta_differential
    setattr(vehicle.gearbox['rear'], 'eta', eta_gearbox)
    # endregion

    # region [2.3] Check transmission and efficiency
    # Get the length of the transmission and the efficiency of the gearbox (Try statement is
    # necessary because they might be a single number)
    try:
        len_transmission = len(vehicle.gearbox['rear'].Input.i_tot)
    except TypeError:
        len_transmission = 1
    try:
        len_efficiency = len(vehicle.gearbox['rear'].eta)
    except TypeError:
        len_efficiency = 1

    # check if required inputs are given
    if len_transmission != len_efficiency:
        raise Exception("GEARBOX CAN\'T BE COMPUTED BECAUSE ETA AND TRANSMISSION VARIABLES DO NOT HAVE THE SAME LENGTH")
    # endregion

    # region [2.4] Set attributes for rear axle
    type_machine = vehicle.Input.machine_type_r

    # If the machine is a FSM because of the lack of data it is assumed, that the FSM and PSM have similar factors
    # for the inertia, the overload factor and overload time
    if type_machine == 'FSM':
        type_machine_load = 'PSM'
    else:
        type_machine_load = type_machine

    J_M = getattr(parameters.LDS.inertia, type_machine_load)                    # inertia of motor and gearbox in kg m^2
    overload_factor = getattr(parameters.LDS.overload_factor, type_machine_load)      # overload factor E-Machine
    overload_duration = getattr(parameters.LDS.overload_duration, type_machine_load)  # overload duration E-Machine
    setattr(vehicle.e_machine['rear'], 'type', type_machine)                    # ASM or PSM or FSM
    setattr(vehicle.e_machine['rear'], 'T_max', vehicle.Input.T_max_Mot_r)      # machine torque in Nm
    setattr(vehicle.e_machine['rear'], 'quantity', quantity)                    # quantity of motors on rear axis
    setattr(vehicle.e_machine['rear'], 'J_M', J_M)
    setattr(vehicle.e_machine['rear'], 'overload_factor', overload_factor)
    setattr(vehicle.e_machine['rear'], 'overload_duration', overload_duration)
    # endregion

    return vehicle, parameters


def initialize_topology_FWD(vehicle, parameters, num_EM):
    # Designed by: Lorenzo Nicoletti (FTM, Technical University of Munich), Korbinian Moller, Ruben Hefele
    # Updated by: Moritz Fundel
    # -------------
    # Created on: 09.05.2023
    # ------------
    # Description: This function initializes a powertrain configuration on the front axle.
    # ------------
    # Input: vehicle: Stores all the information of the computed vehicle
    #        parameters: Stores the constant values and regressions for volume and mass models
    #        num_EM: Number of E-Machines on the front axle
    # ------------
    # Output: Filled gearbox and e-machine classes for the front axle of the vehicle
    # ------------

    # Implementation:
    # region [3.1] Assign in gearbox transmission and efficiency
    if num_EM == 1:
        # A topology with only one central E-Machine needs a differential
        i_differential = parameters.LDS.i_differential
        eta_differential = parameters.LDS.eta_differential
        quantity = 1            # Number of electric machines
    elif num_EM == 2:
        # In a topology with an E-Machine per wheel the differential is not necessary (differential function can be executed by the machine)
        i_differential = 1      # Not necessary, can be set to 1 for the multiplication
        eta_differential = 1    # Not necessary, can be set to 1 for the multiplication
        quantity = 2            # Number of electric machines
    else:   # No valid entry
        raise Exception("NOT A VALID NUMBER OF ELECTRICAL MASCHINES. HAS TO BE EITHER \'1\' or \'2\'")

    setattr(vehicle.gearbox['front'].Input, 'i_tot', vehicle.Input.i_gearbox_f * i_differential)    # gear ratio

    # region [3.2] Assign efficiency of gearbox
    if hasattr(vehicle.Input, 'eta_gearbox_f') and not np.isnan(vehicle.Input.eta_gearbox_f):
        eta_gearbox = vehicle.Input.eta_gearbox_f * eta_differential                # efficiency of gearbox
    else:
        eta_gearbox = parameters.LDS.eta_gearbox * eta_differential      # efficiency of gearbox
    setattr(vehicle.gearbox['front'], 'eta', eta_gearbox)
    # endregion

    # region [2.3] Check transmission and efficiency
    # Get the length of the transmission and the efficiency of the gearbox (Try statement is necessary
    # because they might be a single number)
    try:
        len_transmission = len(vehicle.gearbox['front'].Input.i_tot)
    except TypeError:
        len_transmission = 1
    try:
        len_efficiency = len(vehicle.gearbox['front'].eta)
    except TypeError:
        len_efficiency = 1

    # check if required inputs are given
    if len_transmission != len_efficiency:
        raise Exception("GEARBOX CAN\'T BE COMPUTED BECAUSE ETA AND TRANSMISSION VARIABLES DO NOT HAVE THE SAME LENGTH")
    # endregion

    # region [3.4] Set attributes for rear axle
    type_machine = vehicle.Input.machine_type_f

    # If the machine is a FSM because of the lack of data it is assumed, that the FSM and PSM have similar factors
    # for the inertia, the overload factor and overload time
    if type_machine == 'FSM':
        type_machine_load = 'PSM'
    else:
        type_machine_load = type_machine

    J_M = getattr(parameters.LDS.inertia, type_machine_load)                    # inertia of motor and gearbox in kg m^2
    overload_factor = getattr(parameters.LDS.overload_factor, type_machine_load)         # overload factor motor
    overload_duration = getattr(parameters.LDS.overload_duration, type_machine_load)     # overload duration motor
    setattr(vehicle.e_machine['front'], 'type', type_machine)                   # ASM or PSM or FSM
    setattr(vehicle.e_machine['front'], 'T_max', vehicle.Input.T_max_Mot_f)     # machine torque in Nm
    setattr(vehicle.e_machine['front'], 'quantity', quantity)                   # quantity of motors on front axis
    setattr(vehicle.e_machine['front'], 'J_M', J_M)
    setattr(vehicle.e_machine['front'], 'overload_factor', overload_factor)
    setattr(vehicle.e_machine['front'], 'overload_duration', overload_duration)
    # endregion
    return vehicle, parameters
