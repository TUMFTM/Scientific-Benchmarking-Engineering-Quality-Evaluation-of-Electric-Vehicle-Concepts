"""
Description: This function calculates the total weight of the electric (Low Voltage)
             and electronic(High Voltage) components.
             The LV contains the LV battery and its cables, the LV wiring throughout the vehicle,
             the fuses box and the vehicle ECUs.
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
Output:  The vehicle structure updated with the mass of the electrics (EE) components
------------

Implementation
[0] Import modules, classes and functions
[1] Initialize the variables
[2] Weight of LV components
[3] Weight of HV components
[4] Weight of plugin system
[5] Assign output
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
import numpy as np
# endregion


def calc_EE_weight(vehicle, parameters):
    # region [1] Initialize the variables
    wheelbase = vehicle.dimensions.GX.wheelbase             # Wheelbase in mm
    battery_voltage = vehicle.battery.battery_voltage       # The total nominal voltage of the battery in V
    gross_energy = vehicle.battery.energy_is_gross_in_kWh   # The gross energy of the battery, in kWh

    # Regressions for the mass calculation of EE components
    regr_LV_wiring_coeff = parameters.regr.mass.LV_wiring_harness.coefficients
    regr_HV_cables_coeff = parameters.regr.mass.HV_cables.coefficients
    regr_DCDC_converter_coeff = parameters.regr.mass.DC_DC_converter.coefficients
    regr_HV_charger_coeff = parameters.regr.mass.HV_charger.coefficients
    # endregion

    # region [2] Weight of LV components
    # Includes: 12V battery and cables, fuse box, wires throughout the vehicle leading to the vehicle ECUs.
    # LV battery and its cables
    low_voltage_battery_weight = parameters.masses.LV_battery + parameters.masses.LV_battery_cables

    # Fuse box
    fuse_box_weight = parameters.masses.fuse_box

    # LV wiring
    LV_wiring_weight = regr_LV_wiring_coeff[0] + regr_LV_wiring_coeff[1] * wheelbase

    # Other LV components
    additional_LV_weight = parameters.masses.additional_LV_components

    # Check that the result is not negative (this may happen if the inputs are outside of the regression confidence interval)
    if LV_wiring_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The Low-Volt wiring mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    LV_components_weight = low_voltage_battery_weight + fuse_box_weight + LV_wiring_weight + additional_LV_weight
    # endregion

    # region [3] Weight of HV components
    # HV cables
    HV_wiring_weight = regr_HV_cables_coeff[0] + regr_HV_cables_coeff[1] * wheelbase

    # DC/DC converter and supports
    DC_DC_converter_weight = regr_DCDC_converter_coeff[0] + regr_DCDC_converter_coeff[1] * battery_voltage
    DC_DC_converter_support_weight = parameters.masses.DCDC_converter_supports

    # HV charger with supports
    HV_charger_weight = regr_HV_charger_coeff[0] + regr_HV_charger_coeff[1] * gross_energy + \
                        parameters.masses.HV_charger_support

    # Inverters: Constant value computed for one inverter with its supports
    Inverter_weight = parameters.masses.inverter + parameters.masses.inverter_protection + \
                      parameters.masses.inverter_supports

    # Inverters: One inverter for each E-machine
    inverters_weight = np.zeros(2)
    for axle, (key, value) in enumerate(vehicle.topology.filled_axles.items()):
        if value is True:
            quantity = vehicle.e_machine[key].quantity
            inverters_weight[axle] = Inverter_weight * quantity

    # sum the weight of the inverters
    inverters_weight = np.sum(inverters_weight)

    # Account for other HV components like cable brackets and electric unit control
    additional_HV_components = parameters.masses.additional_HV_components

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if HV_wiring_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The High-Volt wiring mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    if DC_DC_converter_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The DC-DC-Converter mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    if HV_charger_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The High-Volt charging mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    if inverters_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The Inverter mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    # Add up all HV components
    HV_components_weight = HV_wiring_weight + DC_DC_converter_weight + DC_DC_converter_support_weight + \
                           HV_charger_weight + inverters_weight + additional_HV_components
    # endregion

    # region [4] Weight of plugin system
    # This section calculates the weight of the plug-in system, i.e. AC charging cables, DC charging plug
    # and cables to charger and battery, and other components like charging port supports, covers, lids, trim pieces,
    # and power connectors.

    # Home AC charging cable 3kW and fast AC charging cable for public charging stations
    AC_charging_cables_weight = parameters.masses.home_charging_cable + parameters.masses.public_charging_cable

    # Charging plug with cables to HV charger and battery
    charging_plug_weight = parameters.masses.charging_plug

    # Additional charging components (charging port lid, supports etc.)
    additional_charging_weight = parameters.masses.additional_charging_plug_components

    # Add up all plug-in components
    plugin_components_weight = AC_charging_cables_weight + charging_plug_weight + additional_charging_weight
    # endregion

    # region [5] Assign Outputs
    # All outputs in kg
    setattr(vehicle.masses.EE, 'LV_weight', LV_components_weight)
    setattr(vehicle.masses.EE, 'HV_weight', HV_components_weight)
    setattr(vehicle.masses.EE, 'plugin_sys_weight', plugin_components_weight)
    # endregion

    return vehicle, parameters
