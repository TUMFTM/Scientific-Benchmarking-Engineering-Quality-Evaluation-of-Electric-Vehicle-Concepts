"""
Description: This function calculates the total weight of the powertrain. The powertrain is
             defined as the sum of battery, electric machines, gearboxes
             ALL THE GIVEN MASSES ARE CALCULATED IN KG

             All the models were first created in the work of Romano (2),
             and then further detailed in another publication (3) and in
             the Ph.D. thesis (1). A complete overview of the models is available at the
             Appendix E and at the chapter 3.5 of the Ph. D thesis (1)
------------
Sources: (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", Technical University of Munich, Institute of Automotive Technology, 2022
         (2) A. Romano, „Data-based Analysis for Parametric Weight Estimation of new BEV Concepts,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
         (3) L. Nicoletti, A. Romano, A. König, P. Köhler, M. Heinrich and M. Lienkamp, „An Estimation of the Lightweight Potential of Battery Electric Vehicles,“ Energies, vol. 14, no. 15, p. 4655, 2021, DOI: 10.3390/en14154655.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The vehicle structure updated with the mass of the powertrain components
------------

Implementation
[0] Import modules, classes and functions
[1] Initialize the variables
[2] Calculate the weight of the battery in kg
[3] Calculate the weight of the electric machines in kg
[4] Calculate the weight of the gearbox in kg (with oil)
[5] Calculate weight of cooling system in kg (with coolant fluid)
[6] Calculate resulting weights
[7] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
# Import functions
from _01_Volumetric_Component_Modeling.Gearbox.Lay_shaft.calc_mass_laysh import calc_mass_laysh
from _01_Volumetric_Component_Modeling.Gearbox.Lay_shaft.calc_J_laysh import calc_J_laysh
from _01_Volumetric_Component_Modeling.Gearbox.Planetary.calc_mass_planetary import calc_mass_planetary
from _01_Volumetric_Component_Modeling.Gearbox.Planetary.calc_J_planetary import calc_J_planetary
from _01_Volumetric_Component_Modeling.Gearbox.calc_mass_driveshaft import calc_mass_driveshaft
from .calc_battery_weight import calc_battery_weight
# Import modules
import numpy as np
# endregion


def calc_powertrain_weight(vehicle, parameters):
    # region [1] Initialize the variables
    # Regressions for the mass calculation of powertrain components
    regr_ASM_coeff = parameters.regr.mass.ASM.coefficients
    regr_PSM_coeff = parameters.regr.mass.PSM.coefficients
    regr_pw_cooling_coeff = parameters.regr.mass.powertrain_cooling.coefficients

    # Initialize all the necessary array as numpy zeros
    power = np.zeros(2)
    EM_weight = np.zeros(2)
    gearbox_weight = np.zeros(2)
    driveshaft_weight = np.zeros(2)
    oil_weight = np.zeros(2)
    # endregion

    # region [2] Calculate the weight of the battery in kg
    vehicle, parameters = calc_battery_weight(vehicle, parameters)
    # endregion

    # region [3] Calculate the weight of the electric machines in kg
    # Noise insulation for the electric machine
    noise_insulation_weight = parameters.masses.noise_insulation_powertrain

    # Mounting structure for each machine (does not include the housing!)
    EM_mounts_weight = parameters.masses.EM_mounts

    # Iterate through the front and rear axle
    for axle, (key, value) in enumerate(vehicle.topology.filled_axles.items()):

        if value is True:

            machine_type = vehicle.e_machine[key].type
            T_max = vehicle.e_machine[key].T_max                # in Nm
            quantity = vehicle.e_machine[key].quantity
            power[axle] = vehicle.e_machine[key].P_max_mech     # in kW

            match machine_type:
                case 'ASM':     # Asynchronous E-Machine
                    machine_weight = regr_ASM_coeff[0] + regr_ASM_coeff[1] * T_max

                case 'PSM':    # Permanent magnet synchronous
                    machine_weight = regr_PSM_coeff[0] + regr_PSM_coeff[1] * T_max
                case _:        # FSM but with the same configuration as the PSM
                    machine_weight = regr_PSM_coeff[0] + regr_PSM_coeff[1] * T_max

            EM_weight[axle] = (machine_weight + noise_insulation_weight + EM_mounts_weight) * quantity

            setattr(vehicle.e_machine[key], 'weight', EM_weight[axle]/quantity)

    power_tot = np.sum(power)
    # endregion

    # region [4] Calculate the weight of the gearbox in kg (with oil)
    # Mass of the gearbox, the shaft and the oil contained in it
    gearbox_oil_weight = parameters.masses.transmission_fluid

    # Multiply by the number of electric machines on each axle and distinguish
    # gearbox type and construction
    for axle, (key, value) in enumerate(vehicle.topology.filled_axles.items()):

        if value is True:

            gearbox = vehicle.gearbox[key]
            quantity = vehicle.e_machine[key].quantity
            e_machine_length = vehicle.e_machine[key].CY_e_machine_length

            if gearbox.Input.type.lower() == 'lay-shaft':
                # Calculation of gearbox mass in kg (parallel and coaxial design)
                gearbox = calc_mass_laysh(gearbox, parameters)

                # Calculation of gearbox moment of inertia in kg*mm^2 (parallel and coaxial design)
                gearbox = calc_J_laysh(gearbox, parameters)
                gearbox = calc_mass_driveshaft(gearbox, parameters, e_machine_length)

            elif gearbox.Input.type.lower() == 'planetary':
                # Calculation of gearbox mass in kg
                gearbox = calc_mass_planetary(gearbox, parameters)

                # Calculation of moment of inertia in kg*mm^2
                gearbox = calc_J_planetary(gearbox, parameters)
                gearbox = calc_mass_driveshaft(gearbox, parameters, e_machine_length)

            gearbox_weight[axle] = gearbox.masses.m_tot * quantity

            # weight of two driveshafts per axle
            driveshaft_weight[axle] = gearbox.masses.m_driveshaft

            # add oil weight
            oil_weight[axle] = gearbox_oil_weight * quantity

    # endregion

    # region [5] Calculate weight of cooling system in kg (with coolant fluid)
    # If the vehicle has an AWD topology, more coolant is needed, since more machine have to be cooled
    if vehicle.topology.filled_axles['front'] is True and vehicle.topology.filled_axles['rear'] is True:    # AWD
        pw_coolant = parameters.masses.coolant.AWD
    else:   # RWD or FWD
        pw_coolant = parameters.masses.coolant.FWDorRWD

    cooling_weight = regr_pw_cooling_coeff[0] + regr_pw_cooling_coeff[1] * power_tot + pw_coolant

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if cooling_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The cooling mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)
    # endregion

    # region [6] Calculate resulting weights
    # Output motor and transmission weights at front and rear axle. If the vehicle is an FWD or RWD the
    # component mass of the other axle are summed to zero
    gearbox_weight_front = gearbox_weight[0] + driveshaft_weight[0] + oil_weight[0]
    motor_weight_front = EM_weight[0]
    gearbox_weight_rear = gearbox_weight[1] + driveshaft_weight[1] + oil_weight[1]
    motor_weight_rear = EM_weight[1]
    # endregion

    # region [7] Assign Outputs
    setattr(vehicle.masses.powertrain, 'gearbox_weight_front', gearbox_weight_front)
    setattr(vehicle.masses.powertrain, 'motor_weight_front', motor_weight_front)
    setattr(vehicle.masses.powertrain, 'gearbox_weight_rear', gearbox_weight_rear)
    setattr(vehicle.masses.powertrain, 'motor_weight_rear', motor_weight_rear)
    setattr(vehicle.masses.powertrain, 'cooling_weight', cooling_weight)
    # endregion

    return vehicle, parameters
