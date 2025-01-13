"""
Description: This  functions creates a list with the deviations of the real vehicle and the simulated digital reference
             vehicle. The list will then be transformed into a dataframe and printed out
------------
Sources:
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       benchmarking: Stores the Benchmarking values of the corresponding vehicle
------------
Output: deviations: Deviations of certain vehicle parameters between real vehicle and simulated digital reference model
------------

Implementation
[0] Import modules, classes and functions
[1] Calculate max power deviations
[2] Calculate deviation of t 0-100
[3] Calculate consumption deviation
[4] Calculate mass deviation
[5] Calculate range deviation
[6] Calculate battery capacity deviation
[7] Calculate trunk volume deviation
[8] Calculate charge time deviation
[9] Calculate mean charge power deviation
[10] Calculate slalom velocity deviation
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
# endregion

def get_comparison_list(vehicle, benchmarking):
    # region [1] Calculate max power deviations
    # FWD
    if vehicle.topology.drive == 'FWD':
        P_max_real = benchmarking.performance.P_max_Mot_f
        P_max_calc = vehicle.e_machine['front'].P_max_mech

    # RWD
    elif vehicle.topology.drive == 'RWD':
        P_max_real = benchmarking.performance.P_max_Mot_r
        P_max_calc = vehicle.e_machine['rear'].P_max_mech

    elif vehicle.topology.drive == 'AWD':
        P_max_real = benchmarking.performance.P_max_Mot_f + benchmarking.performance.P_max_Mot_r
        P_max_calc = vehicle.e_machine['front'].P_max_mech + vehicle.e_machine['rear'].P_max_mech
    else:
        raise Exception("Machine data missing! Please check input Excel for missing or wrong machine type or torque entries!")

    # noinspection PyUnboundLocalVariable
    dev_Pmax = (P_max_calc - P_max_real)/P_max_real * 100
    text_Pmax = str(round(P_max_calc, 2)) + ' kW (' + str(round(dev_Pmax, 2)) + ' %)'
    # endregion

    # region [2] Calculate deviation of t 0-100
    t0100_real = benchmarking.performance.acceleration_time
    t0100_calc = vehicle.LDS.sim_acc.acc_time_is
    dev_t0100 = ((t0100_calc - t0100_real)/t0100_real) * 100
    text_t0100 = str(round(t0100_calc, 2)) + ' s (' + str(round(dev_t0100, 2)) + ' %)'
    # endregion

    # region [3] Calculate consumption deviation
    cons_real = benchmarking.performance.consumption_WLTP
    cons_calc = vehicle.LDS.sim_cons.consumption100km
    dev_cons = (cons_calc - cons_real)/cons_real * 100
    text_cons = str(round(cons_calc, 2)) + ' kWh/100km (' + str(round(dev_cons, 2)) + ' %)'
    # endregion

    # region [4] Calculate mass deviation
    mass_real = vehicle.masses.vehicle_empty_weight
    mass_calc = vehicle.masses.vehicle_empty_weight_sim
    dev_mass = (mass_calc - mass_real)/mass_real * 100
    text_mass = str(round(mass_calc, 2)) + ' kg (' + str(round(dev_mass, 2)) + ' %)'
    # endregion

    # region [5] Calculate Range deviation
    range_calc = vehicle.LDS.sim_range.range
    range_real = benchmarking.performance.range
    dev_range = (range_calc - range_real)/range_real * 100
    text_range = str(round(range_calc, 2)) + ' km (' + str(round(dev_range, 2)) + ' %)'
    # endregion

    # region [6] Calculate battery capacity deviation
    capa_calc = vehicle.battery.energy_is_net_in_kWh
    capa_real = benchmarking.performance.battery_net_energy
    dev_capa = (capa_calc - capa_real)/capa_real * 100
    text_capa = str(round(capa_calc, 2)) + ' kWh (' + str(round(dev_capa, 2)) + ' %)'
    # endregion

    # region [7] Calculate trunk volume deviation
    trunk_calc = vehicle.dimensions.volume_trunk
    trunk_real = benchmarking.comfort.trunk_volume_ADAC
    dev_trunk = (trunk_calc - trunk_real)/trunk_real * 100
    text_trunk = str(round(trunk_calc, 2)) + ' l (' + str(round(dev_trunk, 2)) + ' %)'
    # endregion

    # region [8] Calculate charge time deviation
    charge_calc = vehicle.battery.charging.total_time
    # Get benchmarking of the charging time based on the ev-database
    charge_real = benchmarking.performance.charging_time.EV_database

    dev_charge = (charge_calc - charge_real)/charge_real * 100
    text_charge = str(round(charge_calc, 2)) + ' min (' + str(round(dev_charge, 2)) + ' %)'
    # endregion

    # region [9] Calculate mean charge power deviation
    charge_power_mean_calc = vehicle.battery.charging.power_mean
    charge_power_mean_real = vehicle.battery.charging.power_mean_ev_database
    dev_charge_power_mean = (charge_power_mean_calc-charge_power_mean_real)/charge_power_mean_real * 100
    text_charge_power_mean = str(round(charge_power_mean_calc, 2)) + ' kW (' + str(round(dev_charge_power_mean, 2)) + ' %)'
    # endregion

    # region [10] Calculate slalom velocity deviation
    slalom_calc = vehicle.Lateral_Dynamics.v_slalom
    slalom_real = benchmarking.performance.slalom
    dev_slalom = (slalom_calc - slalom_real) / slalom_real * 100
    text_slalom = str(round(slalom_calc, 2)) + ' km/h (' + str(round(dev_slalom, 2)) + ' %)'
    # endregion

    deviations = [text_Pmax, text_t0100, text_cons, text_capa, text_range, text_mass, text_trunk, text_charge,
                  text_charge_power_mean, text_slalom]

    return deviations
