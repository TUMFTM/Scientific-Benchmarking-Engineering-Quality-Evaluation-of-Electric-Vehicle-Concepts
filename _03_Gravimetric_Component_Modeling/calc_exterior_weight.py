"""
Description: This function calculates the total weight of the exterior. The exterior is
             defined as the sum of Closures, Bumpers, Lights, Windshield and windows. Options toggle in set_veh_options
             ALL THE GIVEN MASSES ARE CALCULATED IN KG

             All the models were first created in the work of Romano (2),
             and then further detailed in another publication (3) and in
             the Ph.D. thesis (1). A complete overview of the models is available at the
             Appendix E and at the chapter 3.5 of the Ph. D thesis (1)
------------
Sources: (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", Technical University of Munich, Institute of Automotive Technology, 2022
         (2) A. Romano, „Data-based Analysis for Parametric Weight Estimation of new BEV Concepts,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
         (3) L. Nicoletti, A. Romano, A. König, P. Köhler, M. Heinrich and M. Lienkamp, „An Estimation of the Lightweight Potential of Battery Electric Vehicles,“ Energies, vol. 14, no. 15, p. 4655, 2021, DOI: 10.3390/en14154655.
         (4) E. Elagamy, „Creation of a Parametric Model for the Derivation of the Conceptual Dimensions for Battery Electric Vehicles,“ Master thesis, Institute for Automotive Engineering, RWTH Aachen University, Aachen, 2020.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The vehicle structure updated with the mass of the exterior components
------------

Implementation
[0] Import modules, classes and functions
[1] Initialize the variables
[2] Closures
[3] Bumpers
[4] Fenders
[5] Lights
[6] Windshield and wipers
[7] Assign Output
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
# endregion


def calc_exterior_weight(vehicle, parameters):
    # region [1] Initialize the variables
    wheelbase = vehicle.dimensions.GX.wheelbase             # in mm
    width = vehicle.dimensions.GY.vehicle_width             # in mm
    height = vehicle.dimensions.GZ.vehicle_height           # in mm
    vehicle_form = vehicle.topology.frameform               # SUV, Hatchback or Sedan
    overhang_r = vehicle.dimensions.GX.vehicle_overhang_r   # in mm

    # Further Parameters
    hood_material = vehicle.masses.optional_extras.hood_material            # steel/alu
    doors_material = vehicle.masses.optional_extras.doors_material          # steel/alu
    tailgate_material = vehicle.masses.optional_extras.tailgate_material    # steel/alu
    fenders_material = vehicle.masses.optional_extras.fenders_material      # steel/alu
    headlights_tech = vehicle.masses.optional_extras.headlights_tech        # LED/Xenon and Halogen
    doors_number = vehicle.masses.optional_extras.doors_number              # 4/2
    panoramic_roof = vehicle.masses.optional_extras.panorama_roof           # 1=yes; 0=no
    sliding_roof = vehicle.masses.optional_extras.sliding_roof              # 1=yes; 0=no

    # Regressions for the mass calculation of exterior components
    regr_hood_steel_coeff = parameters.regr.mass.hood.steel.coefficients
    regr_hood_aluminum_coeff = parameters.regr.mass.hood.alu.coefficients
    regr_front_door_steel_coeff = parameters.regr.mass.door_driver.steel.coefficients
    regr_front_door_aluminum_coeff = parameters.regr.mass.door_driver.alu.coefficients
    regr_rear_door_steel_coeff = parameters.regr.mass.door_rear.steel.coefficients
    regr_rear_door_aluminum_coeff = parameters.regr.mass.door_rear.alu.coefficients
    regr_door_2door_coeff = parameters.regr.mass.door_2door.coefficients
    regr_tailgate_steel_coeff = parameters.regr.mass.tailgate.steel.coefficients
    regr_tailgate_aluminum_coeff = parameters.regr.mass.tailgate.alu.coefficients
    regr_front_bumper_coeff = parameters.regr.mass.front_bumper.coefficients
    regr_rear_bumper_coeff = parameters.regr.mass.rear_bumper.coefficients
    regr_headlights_LED_coeff = parameters.regr.mass.headlights.LED.coefficients
    regr_headlights_xenon_coeff = parameters.regr.mass.headlights.xenon.coefficients
    regr_headlights_halogen_coeff = parameters.regr.mass.headlights.halogen.coefficients
    regr_taillights_coeff = parameters.regr.mass.taillights.coefficients
    regr_rear_quarter_glasses_coeff = parameters.regr.mass.quarter_glasses_4door.coefficients
    # endregion

    # region [2] Closures
    # In this section, the mass of hood, doors, and tailgate is calculated.
    # Hood. We distinguish between steel and aluminum.
    if hood_material.lower() == 'steel':
        hood_weight = regr_hood_steel_coeff[0] + regr_hood_steel_coeff[1] * width
    else:   # aluminum
        hood_weight = regr_hood_aluminum_coeff[0] + regr_hood_aluminum_coeff[1] * width

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if hood_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The hood mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    # Doors (2 or 4); Doors weight includes inner panels and windows.
    if doors_number == 4:   # 4 door vehicles.
        if doors_material.lower() == 'steel':
            front_doors_weight = 2 * (regr_front_door_steel_coeff[0] + regr_front_door_steel_coeff[1] *
                                      height + regr_front_door_steel_coeff[2] * wheelbase)
            rear_doors_weight = 2 * (regr_rear_door_steel_coeff[0] + regr_rear_door_steel_coeff[1] *
                                   height + regr_rear_door_steel_coeff[2] * wheelbase)
        else:  # aluminum
            front_doors_weight = 2 * (regr_front_door_aluminum_coeff[0] + regr_front_door_aluminum_coeff[1] *
                                    height + regr_front_door_aluminum_coeff[2] * wheelbase)
            rear_doors_weight = 2 * (regr_rear_door_aluminum_coeff[0] + regr_rear_door_aluminum_coeff[1] *
                                     height + regr_rear_door_aluminum_coeff[2] * wheelbase)

    else:   # 2 doors, no material distinction due to little available data
        front_doors_weight = 2 * (regr_door_2door_coeff[0] + regr_door_2door_coeff[1] * height +
                                 regr_door_2door_coeff[2] * wheelbase)
        rear_doors_weight = 0

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if front_doors_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The front door mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    if rear_doors_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The rear door mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    # Tailgate (SUVs, Hatchbacks) or Trunk (Sedans). Tailgate includes rear window
    if vehicle_form.lower() == 'sedan':  # Trunk: constant values.
        if tailgate_material.lower() == 'steel':       # steel
            tailgate_weight = parameters.masses.trunk_steel
        else:                                           # aluminum
            tailgate_weight = parameters.masses.trunk_alu

    else:  # SUV, SW, hatchback -> Tailgate
        if tailgate_material.lower() == 'steel':        # steel
            tailgate_weight = regr_tailgate_steel_coeff[0] + regr_tailgate_steel_coeff[1] * width + \
                              regr_tailgate_steel_coeff[2] * height
        else:                                           # aluminum
            tailgate_weight = regr_tailgate_aluminum_coeff[0] + regr_tailgate_aluminum_coeff[1] * width + \
                              regr_tailgate_aluminum_coeff[2] * height

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if tailgate_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The tailgate mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    # Add hood, doors and tailgate
    closures_weight = hood_weight + front_doors_weight + rear_doors_weight + tailgate_weight
    # endregion

    # region [3] Bumpers
    # Front bumper
    bumper_front_weight = regr_front_bumper_coeff[0] + regr_front_bumper_coeff[1] * width

    # Rear bumper
    bumper_rear_weight = regr_rear_bumper_coeff[0] + regr_rear_bumper_coeff[1] * width

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if bumper_front_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The front bumper mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    if bumper_rear_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The rear bumper mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    # Sum of front and rear bumper
    bumpers_weight = bumper_front_weight + bumper_rear_weight
    # endregion

    # region [4] Fenders
    # Mostly this weight accounts only for the front fenders, since the rear fenders are usually integrated in the BIW
    if fenders_material.lower() == 'steel':
        fenders_weight = parameters.masses.fenders.steel
    else:    # alu
        fenders_weight = parameters.masses.fenders.alu
    # endregion

    # region [5] Lights
    # Headlights: 3 possibilities: LED, Xenon and Halogen
    match headlights_tech:
        case 'LED':
            headlights_weight = regr_headlights_LED_coeff[0] + regr_headlights_LED_coeff[1] * width

        case 'Xenon':
            headlights_weight = regr_headlights_xenon_coeff[0] + regr_headlights_xenon_coeff[1] * width + \
                                regr_headlights_xenon_coeff[2] * height

        case _:     # Halogen
            headlights_weight = regr_headlights_halogen_coeff[0] + regr_headlights_halogen_coeff[1] * width

    # Taillights
    taillights_weight = regr_taillights_coeff[0] + regr_taillights_coeff[1] * width + regr_taillights_coeff[2] * height

    # 3rd stop light
    stop_light_weight = parameters.masses.stop_light

    # Foglights
    foglights_weight = parameters.masses.fog_lights

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if headlights_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The headlight mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    if taillights_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The taillight mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    # Sum al the lighting components
    lights_weight = headlights_weight+taillights_weight+stop_light_weight + foglights_weight
    # endregion

    # region [6] Windshield and wipers
    # Front windshield wiper (only the wiper blades!) in kg
    front_wipers_weight = parameters.masses.wiper_front

    # Weight of the fluids for the wipers and the washing system (tank, hoses, nozzles)
    wipers_fluid_weight = parameters.masses.washer_fluid + parameters.masses.washer_system

    # Front windshield mean value based on wheelbase intervals (segment) --> see (4)
    if wheelbase <= 2493.12:                            # A Segment
        windshield_weight = parameters.masses.windshield_A
    elif 2493.12 < wheelbase <= 2640.04:                # B Segment
        windshield_weight = parameters.masses.windshield_B
    elif 2640.04 < wheelbase <= 2750.32:                # C Segment
        windshield_weight = parameters.masses.windshield_C
    elif 2750.32 < wheelbase <= 2927.14:                # D Segment
        windshield_weight = parameters.masses.windshield_D
    else:                                               # E Segment
        windshield_weight = parameters.masses.windshield_E_F

    # Rear glass windshield and rear windshield wiper -> Sedans don't have the rear wiper
    if vehicle_form.lower() == 'sedan':  # rear glass not included in the trunk lid
        rear_wipers_weight = 0
        rear_window_weight = parameters.masses.rear_window_sedans
    else:   # weight of rear glass already included in the tailgate. Wiper present.
        rear_wipers_weight = parameters.masses.wiper_rear
        rear_window_weight = 0

    # Quarter glass: Glass between rear door and luggage compartment
    if doors_number < 4:    # 2 door vehicles
        rear_quarter_glasses_weight = parameters.masses.quarter_glasses_2door
    else:
        if vehicle_form.lower() == 'sedan':
            rear_quarter_glasses_weight = parameters.masses.quarter_glasses_sedans
        else:
            rear_quarter_glasses_weight = regr_rear_quarter_glasses_coeff[0] + \
                                          regr_rear_quarter_glasses_coeff[1] * overhang_r

    # Panoramic roof (if present) -> The panoramic roof is fixed and cannot be opened
    if panoramic_roof == 1:
        panoramic_roof_weight = parameters.masses.fixed_glass_roof
    else:
        panoramic_roof_weight = 0

    # Sliding roof -> differently from panoramic roof it can be opened
    if sliding_roof == 1:
        sliding_roof_weight = parameters.masses.sliding_glass_roof
    else:
        sliding_roof_weight = 0

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if rear_quarter_glasses_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The rear quarter glass mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    # sum all components
    windshield_windows_weight = windshield_weight + front_wipers_weight + rear_wipers_weight + rear_window_weight + \
                                rear_quarter_glasses_weight + panoramic_roof_weight + sliding_roof_weight + \
                                wipers_fluid_weight
    # endregion

    # region [7] Assign Output
    # All outputs are expressed in kg
    setattr(vehicle.masses.exterior, 'closures_weight', closures_weight)
    setattr(vehicle.masses.exterior, 'bumpers_weight', bumpers_weight)
    setattr(vehicle.masses.exterior, 'fenders_weight', fenders_weight)
    setattr(vehicle.masses.exterior, 'lights_weight', lights_weight)
    setattr(vehicle.masses.exterior, 'windshield_windows_weight', windshield_windows_weight)
    # endregion

    return vehicle, parameters
