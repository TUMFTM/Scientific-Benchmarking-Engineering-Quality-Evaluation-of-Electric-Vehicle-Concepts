"""
Description:  This function calculates the weight of the accessories of the vehicle.
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
Output: The vehicle structure updated with the mass of the accessories
------------

Implementation
[0] Import modules, classes and functions
[1] Initialize the variables
[2] Emergency equipment
[3] Comfort and ADAS
[4] Tow hitch
[5] Assign output
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
# endregion


def calc_accessories_weight(vehicle, parameters):
    # region [1] Initialize the variables
    # Tire and rim dimensions
    tire_diameter = vehicle.dimensions.CX.wheel_f_diameter                  # in mm
    tire_width = vehicle.dimensions.CY.wheel_f_width                        # in mm
    rim_diameter_in_inches = vehicle.dimensions.CX.rim_diameter_f_inch      # in inches

    # Optional extras (1= Optional extra is present; 0=Optional extra is not present)
    ACC = vehicle.masses.optional_extras.ACC                    # Active Cruise Control
    BMS = vehicle.masses.optional_extras.BSM                    # Blind Spot Monitor
    PA = vehicle.masses.optional_extras.park_assist             # Park Assist System
    ST = vehicle.masses.optional_extras.spare_tire              # Spare Tire (if built)
    NV = vehicle.masses.optional_extras.night_vision            # Night vision
    LKS = vehicle.masses.optional_extras.LKS                    # Lane Keeping Support Camera
    KL = vehicle.masses.optional_extras.keyless                 # Keyless opening
    TA = vehicle.masses.optional_extras.trunk_assist            # Trunk Assist System
    PC = vehicle.masses.optional_extras.phone_connectivity      # Phone connectivity
    TH = vehicle.masses.optional_extras.tow_hitch               # Tow hitch

    # Regressions for the mass calculation of EE components
    regr_tire_coeff = parameters.regr.mass.tire.coefficients
    regr_rim_coeff = parameters.regr.mass.rim.coefficients
    regr_spare_wheel_coeff = parameters.regr.mass.spare_wheel.coefficients
    # endregion

    # region [2] Emergency equipment
    # mass of standard vehicle wheel
    standard_wheel_weight = regr_tire_coeff[0] + regr_tire_coeff[1] * tire_width + regr_tire_coeff[2] * tire_diameter + \
                            regr_rim_coeff[0] + regr_rim_coeff[1] * rim_diameter_in_inches

    # spare wheel (if present) and toolbox: warning triangle, first aid, equipment to change/repair tire
    if ST == 1:
        spare_wheel_weight = regr_spare_wheel_coeff[0] + regr_spare_wheel_coeff[1] * standard_wheel_weight
        toolbox_weight = parameters.masses.toolbox.car_jack + parameters.masses.toolbox.container + \
                         parameters.masses.toolbox.first_aid + parameters.masses.toolbox.jack_crank + \
                         parameters.masses.toolbox.nut_tool + parameters.masses.toolbox.screwdriver + \
                         parameters.masses.toolbox.storage_bag + parameters.masses.toolbox.tire_compressor + \
                         parameters.masses.toolbox.tow_hook + parameters.masses.toolbox.wheel_lock
    else:
        spare_wheel_weight = 0
        toolbox_weight = parameters.masses.toolbox.container + parameters.masses.toolbox.first_aid + \
                         parameters.masses.toolbox.nut_tool + parameters.masses.toolbox.screwdriver + \
                         parameters.masses.toolbox.storage_bag + parameters.masses.toolbox.tire_compressor + \
                         parameters.masses.toolbox.tire_sealant + parameters.masses.toolbox.tow_hook + \
                         parameters.masses.toolbox.wheel_lock
    # endregion

    # region [3] Comfort and ADAS
    # pedestrian warning, always present on BEVs. Constant value for speakers and support.
    pedestrian_warning = parameters.masses.AVAS

    # park assist with cameras f/r (if present)
    if PA == 1:
        park_assist_weight = parameters.masses.park_assist
    else:
        park_assist_weight = 0

    # ADAS control unit (if ADAS are present)
    if ACC == 1 or BMS == 1 or LKS == 1 or NV == 1:
        ADAS_ECU = parameters.masses.ADAS_ECU
    else:
        ADAS_ECU = 0

    # Adaptive cruise control (if present): radar+supports
    if ACC == 1:
        ACC_weight = parameters.masses.ACC_radar
    else:
        ACC_weight = 0

    # Blind spot monitoring (if present): 2 short range radars
    if BMS == 1:
        BSM_weight = parameters.masses.BSM
    else:
        BSM_weight = 0

    # Lane Keeping Support Camera (if present)
    if LKS == 1:
        LKS_weight = parameters.masses.lane_assist
    else:
        LKS_weight = 0

    # Control Unit for Keyless entry (if present)
    if KL == 1:
        Keyless_weight = parameters.masses.keyless_system
    else:
        Keyless_weight = 0

    # Night vision camera (if present)
    if NV == 1:
        night_vision_weight = parameters.masses.night_vision
    else:
        night_vision_weight = 0

    # Sensors for kick to open tailgate (if present)
    if TA == 1:
        trunk_assist_weight = parameters.masses.trunk_opening_sensor
    else:
        trunk_assist_weight = 0

    # Wireless charge pad and wifi hotspot (if present)
    if PC == 1:
        phone_connectivity_weight = parameters.masses.phone_wifi + parameters.masses.phone_wireless_charge
    else:
        phone_connectivity_weight = 0
    # endregion

    # region [4] Tow hitch
    # Includes hitch and frame reinforcements
    if TH == 1:
        tow_hitch_weight = parameters.masses.tow_system
    else:
        tow_hitch_weight = 0
    # endregion

    # region [5] Assign output
    # Total the mass of the accessories. this value corresponds to the mass of the entire module
    masses_accessories = pedestrian_warning + spare_wheel_weight + park_assist_weight + toolbox_weight + \
                         ACC_weight + BSM_weight + LKS_weight + ADAS_ECU + Keyless_weight + night_vision_weight + \
                         trunk_assist_weight + phone_connectivity_weight+tow_hitch_weight
    setattr(vehicle.masses, 'accessories', masses_accessories)
    # endregion

    return vehicle, parameters
