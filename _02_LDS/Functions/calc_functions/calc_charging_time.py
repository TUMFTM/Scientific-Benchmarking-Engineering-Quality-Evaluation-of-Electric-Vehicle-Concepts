"""
Description: This function estimates the time of charging of the vehicle based on a standardized
             charging profile (firstly only NCA/NMC cells are considered since other cells are not implemented
             in the analyzed vehicles)
------------
Sources: More information regarding the implementation of the charging profile can be found here:
         (1) P3 Charging Index, "Vergleich der Schnellladefähigkeit verschiedener Elektrofahrzeuge", 2022
         (2) Jossen,  "Moderne Akkumulatoren richtig einsetzen", 2019
         (3) Cao et al., "An optimized EV charging model considering TOU price and SOC curve", IEEE Trans. Smart Grid 3, 2011
         (4) Rosenberger et al., "Scientific benchmarking: Engineering quality evaluation of electric vehicle concepts", e-Prime - Advances in Electrical Engineering, Electronics and Energy 9, 2024
         (5) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The Charging Time from 10% SOC to 80% SOC and the Charging Index
------------

Implementation
[0] Import modules, classes and functions
[1] Assign simulation variables
[2] Load the corresponding charging profile
[3] Compute mean and adjust the charging profile
[4] Calculate estimated charging time
[5] Assign outputs
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
import os
import json
# Import functions
# endregion


def calc_charging_time(vehicle, parameters):
    # region [1] Assign simulation variables
    # 1.1 Assign vehicle information
    battery_energy_net = vehicle.Input.battery_net_energy       # Net capacity of the real vehicle in kWh
    max_charging_power = vehicle.battery.charging.power_EV_database
    mean_charging_power = vehicle.battery.charging.power_mean_ev_database   # Store the mean value of the charging power

    # 1.2 Assign parameter information
    eta_battery = 0.95                              # Efficiency of the battery, (2, page 34)

    # 1.3 Assign the intervall of fast charging
    # --> Strong suggestion is to leave this between 10% and 80% (typical intervall of fast charging (1))
    speed_charg_start = 10                          # Percentual SOC-State at the beginning of the speed charge
    speed_charg_end = 80                            # Percentual SOC-State at the end of the speed charge
    check_charging_profile = 0                      # Necessary to generate a warning if the desired analyzed SOC is not between 10%-80%
    # endregion

    # region [2] Load the corresponding charging profile
    # 2.1 Compute the ratio between the maximum charging_power and the mean charging power
    ratio_power = mean_charging_power/max_charging_power

    # 2.2 Differentiate between the ratio of power (Cell chemistry right now not important)
    given_ratio_power = np.array([0.64, 0.73, 0.79, 0.89])  # Ratio power of provided profiles (4)
    find_nearest_ratio = np.argmin(np.abs(given_ratio_power-ratio_power), axis=0)

    if find_nearest_ratio == 0:
        # Nearest charging ratio is 0.64 and therefore the lowest Charging Profile is selected
        charging_profile_file = "Generic_Charging_Profile_low"
    elif find_nearest_ratio == 1:
        # Nearest charging ratio is 0.73 and therefore the middle Charging Profile is selected
        charging_profile_file = "Generic_Charging_Profile_middle"

        # Necessary because this charging profile is only defined between 7% and 100% SOC
        check_charging_profile = 1
    elif find_nearest_ratio == 2:
        # Nearest charging ratio is 0.79 and therefore the high Charging Profile is selected
        charging_profile_file = "Generic_Charging_Profile_high"

        # Necessary because this charging profile is only defined between 7% and 100% SOC
        check_charging_profile = 1
    elif find_nearest_ratio == 3:
        # Nearest charging ratio is 0.89 and therefore the highest Charging Profile is selected
        charging_profile_file = "Generic_Charging_Profile_highest"

        # Necessary because this charging profile is only defined between 7% and 100% SOC
        check_charging_profile = 1
    else:
        # Wrong input
        setattr(vehicle.battery.charging, 'total_time', np.nan)
        setattr(vehicle.battery.charging, 'power_mean', np.nan)
        raise Exception("CAN\'T SELECT A CHARGING PROFILE: PLEASE CHECK THE CELL TYPE")

    # Get the path of the project
    path_project = os.getcwd()
    path_cycle = os.path.join(path_project, '_02_LDS', 'Charging_Profiles')

    suffix_file = charging_profile_file + '.json'
    file_cycle = os.path.join(path_cycle, suffix_file)   # Loading path

    # Open the json file
    with open(file_cycle, "r") as f:
        drive_cycle = json.load(f)

    Charging_Profil = np.array(drive_cycle[charging_profile_file])
    # endregion

    # 2.3 Check if the SOC was changed
    if speed_charg_start != 10 or speed_charg_end != 80:
        Charging_Profile_SOC_min = np.min(Charging_Profil[:, 0])
        Charging_Profile_SOC_max = np.max(Charging_Profil[:, 0])
        if check_charging_profile == 1 and Charging_Profile_SOC_min < speed_charg_start:
            text_error = 'The charging profile is not defined between 0% and ' + \
                         str(Charging_Profile_SOC_min) + '% SOC. Please change the values in line 52 and 53'
            raise Exception(text_error)

        if check_charging_profile == 1 and Charging_Profile_SOC_max > speed_charg_end:
            text_error = 'The charging profile is not defined between ' + \
                         str(Charging_Profile_SOC_max) + 'and 100% SOC. Please change the values in line 52 and 53'
            raise Exception(text_error)

        print('The selected range of the SOC is not between 10% and 80%. Therefore the Benchmark comparison can''t be absolved appropriate')
        answer = input('Do you want to continue?  (No/Yes)')

        if answer.lower() == 'no':
            print('Execution aborted. Please change the start and endpoint of the SOC in line 52 and 53')
            quit()
    # endregion

    # region [3] Compute mean and adjust the charging profile
    State_of_SOC = Charging_Profil[:, 0]        # x-coordinate of the Charging Profile (State of SOC)
    Charging_Power = Charging_Profil[:, 1]      # y-coordinate of the Charging Profile (Charging Power)

    # Get index of the start and end SOC-state
    try:
        index_start = np.argwhere(State_of_SOC == speed_charg_start)[0, 0]
    except IndexError:
        # If there is no exact match then get the next higher SOC-state
        index_start = np.argwhere(State_of_SOC > speed_charg_start)[0, 0]

    try:
        index_end = np.argwhere(State_of_SOC == speed_charg_end)[0, 0]
    except IndexError:
        # If there is no exact match then get the next higher SOC-state
        index_end = np.argwhere(State_of_SOC > speed_charg_end)[0, 0]

    # Compute the mean of the charging power (3)
    Charging_Power_mean_raw = np.mean(Charging_Power[index_start:index_end + 1])

    # Adapt the maximum power of the charging_profile based on the maximum charging power of the real vehicle
    Charging_Power = Charging_Power * max_charging_power
    Charging_Power_mean = Charging_Power_mean_raw * max_charging_power
    # endregion

    # region [4] Calculate estimated charging time
    # Calculate the start and end capacity of the charging process
    energy_net_start = battery_energy_net * speed_charg_start/100
    energy_net_end = battery_energy_net * speed_charg_end/100

    # Calculate charging time (3 & 4)
    total_time = (energy_net_end - energy_net_start) / (eta_battery * Charging_Power_mean) * 60
    # endregion

    # endregion [5] Assign outputs
    setattr(vehicle.battery.charging, 'total_time', total_time)

    # noinspection PyUnboundLocalVariable
    setattr(vehicle.battery.charging, 'power_mean', Charging_Power_mean)
    setattr(vehicle.battery.charging, 'power_max', max_charging_power)
    # endregion

    return vehicle, parameters
