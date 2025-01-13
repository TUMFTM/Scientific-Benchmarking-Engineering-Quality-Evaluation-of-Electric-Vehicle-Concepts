"""
Description: Initialize the weight options of the vehicle
------------
Sources:  (1) Felgenhauer, Matthias; Nicoletti, Lorenzo, "Empiric Weight Model for the Early Phase of Vehicle Architecture Design", DOI: 10.1109/EVER.2019.8813530, 2019
------------
Input: vehicle: Stores the calculated component volumes and masses
       parameters: Stores the constant values and regressions for volume and mass models
------------
Output: Updated vehicle class with the initialized weight options
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Assign Inputs
[2] Calculate vehicle reduced vehicle mass
[3] Check values and assign outputs
[4] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import numpy as np
import math
# endregion


def initialize_weight_options(vehicle, parameters):
    # region [1] Assign Inputs:
    # Local Inputs for the mass estimation
    weight_passenger = parameters.masses.payload.weight_passenger   # in kg
    weight_suitcase = parameters.masses.payload.weight_luggage      # in kg
    payload = vehicle.Input.vehicle_payload                         # in kg
    extra_equipment = vehicle.Input.extra_equipment                 # in kg

    # Repartition of the vehicle
    front_repartition = vehicle.masses.optional_extras.front_repartition  # Repartition in % on the front axle
    # endregion

    # If the user gives an input, this will be used for the weight calculation (This should always be the case)
    if not np.isnan(vehicle.Input.vehicle_empty_weight):

        reduced_weight = vehicle.Input.vehicle_empty_weight        # in kg
    else:

        # Variables for the volume estimation
        overhang_f = vehicle.dimensions.GX.vehicle_overhang_f   # in mm
        wheelbase = vehicle.dimensions.GX.wheelbase             # in mm
        width = vehicle.dimensions.GY.vehicle_width             # in mm
        height = vehicle.dimensions.GZ.vehicle_height           # in mm
        length = vehicle.dimensions.GX.vehicle_length           # in mm
        overhang_r = length - wheelbase - overhang_f            # in mm
        frameform = vehicle.topology.frameform                  # vehicle frameform -> SUV/Sedan/Hatchback

        # region [2] Calculate vehicle reduced vehicle mass:
        # Calculate the vehicle volume in m^3. Distinguish between Sedan and Hatchback and SUV see (1)
        # Formulas taken from (1)
        if frameform.lower() == 'sedan':
            volume = (1/2 * overhang_f + wheelbase + 2/3 * overhang_r) * width * height/math.pow(10, 9)
        else:  # Volume for SUV and Hatchback
            volume = (1/2 * overhang_f + wheelbase + 3/4 * overhang_r) * width * height/math.pow(10, 9)

        # Calculate empirical reduced mass (no battery included) in kg see (1)
        reduced_weight = -169.497 + 139.463 * volume
        # endregion

    # region [3] Check values and assign outputs
    # Calculate empty weight EU (with driver) and the max weight (all in kg)
    vehicle_empty_weight = reduced_weight + extra_equipment
    vehicle_empty_weight_EU = vehicle_empty_weight + weight_passenger + weight_suitcase
    vehicle_max_weight = vehicle_empty_weight_EU + payload

    # Check if the given weight does not exceed the 3.5t limit for passenger cars
    if vehicle_max_weight > 3500:
        raise Exception('The actual vehicle weights above 3500 kg and is therefore not suitable for licencing as a passenger car')
    # endregion

    # region [4] Calculate the axle loads
    rear_repartition = 100 - front_repartition  # Repartition in % on the rear axle
    axle_load_r_max = rear_repartition * 0.01 * vehicle_max_weight          # in kg
    axle_load_f_max = front_repartition * 0.01 * vehicle_max_weight         # in kg
    axle_load_r_empty = rear_repartition * 0.01 * vehicle_empty_weight      # in kg
    axle_load_f_empty = front_repartition * 0.01 * vehicle_empty_weight     # in kg
    # endregion

    # region [4] Assign Outputs
    # If the vehicle has extra optionals, their mass is described by this variable
    setattr(vehicle.masses, 'extra_equipment', extra_equipment)
    # Corresponds to the maximum payload of the vehicle (including the passengers)
    setattr(vehicle.masses, 'payload', payload)
    setattr(vehicle.masses, 'vehicle_empty_weight', vehicle_empty_weight)
    setattr(vehicle.masses, 'vehicle_empty_weight_EU', vehicle_empty_weight_EU)
    setattr(vehicle.masses, 'vehicle_max_weight', vehicle_max_weight)

    # Axle loads
    setattr(vehicle.masses, 'axle_load_r_max', axle_load_r_max)         # in kg
    setattr(vehicle.masses, 'axle_load_f_max', axle_load_f_max)         # in kg
    setattr(vehicle.masses, 'axle_load_r_empty', axle_load_r_empty)     # in kg
    setattr(vehicle.masses, 'axle_load_f_empty', axle_load_f_empty)     # in kg
    # endregion

    return vehicle, parameters
