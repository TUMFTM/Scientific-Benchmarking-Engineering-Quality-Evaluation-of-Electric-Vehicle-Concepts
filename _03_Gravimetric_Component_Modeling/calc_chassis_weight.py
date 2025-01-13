"""
Description: This function calculates the total weight of the chassis. The chassis is
             defined as the sum of brakes, brake calipers and pads, rims, tires, shock
             absorber, coil springs and axles weight.
             Air suspension and all wheel steering toggles in set_veh_options
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
Output: The vehicle structure updated with the mass of the chassis components
------------

Implementation
[0] Import modules, classes and functions
[1] Initialize the variables
[2] Weight of brake system
[3] Weight of rims and tires
[4] Front Axle weight complete
[5] Rear Axle weight complete
[6] Additional components for air suspensions
[7] Steering system weight
[8] Assign outputs
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
# endregion

def calc_chassis_weight(vehicle, parameters):
    # region [1] Initialize the variables
    rim_diameter_in_inches = vehicle.dimensions.CX.rim_diameter_f_inch      # in inches
    tire_diameter = vehicle.dimensions.CX.wheel_f_diameter                  # in mm
    tire_width = vehicle.dimensions.CY.wheel_f_width                        # in mm
    wheelbase = vehicle.dimensions.GX.wheelbase                             # in mm
    width = vehicle.dimensions.GY.vehicle_width                             # in mm
    gross_weight = vehicle.masses.vehicle_max_weight                        # in kg
    gross_load_front_axle = vehicle.masses.axle_load_f_max                  # in kg
    gross_load_rear_axle = gross_weight-gross_load_front_axle               # in kg

    # Optional extras of the vehicle:
    air_susp = vehicle.masses.optional_extras.AS            # 1: air suspension; 0: no air suspensions
    rear_steering = vehicle.masses.optional_extras.AWS      # 1: rear steering; 0: no rear steering

    # Regression and constant values for the mass calculation of chassis components
    regr_rim_coeff = parameters.regr.mass.rim.coefficients
    regr_tire_coeff = parameters.regr.mass.tire.coefficients
    regr_brakes_front_coeff = parameters.regr.mass.front_wheel_brakes.coefficients
    regr_brakes_rear_coeff = parameters.regr.mass.rear_wheel_brakes.coefficients
    regr_axles_front_links_coeff = parameters.regr.mass.front_axle_links.coefficients
    regr_axles_front_SD_coeff = parameters.regr.mass.front_axle_SD.coefficients
    regr_axles_rear_ML_links_coeff = parameters.regr.mass.rear_axle_links_ML.coefficients
    regr_axles_rear_SD_coeff = parameters.regr.mass.rear_axle_SD.coefficients
    regr_axles_rear_TB_coeff = parameters.regr.mass.rear_axle_TB.coefficients
    regr_steering_system_coeff = parameters.regr.mass.steering.coefficients
    # endregion

    # region [2] Weight of brake system
    # Calculate the mass of the front wheel brakes (brake discs, calipers and pads) from the vehicle's gross weight
    brakes_front_weight = regr_brakes_front_coeff[0] + regr_brakes_front_coeff[1] * gross_weight

    # Calculate the mass of the rear wheel brakes (brake discs, calipers and pads) from the mass of the front wheel brakes
    brakes_rear_weight = regr_brakes_rear_coeff[0] + regr_brakes_rear_coeff[1] * brakes_front_weight

    # Total mass of brake components in the wheel (contribute to unsprung mass)
    wheel_brakes_weight = brakes_front_weight + brakes_rear_weight

    # ABS system as constant value
    ABS_system_weight = parameters.masses.ABS_system

    # Brake lines as constant value
    brake_lines_weight = parameters.masses.brake_lines_system

    # Master cylinder as constant value
    master_cylinder_weight = parameters.masses.master_cylinder

    # Parking brake actuators as constant value
    parking_actuators_weight = parameters.masses.parking_brake_actuators

    # Brake fluid as constant value
    brake_fluid_weight = parameters.masses.brake_fluid

    # Brake hoses as constant value (for all four brakes)
    brake_hoses_weight = 2 * parameters.masses.brake_hose

    # Brake disc covers as constant value (for all four brakes)
    disc_covers_weight = 2 * parameters.masses.brake_disc_cover

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if brakes_front_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The front brakes mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    if brakes_rear_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The rear brakes mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    # Sum the additional brake components
    additional_brake_components = ABS_system_weight + brake_lines_weight + master_cylinder_weight + \
                                  parking_actuators_weight + brake_fluid_weight + brake_hoses_weight + \
                                  disc_covers_weight
    # endregion

    # region [3] Weight of rims and tires
    # Weight of the four rims in kg
    rims_weight = (regr_rim_coeff[0] + regr_rim_coeff[1] * rim_diameter_in_inches) * 4

    # Weight of the four tires in kg
    tires_weight = (regr_tire_coeff[0] + regr_tire_coeff[1] * tire_width + regr_tire_coeff[2] * tire_diameter) * 4

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if rims_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The rim mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    if tires_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The tire mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)
    # endregion

    # region [4] Front Axle weight complete
    # The front axle is computed separately from its spring-damper assembly.
    # This approach allows distinguishing between vehicles with and without air
    # suspension. The spring-damper assembly is calculated differently.
    # Spring-damper assembly NO AS: steel spring and damper.
    # Spring-damper assembly AS: air spring and damper.
    # The weight of the axle includes suspension arms, anti-roll bar, subframe and wheel hubs.
    # No geometry distinction
    if air_susp == 0:   # no air suspension
        weight_front_axle_arms = regr_axles_front_links_coeff[0] + regr_axles_front_links_coeff[1] * \
                                 gross_load_front_axle + regr_axles_front_links_coeff[2] * width
        weight_front_axle_shockabs = regr_axles_front_SD_coeff[0] + regr_axles_front_SD_coeff[1] * \
                                     gross_load_front_axle
    else:   # with air suspension
        weight_front_axle_arms = regr_axles_front_links_coeff[0] + regr_axles_front_links_coeff[1] * \
                                 gross_load_front_axle + regr_axles_front_links_coeff[2] * width
        weight_front_axle_shockabs = parameters.masses.front_AS

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if weight_front_axle_arms < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The front axle arm mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    if weight_front_axle_shockabs < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The front axle shock absorber mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)
    # endregion

    # region [5] Rear Axle weight complete
    # We need to distinguish between Torsion beam and multilink axles
    # The mass of the torsion beam is calculated along with its spring-damper assembly
    # The mass of the axle comprises control arms, subframe, anti-roll bar and wheel hubs.
    # Multilink suspensions can have air suspension. As for the front axle, the
    # mass of the spring-damper assembly is calculated differently based on this distinction.
    if vehicle.topology.axis_type_r.lower() == 'torsion_beam':
        weight_rear_axle = regr_axles_rear_TB_coeff[0] + regr_axles_rear_TB_coeff[1] * gross_weight
    else:    # Multi link
        if air_susp == 0:   # without air suspensions
            weight_rear_axle = regr_axles_rear_ML_links_coeff[0] + regr_axles_rear_ML_links_coeff[1] * \
                               gross_weight + regr_axles_rear_ML_links_coeff[2] * width + \
                               regr_axles_rear_SD_coeff[0] + regr_axles_rear_SD_coeff[1] * gross_load_rear_axle
        else:
            weight_rear_axle = regr_axles_rear_ML_links_coeff[0] + regr_axles_rear_ML_links_coeff[1] * \
                               gross_weight + regr_axles_rear_ML_links_coeff[2] * width + parameters.masses.rear_AS

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if weight_rear_axle < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The rear axle mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)
    # endregion

    # region [6] Additional components for air suspensions
    # This section calculates the weight of the on-board components of the suspension system.
    # These are air bottles, compressor, distributor. Masses include supports and protections

    if air_susp == 1:
        # add weight of additional components
        air_bottle_weight = parameters.masses.AS_air_bottle
        compressor_weight = parameters.masses.AS_compressor
        distributor_weight = parameters.masses.AS_distributor

    else:
        air_bottle_weight = 0
        compressor_weight = 0
        distributor_weight = 0

    additional_weight_AS = air_bottle_weight + compressor_weight + distributor_weight
    # endregion

    # region [7] Steering system weight
    # The mass of the steering system includes the steering shaft assembly, the
    # steering wheel (without airbag), the steering rack assembly and the tie rods.
    # If the vehicle is equipped with all-wheel-steering, the weight of the
    # rear actuation motor and tie rods is included.

    weight_steering = regr_steering_system_coeff[0] + regr_steering_system_coeff[1] * gross_weight + \
                      regr_steering_system_coeff[2] * wheelbase
    if rear_steering == 1:   # add weight of rear axle steering
        weight_steering = weight_steering + parameters.masses.rear_axle_steering

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if weight_steering < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The steering mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)
    # endregion

    # region [8] Assign outputs
    # All the outputs are in kg
    setattr(vehicle.masses.chassis, 'wheel_brakes_weight', wheel_brakes_weight)
    setattr(vehicle.masses.chassis, 'additional_brake_components_weight', additional_brake_components)
    setattr(vehicle.masses.chassis, 'rims_weight', rims_weight)
    setattr(vehicle.masses.chassis, 'tires_weight', tires_weight)
    setattr(vehicle.masses.chassis, 'rear_axle_weight', weight_rear_axle)
    setattr(vehicle.masses.chassis, 'front_axle_weight', weight_front_axle_arms + weight_front_axle_shockabs)
    setattr(vehicle.masses.chassis, 'steering_weight', weight_steering)
    setattr(vehicle.masses.chassis, 'air_susp_weight', additional_weight_AS)
    # endregion

    return vehicle, parameters
