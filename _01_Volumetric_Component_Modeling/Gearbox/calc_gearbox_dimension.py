"""
Description:    This function computes the dimensions of the gearboxes based on the selected efficiency map
------------
Sources:    None
------------
Input:   vehicle: Class element which stores all the vehicle information
         parameters: Class element which stores all necessary computation parameters
         key: Switch between the front and the rear axle
------------
Output:  Object element for a machine
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Assign all the inputs
[2] Check if Inputs are valid
[3] Calculate gearbox dimensions
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
import numpy as np
# Import classes
# Import methods
# endregion


def calc_gearbox_dimension(vehicle, parameters, key):
    # Assign the gearbox
    gearbox = vehicle.gearbox[key]

    # region [1]: Assign all the inputs
    type_e_machine = vehicle.e_machine[key].type
    setattr(gearbox.Input, 'T_max', vehicle.e_machine[key].T_max)  # Maximum torque of el.motor[Nm]

    # Nominal torque of el.motor[Nm]
    overload_factor = vehicle.e_machine[key].overload_factor
    setattr(gearbox.Input, 'overload_factor', overload_factor)
    setattr(gearbox.Input, 'T_nom', gearbox.Input.T_max/overload_factor)

    # Diameter of el.motor[mm]
    setattr(gearbox.Input, 'd_mot',  vehicle.e_machine[key].CX_e_machine_diameter)

    setattr(gearbox.Input, 'type', vehicle.Input.gearbox_type[key])
    setattr(gearbox.Input, 'axles', vehicle.Input.gearbox_axles[key])

    # Number of machine on the considered axle(front or rear axle).If there are 2
    # Machines(one per wheel) the differential is not required and won 't be calculated
    setattr(gearbox.Input, 'num_EM', vehicle.e_machine[key].quantity)

    if hasattr(gearbox.Input, 'opt_gears') == 0:
        setattr(gearbox.Input, 'opt_gears', 'Manual')  # Optimization goal(Height / Length / Mass / Manual)
    setattr(gearbox.Input, 'inc_init',  0)  # Angle between shafts with manual selection[deg]
    setattr(gearbox.Input, 'manTR', 0)

    # Nominal engine speed from the engine characteristics in rpm
    motor_characteristic = vehicle.e_machine[key].characteristic    # Vector containing the torque curve of the machine
    T_max = round(max(motor_characteristic[:, 0]), 4)               # Maximum torque of the machine in Nm
    idx = np.where(motor_characteristic[:, 0].round(4) == T_max)[0]
    setattr(gearbox.Input, 'n_nom', motor_characteristic[idx[-1], 1])

    # Pressure angle in transverse section[rad]
    alpha_t = math.atan(math.tan(parameters.gearbox.GearingConst.alpha_n)) / math.cos(parameters.gearbox.GearingConst.beta)
    setattr(parameters.gearbox.GearingConst, 'alpha_t', alpha_t)

    setattr(parameters.gearbox.GearingConst, 'epsilon_beta', 2)  # Desired overlap ratio[-]

    # Base helix angle of first stage[rad]
    beta_b = math.acos(math.sin(parameters.gearbox.GearingConst.alpha_n)) / math.sin(parameters.gearbox.GearingConst.alpha_t)
    setattr(parameters.gearbox.GearingConst, 'beta_b', beta_b)

    # Lifetime factor regarding differential shaft speed[10 ^ 6 revolutions]
    L10 = parameters.gearbox.CalcFactors.L_10h * 60 * gearbox.Input.n_nom / math.pow(10, 6)
    setattr(parameters.gearbox.CalcFactors, 'L_10', L10)

    # region [2]: Check if Inputs are valid
    # Check number of E-machines
    if gearbox.Input.num_EM not in (1, 2):
        raise Exception("The vehicle can only have exactly one or exactly two e-machines.")
    if gearbox.Input.type.lower() not in ('lay-shaft', 'planetary'):
        raise Exception("The gearbox\' type has to be either lay-shaft or planetary")
    if gearbox.Input.axles.lower() not in ('parallel', 'coaxial'):
        raise Exception("The lay shaft configuration of the gearbox must be either parallel or coaxial")
    # endregion

    # region [3]: Calculate gearbox dimensions
    # Distinguish between planetary and lay shaft gearboxes
    if gearbox.Input.type.lower() == 'lay-shaft':
        # Calculation of lay - shaft gearbox parameters

        from .Lay_shaft.set_layshaft_transmission import set_layshaft_transmission
        from .Lay_shaft.calc_dimensions import calc_dimensions
        gearbox = set_layshaft_transmission(gearbox, parameters)

        # Calculation of gearbox main dimensions in mm
        gearbox = calc_dimensions(gearbox, parameters)

    elif gearbox.Input.type.lower() == 'planetary':
        from .Planetary.set_planetary_transmission import set_planetary_transmission
        from .Planetary.calc_dimensions_plan import calc_dimensions_plan

        # Calculation of planetary gearbox parameters
        gearbox = set_planetary_transmission(gearbox, parameters)

        # Calculation of gearbox main dimensions in mm
        gearbox = calc_dimensions_plan(gearbox, parameters)

    return gearbox
