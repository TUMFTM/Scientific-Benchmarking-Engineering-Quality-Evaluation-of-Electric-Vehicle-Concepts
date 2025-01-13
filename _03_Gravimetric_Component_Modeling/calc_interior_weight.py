"""
Description: This function calculates the total weight of the interior. The interior is
             defined as the sum of Airbags, center console, door panels, HVAC,
             instrument panel, noise insulation material, seatbelts, seats, speakers, trim parts
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
Output: The vehicle structure updated with the mass of the interior components
------------

Implementation
[0] Import modules, classes and functions
[1] Initialize the variables
[2] Weight of safety equipment (EU spec)
[3] Weight of seats
[4] Weight of pedals
[5] Weight of HVAC
[6] Weight of center console
[7] Weight of instrument panel
[8] Weight of noise insulation material
[9] Weight of trim parts
[10] Weight of speakers
[11] Assign Output
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
# endregion


def calc_interior_weight(vehicle, parameters):
    # region [1] Initialize the variables
    wheelbase = vehicle.dimensions.GX.wheelbase             # in mm
    width = vehicle.dimensions.GY.vehicle_width             # in mm
    veh_length = vehicle.dimensions.GX.vehicle_length       # in mm
    seating_capacity = vehicle.topology.number_of_seats     # [/]

    # Options
    cluster_type = vehicle.masses.optional_extras.cluster_type
    infotainment = vehicle.masses.optional_extras.infotainment
    HUD = vehicle.masses.optional_extras.HUD
    rear_seats = vehicle.masses.optional_extras.rear_seats
    rear_bench_sliding = vehicle.masses.optional_extras.sliding_rear_bench
    subwoofer = vehicle.masses.optional_extras.subwoofer

    # Regressions for the mass calculation of interior components
    regr_front_seat_coeff = parameters.regr.mass.front_seat.coefficients
    regr_rear_bench_coeff = parameters.regr.mass.rear_seat_bench.coefficients
    regr_third_seat_row_coeff = parameters.regr.mass.third_seat_row.coefficients
    regr_heating_system_cabin_coeff = parameters.regr.mass.heating_system_cabin.coefficients
    regr_center_console_coeff = parameters.regr.mass.center_console.coefficients
    regr_trim_parts_coeff = parameters.regr.mass.trims.coefficients
    # endregion

    # region [2] Weight of safety equipment (EU spec)
    # The weight of the airbags is divided into: driver's airbag, passenger's airbag,
    # knee airbag, curtain airbag and rear side airbag.
    airbag_sensors_weight = parameters.masses.airbag_sensors
    airbag_driver_weight = parameters.masses.airbag_driver
    airbag_passenger_weight = parameters.masses.airbag_passenger
    airbag_knee_weight = parameters.masses.airbag_knee
    airbag_curtain_weight = parameters.masses.airbag_curtain

    # Rear side airbags
    if seating_capacity > 2:
        airbag_rear_side_weight = parameters.masses.airbag_rear_side
    else:
        airbag_rear_side_weight = 0

    # Airbag control unit
    airbag_CU_weight = parameters.masses.airbag_CU

    # total airbag_weight
    airbag_weight = airbag_sensors_weight + airbag_driver_weight + airbag_passenger_weight + 2 * airbag_knee_weight + \
                    airbag_curtain_weight + airbag_rear_side_weight + airbag_CU_weight

    # Weight of seatbelts
    seatbelt_front_weight = 2 * parameters.masses.seatbelt_driver
    seatbelt_rear_weight = (seating_capacity - 2) * parameters.masses.seatbelt_rear
    seatbelts_weight = seatbelt_front_weight + seatbelt_rear_weight

    # Horn system
    horn_weight = parameters.masses.horn_system

    # Add up all safety equipment
    safety_equipment_weight = airbag_weight + seatbelts_weight + horn_weight
    # endregion

    # region [3] Weight of seats
    front_seats_weight = 2 * (regr_front_seat_coeff[0] + regr_front_seat_coeff[1] * width +
                              regr_front_seat_coeff[2] * wheelbase)

    if 2 < seating_capacity <= 5:
        if rear_seats.lower() == 'bench':   # Bench seats
            rear_seats_weight = regr_rear_bench_coeff[0] + regr_rear_bench_coeff[1] * width + \
                                regr_rear_bench_coeff[2] * wheelbase

            if rear_bench_sliding == 1:     # additional weight sliding mechanism rear seat bench
                rear_seats_weight = rear_seats_weight + parameters.masses.bench_sliding_mechanism        # [kg]

        else:                                   # individual seats
            rear_seats_weight = (seating_capacity - 2) * (front_seats_weight * 0.5)

    elif seating_capacity > 5:  # 7 seater
        if rear_seats.lower() == 'bench':   # 2nd row Bench seats + 3rd row bench
            rear_seats_weight = regr_rear_bench_coeff[0] + regr_rear_bench_coeff[1] * width + \
                                regr_rear_bench_coeff[2] * wheelbase + \
                                regr_third_seat_row_coeff[0] + regr_third_seat_row_coeff[1] * veh_length

            if rear_bench_sliding == 1:     # additional weight sliding mechanism rear seat bench
                rear_seats_weight = rear_seats_weight + parameters.masses.bench_sliding_mechanism

        else:                               # 2nd row individual seats + 3rd row bench
            rear_seats_weight = (seating_capacity - 4) * (front_seats_weight * 0.5) + \
                                regr_third_seat_row_coeff[0] + regr_third_seat_row_coeff[1] * veh_length

    else:  # 2 seater
        rear_seats_weight = 0

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if front_seats_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The front seat mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    if rear_seats_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The rear seat mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    # Total seat mass
    seats_weight = front_seats_weight + rear_seats_weight
    # endregion

    # region [4] Weight of pedals
    pedals_weight = parameters.masses.brake_pedal + parameters.masses.drive_pedal
    # endregion

    # region [5] Weight of HVAC
    # A/C: Condenser, compressor, A/C lines and valves+refrigerant.
    AC_weight = parameters.masses.AC_system + parameters.masses.AC_refrigerant

    # Heating system: Air vents, blowing unit system, radiator, evaporator,
    # temp. sensors, filters, air intakes, resistors, defrosters
    heating_weight = regr_heating_system_cabin_coeff[0] + regr_heating_system_cabin_coeff[1] * wheelbase + \
                     regr_heating_system_cabin_coeff[2] * width

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if heating_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The heating system mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

    HVAC_weight = AC_weight + heating_weight
    # endregion

    # region [6] Weight of center console
    # Center console includes Structure, cupholders, parking brake switch, storage compartments
    center_console_weight = regr_center_console_coeff[0] + regr_center_console_coeff[1] * wheelbase

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if center_console_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The center console mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)
    # endregion

    # region [7] Weight of instrument panel
    # Dashboard and dashboard covers
    dashboard_weight = parameters.masses.dashboard

    # Cluster system (if present): instrument cluster in front of the driver
    if cluster_type == 1:   # digital instrument cluster
        cluster_weight = parameters.masses.cluster_system.digital
    else:                   # analog
        cluster_weight = parameters.masses.cluster_system.analog

    # Cross Car beam
    cross_car_beam_weight = parameters.masses.cross_car_beam

    # LCD screen (if present) in the center of the dashboard. Includes screen and Hardware weight
    if infotainment == 1:
        infotainment_weight = parameters.masses.infotainment
    else:
        infotainment_weight = 0

    # Head up display (if present) in the driver's field of view
    if HUD == 1:
        HUD_weight = parameters.masses.HUD
    else:
        HUD_weight = 0

    # glovebox storage compartment with lid.
    glovebox_weight = parameters.masses.glovebox

    instrument_panel_weight = dashboard_weight + cluster_weight + cross_car_beam_weight + \
                              infotainment_weight + HUD_weight + glovebox_weight
    # endregion

    # region [8] Weight of noise insulation material
    # mean value based based on the segment (the segment division is made based on the wheelbase)
    if wheelbase <= 2750:   # segments A to C
        noise_ins_weight = parameters.masses.noise_insulation.A_to_C
    else:                   # larger wheelbase-->segments D to F
        noise_ins_weight = parameters.masses.noise_insulation.D_to_F
    # endregion

    # region [9] Weight of trim parts
    # interior trim covers on pillars, roof, floor
    trim_parts_weight = regr_trim_parts_coeff[0] + regr_trim_parts_coeff[1] * width + \
                        regr_trim_parts_coeff[2] * veh_length

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if trim_parts_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The trim parts mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)
    # endregion

    # region [10] Weight of speakers
    speakers_weight = parameters.masses.speaker.dashboard + 2 * parameters.masses.speaker.front + \
                      2 * parameters.masses.speaker.rear

    # if a subwoofer is present, a constant value is added to the speaker's weight.
    if subwoofer == 1:
        speakers_weight = speakers_weight + parameters.masses.speaker.subwoofer
    # endregion

    # region [11] Assign Output
    # All outputs are in kg
    setattr(vehicle.masses.interior, 'safety_equipment_weight', safety_equipment_weight)
    setattr(vehicle.masses.interior, 'center_console_weight', center_console_weight)
    setattr(vehicle.masses.interior, 'HVAC_weight', HVAC_weight)
    setattr(vehicle.masses.interior, 'instrument_panel_weight', instrument_panel_weight)
    setattr(vehicle.masses.interior, 'noise_insulation_weight', noise_ins_weight)
    setattr(vehicle.masses.interior, 'seats_weight', seats_weight)
    setattr(vehicle.masses.interior, 'speakers_weight', speakers_weight)
    setattr(vehicle.masses.interior, 'trim_parts_weight', trim_parts_weight)
    setattr(vehicle.masses.interior, 'pedals_weight', pedals_weight)
    # endregion

    return vehicle, parameters
