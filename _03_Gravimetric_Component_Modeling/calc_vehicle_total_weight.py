"""
Description: This function calculates the total vehicle weight by adding the weight of each functional module
             The output is the total vehicle weight
             ALL THE GIVEN MASSES ARE CALCULATED IN KG
------------
Sources: (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", Technical University of Munich, Institute of Automotive Technology, 2022
         (2) A. Romano, „Data-based Analysis for Parametric Weight Estimation of new BEV Concepts,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
         (3) L. Nicoletti, A. Romano, A. König, P. Köhler, M. Heinrich and M. Lienkamp, „An Estimation of the Lightweight Potential of Battery Electric Vehicles,“ Energies, vol. 14, no. 15, p. 4655, 2021, DOI: 10.3390/en14154655.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The calculated total vehicle mass in kg
------------

Implementation
[0] Import modules, classes and functions
[1] Initialize necessary variables
[2] Sum elements of chassis
[3] Sum elements of powertrain
[4] Sum elements of interior
[5] Sum elements of exterior
[6] Sum elements of frame
[7] Sum elements of EE
[8] Mass of accessories
[9] Create output table and check if vehicle surpasses 3.5t passenger car limit
[10] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
import numpy as np
import pandas as pd
# endregion


def calc_vehicle_total_weight(vehicle, parameters):
    # region [1] Initialize necessary variables
    weight_passenger = parameters.masses.payload.weight_passenger   # Mass of one passenger in kg according to 2007/46/EC
    weight_suitcase = parameters.masses.payload.weight_luggage      # Mass of his suitcase in kg according to 2007/46/EC
    payload = vehicle.masses.payload                                # Payload of the vehicle (i.e. passenger weight + maximum luggage load)
    weight_extra_equipment = vehicle.masses.extra_equipment         # If there are extra equipment in the vehicle they can be assigned here
    # endregion

    # region [2] Sum elements of chassis
    chassis = vehicle.masses.chassis
    dict_chassis = vars(chassis)
    keys_chassis = [all_keys_chassis for all_keys_chassis in dict_chassis if not all_keys_chassis.startswith('__')]

    # Derive the total chassis mass
    mass_chassis = 0
    for key_chassis in keys_chassis:
        mass_component_chassis = dict_chassis[key_chassis]
        mass_chassis = mass_chassis + mass_component_chassis
    # endregion

    # region [3] Sum elements of powertrain
    powertrain = vehicle.masses.powertrain
    dict_powertrain = vars(powertrain)
    keys_powertrain = [all_keys_powertrain for all_keys_powertrain in dict_powertrain if not all_keys_powertrain.startswith('__')]

    # Derive the total powertrain mass
    mass_powertrain = 0
    for key_powertrain in keys_powertrain:
        mass_component_powertrain = dict_powertrain[key_powertrain]
        mass_powertrain = mass_powertrain + mass_component_powertrain

    # Calculate masses of powertrain
    battery_mass = powertrain.battery_structural_components + powertrain.battery_cells + powertrain.battery_electrical
    GM_mass = mass_powertrain - battery_mass - powertrain.cooling_weight
    cooling_mass = powertrain.cooling_weight
    # endregion

    # region [4] Sum elements of interior
    interior = vehicle.masses.interior
    dict_interior = vars(interior)
    keys_interior = [all_keys_interior for all_keys_interior in dict_interior if not all_keys_interior.startswith('__')]

    # Derive the total interior mass
    mass_interior = 0
    for key_interior in keys_interior:
        mass_component_interior = dict_interior[key_interior]
        mass_interior = mass_interior + mass_component_interior
    # endregion

    # region [5] Sum elements of exterior
    exterior = vehicle.masses.exterior
    dict_exterior = vars(exterior)
    keys_exterior = [all_keys_exterior for all_keys_exterior in dict_exterior if not all_keys_exterior.startswith('__')]

    # Derive the total exterior mass
    mass_exterior = 0
    for key_exterior in keys_exterior:
        mass_component_exterior = dict_exterior[key_exterior]
        mass_exterior = mass_exterior + mass_component_exterior
    # endregion

    # region [6] Sum elements of frame
    frame = vehicle.masses.frame
    dict_frame = vars(frame)
    keys_frame = [all_keys_frame for all_keys_frame in dict_frame if not all_keys_frame.startswith('__')]

    # Derive the total frame mass
    mass_frame = 0
    for key_frame in keys_frame:
        mass_component_frame = dict_frame[key_frame]
        mass_frame = mass_frame + mass_component_frame
    # endregion

    # region [7] Sum elements of EE
    EE = vehicle.masses.EE
    dict_EE = vars(EE)
    keys_EE = [all_keys_EE for all_keys_EE in dict_EE if not all_keys_EE.startswith('__')]

    # Derive the total EE mass
    mass_EE = 0
    for key_EE in keys_EE:
        mass_component_EE = dict_EE[key_EE]
        mass_EE = mass_EE + mass_component_EE
    # endregion

    # region [8] Mass of accessories
    mass_accessories = vehicle.masses.accessories
    # endregion

    # region [9] Create output table and check if vehicle surpasses 3.5t passenger car limit

    # Store the masses of the several components into a Dataframe
    columns = ['mass_chassis', 'mass_powertrain', 'mass_interior', 'mass_exterior', 'mass_frame', 'mass_EE', 'mass_accessories']
    vehicle_masses_list = np.array([[mass_chassis, mass_powertrain, mass_interior, mass_exterior, mass_frame, mass_EE, mass_accessories]])
    simulated_vehicle_masses = pd.DataFrame(vehicle_masses_list, columns=columns)

    # Calculate empty weight EU (with driver) and the max weight in kg
    vehicle_empty_weight_sim = mass_chassis + mass_powertrain + mass_interior + mass_exterior + \
                               mass_frame + mass_EE + mass_accessories + weight_extra_equipment
    vehicle_empty_weight_EU_sim = vehicle_empty_weight_sim + weight_passenger + weight_suitcase
    vehicle_max_weight_sim = vehicle_empty_weight_EU_sim + payload

    # Check that the given mass does not surpass the 3.5t limit for passenger cars
    if vehicle_max_weight_sim > 3500:
        # If the vehicle reaches the maximum weight for licensing, the weight has to
        # be reduced. This is achieved by reducing payload and extra equipment weight.
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The actual vehicle weights above 3500 kg, extra equipment and payload will be reduced'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)

        # Weight to reduce in kg
        to_reduce = vehicle_max_weight_sim - 3500

        # Reduce extra equipment weight:
        weight_extra_equipment_new = max(0, weight_extra_equipment - to_reduce)
        to_reduce = to_reduce - (weight_extra_equipment - weight_extra_equipment_new)

        # Reassign new extra equipment weight
        setattr(vehicle.masses, 'extra_equipment', weight_extra_equipment_new)

        # If it is not sufficient, reduce the payload
        if to_reduce > 0:

            payload_new = max(0, payload - to_reduce)
            to_reduce = to_reduce - (payload - payload_new)

            # Reassign new payload
            payload = payload_new
            setattr(vehicle.masses, 'payload', payload_new)

            # if it is not sufficient, this vehicle cannot be licenced with the actual weight:
            if to_reduce > 0:
                raise Exception('The actual vehicle weights above 3500 kg and is therefore not suitable for licencing as a passenger car')

        # Recalculate maximum weight
        vehicle_max_weight_sim = vehicle_empty_weight_EU_sim + payload + weight_extra_equipment_new
    # endregion

    # region [10] Assign Outputs
    setattr(vehicle.masses, 'vehicle_empty_weight_sim', vehicle_empty_weight_sim)
    setattr(vehicle.masses, 'vehicle_empty_weight_EU_sim', vehicle_empty_weight_EU_sim)

    # Add payload = gross weight - curb weight EU. It includes passengers (driver already in curb weight EU) and cargo
    setattr(vehicle.masses, 'vehicle_max_weight_sim', vehicle_max_weight_sim)
    setattr(vehicle.masses, 'simulated_vehicle_masses', simulated_vehicle_masses)
    # endregion

    return vehicle, parameters
