"""
Description: This function extracts real and simulated vehicle data and calculates their deviations.
             If the save option is activated the results will be stored in a pkl file.
             More information of the general approach of the benchmarking analysis can be found in (1, 2 and 3)
------------
Sources:  (1) Rosenberger et al., "Scientific benchmarking: Engineering quality evaluation of electric vehicle concepts", e-Prime - Advances in Electrical Engineering, Electronics and Energy 9, 2024
          (2) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
          (3) Koening, "Bewertung von elektrischen Fahrzeugkonzepten anhand eines weiterentwickelten Simulationsmodells", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
          (4) Kühberger, „Weiterentwicklung eines Simulationsmodells zur Bewertung von Elektrofahrzeugkonzepten im Bereich Package,“ Semesterarbeit, Lehrstuhl für Fahrzeugtechnik, Technische Universität München, 2023
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
       benchmarking: Stores the Benchmarking values of the corresponding vehicle
       save_option: Boolean to store the .pkl file
------------
Output: None
------------

Implementation
[0] Import modules, classes and functions
[1] Initialize dictionaries
[2] Calculate real values of range and consumption
[3] Extract real vehicle values
[4] Extract simulated vehicle values
[5] Calculate deviations
[6] Save pkl file
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
import os
import pickle
import time
import numpy as np
# endregion


def evaluate_vehicle(vehicle, parameters, benchmarking, save_option):
    # region [1] Initialize dictionaries
    real = dict()                   # Stores the parameters of the real vehicle from the benchmarking class
    sim = dict()                    # Stores the parameters of the simulated vehicle from the vehicle class
    deviation = dict()              # Stores the deviations between real values and simulated values
    # endregion

    # region [2] Calculate real values of range and consumption
    # calc for the cars without ADAC ecotest the consumption and capacity with regression
    # calc battery capacity with charging losses (see 1 and 4, p.)
    path_battery_ADAC = benchmarking.performance.battery_net_energy_ADAC
    path_battery_net = benchmarking.performance.battery_net_energy
    if np.isnan(path_battery_ADAC):
        coefficients_batt = parameters.regr.LDS.battery_capacity_charging_loss_ECOTEST.coefficients
        path_battery_ADAC = coefficients_batt[0] + path_battery_net * coefficients_batt[1]

    # calc consumption in ECOTEST of real vehicles
    path_consumption_ADAC = benchmarking.performance.consumption_ECOTEST
    path_consumption_WLTP = benchmarking.performance.consumption_WLTP
    if np.isnan(path_consumption_ADAC):
        coefficients_cons = parameters.regr.LDS.consumption_ECOTEST.coefficients
        path_consumption_ADAC = coefficients_cons[0] + path_consumption_WLTP * coefficients_cons[1]

    # calculate the range of the real vehicle in the ECOTEST
    range_real_vehicle_ECOTEST = path_battery_ADAC / path_consumption_ADAC * 100
    benchmarking.performance.range = range_real_vehicle_ECOTEST
    # endregion

    # region [3] Extract real vehicle values
    # Performance Values
    real['t0_100'] = benchmarking.performance.acceleration_time                 # Real Acceleration time in s
    real['Range'] = range_real_vehicle_ECOTEST                                  # Real Range in km
    real['Consumption'] = path_consumption_WLTP                                 # Real Consumption in kWh/100km
    real['Mass'] = vehicle.masses.vehicle_empty_weight                          # Real Mass in kg
    real['charging_time'] = benchmarking.performance.charging_time.EV_database  # Real Charging time in min
    real['charging_power_max'] = vehicle.battery.charging.power_EV_database     # Real Maximum charging power in kW
    real['charging_power_mean'] = vehicle.battery.charging.power_mean_ev_database   # Real Mean charging power in kW
    real['slalom'] = benchmarking.performance.slalom                                # Real 18m Slalom velocity in km/h

    # Comfort values
    real['W20_1'] = benchmarking.comfort.W20_1                                  # W20-1 measure in mm
    real['W20_2'] = benchmarking.comfort.W20_2                                  # W20-2 measure in mm
    real['H61_1'] = benchmarking.comfort.H61_1                                  # H61-1 measure in mm
    real['H61_2'] = benchmarking.comfort.H61_2                                  # H61-2 measure in mm
    real['L99_1'] = benchmarking.comfort.L99_1                                  # L99-1 measure in mm
    real['L99_2'] = benchmarking.comfort.L99_2                                  # L99-2 measure in mm
    real['L50_2'] = real['L99_2'] - real['L99_1']                               # L50-2 measure in mm
    real['H5_1'] = benchmarking.comfort.H5_1                                    # H5-1 measure in mm
    real['H5_2'] = benchmarking.comfort.H5_2                                    # H5-2 measure in mm
    real['Trunk_volume'] = benchmarking.comfort.trunk_volume_ADAC               # Trunk volume in l
    # endregion

    # region [4] Extract simulated vehicle values
    # performance values
    sim['t0_100'] = vehicle.LDS.sim_acc.acc_time_is                             # Simulated Acceleration time in s
    sim['Range'] = vehicle.LDS.sim_range.range                                   # Simulated Range in km
    sim['Consumption'] = vehicle.LDS.sim_cons.consumption100km                  # Simulated Consumption in kWh/100km
    sim['Mass'] = vehicle.masses.vehicle_empty_weight_sim                       # Simulated Mass in kg
    sim['charging_time'] = vehicle.battery.charging.total_time                  # Simulated Charging time in m
    sim['charging_power_max'] = vehicle.battery.charging.power_max              # Simulated Maximum charging power in kW
    sim['charging_power_mean'] = vehicle.battery.charging.power_mean            # Simulated Mean charging power in kW
    sim['slalom'] = vehicle.Lateral_Dynamics.v_slalom                           # Simulated 18m slalom velocity in km/h

    # comfort values
    sim['W20_1'] = vehicle.manikin.W20_1                                        # Simulated W20-1 measure in mm
    sim['W20_2'] = vehicle.manikin.W20_2                                        # Simulated W20-2 measure in mm
    sim['H61_1'] = vehicle.manikin.H61_1                                        # Simulated H61-1 measure in mm
    sim['H61_2'] = vehicle.manikin.H61_2_95_percentile                          # Simulated H61-2 measure in mm
    sim['L99_1'] = vehicle.manikin.L99_1                                        # Simulated L99-1 measure in mm
    sim['L99_2'] = vehicle.manikin.L99_2                                        # Simulated L99-2 measure in mm
    sim['L50_2'] = vehicle.manikin.L50_2                                        # Simulated L50-2 measure in mm
    sim['H5_1'] = vehicle.manikin.H5_1                                          # Simulated H5-1 measure in mm
    sim['H5_2'] = vehicle.manikin.H5_2                                          # Simulated H5-2 measure in mm
    sim['Trunk_volume'] = vehicle.dimensions.volume_trunk                       # Simulated trunk volume in l
    # endregion

    # region [5] Calculate deviations
    # Performance values
    deviation['t0_100'] = (sim['t0_100'] - real['t0_100'])/real['t0_100'] * 100
    deviation['Range'] = (sim['Range'] - real['Range'])/real['Range'] * 100
    deviation['Consumption'] = (sim['Consumption'] - real['Consumption'])/real['Consumption'] * 100
    deviation['Mass'] = (sim['Mass'] - real['Mass'])/real['Mass'] * 100
    deviation['charging_time'] = (sim['charging_time'] - real['charging_time'])/real['charging_time'] * 100
    deviation['charging_power_max'] = (sim['charging_power_max'] - real['charging_power_max'])/real['charging_power_max'] * 100
    deviation['charging_power_mean'] = (sim['charging_power_mean'] - real['charging_power_mean'])/real['charging_power_mean'] * 100
    deviation['slalom'] = (sim['slalom'] - real['slalom'])/real['slalom'] * 100

    # Comfort values
    deviation['W20_1'] = (sim['W20_1'] - real['W20_1'])/real['W20_1'] * 100
    deviation['W20_2'] = (sim['W20_2'] - real['W20_2'])/real['W20_2'] * 100
    deviation['H61_1'] = (sim['H61_1'] - real['H61_1'])/real['H61_1'] * 100
    deviation['H61_2'] = (sim['H61_2'] - real['H61_2'])/real['H61_2'] * 100
    deviation['L99_1'] = (sim['L99_1'] - real['L99_1'])/real['L99_1'] * 100
    deviation['L99_2'] = (sim['L99_2'] - real['L99_2'])/real['L99_2'] * 100
    deviation['L50_2'] = (sim['L50_2'] - real['L50_2'])/real['L50_2'] * 100
    deviation['H5_1'] = (sim['H5_1'] - real['H5_1'])/real['H5_1'] * 100
    deviation['H5_2'] = (sim['H5_2'] - real['H5_2'])/real['H5_2'] * 100
    deviation['Trunk_volume'] = (sim['Trunk_volume'] - real['Trunk_volume'])/real['Trunk_volume'] * 100
    # endregion

    # region [6] Save pkl file
    if save_option:
        # Create the dictionary to for saving the benchmarking results of the vehicle
        results_benchmarking = dict()
        results_benchmarking['vehicle'] = vehicle
        results_benchmarking['parameters'] = parameters
        results_benchmarking['benchmarking'] = benchmarking
        results_benchmarking['sim'] = sim
        results_benchmarking['real'] = real
        results_benchmarking['deviation'] = deviation

        # Define the name of the stored file (The file name corresponds with the vehicle name)
        vehicle_file_name = vehicle.Input.vehicle_name + ".pkl"

        # Get the path of the main file as origin directory
        path_main = os.getcwd()

        # Select the directory where the saving process takes place
        path_results = os.path.join(path_main, "_05_Benchmarking", "Results")

        # Select the saving path of the benchmarking_results
        path_results_vehicle = os.path.join(path_results, vehicle_file_name)

        # Check if the benchmarking file already exists
        if os.path.exists(path_results_vehicle):
            # If the file exists then backup the old file

            # Get the creation date of the already saved file
            creation_date = time.ctime(os.path.getmtime(path_results_vehicle))
            
            # Create the new suffix for the already saved file
            creation_date_split = str.split(creation_date, ' ')
            creation_time = str.replace(creation_date_split[3], ':', '_')
            if creation_date_split[2] == '':
                creation_date_split[3] = '0' + creation_date_split[3]
                creation_date_split.remove(creation_date_split[2])
            creation_date_suffix = ['', creation_date_split[2], creation_date_split[1], creation_date_split[4], creation_time]

            # Create the new filename for the backup
            vehicle_file_name_new = vehicle.Input.vehicle_name + '_'.join(creation_date_suffix) + '.pkl'

            # Check if the Backup directory exists and if not create it
            path_backups = os.path.join(path_results, "Backups")
            if not os.path.exists(path_backups):
                os.makedirs(path_backups)

            # Move the already stored file into the Backup Folder and rename it
            path_results_new = os.path.join(path_main, "_05_Benchmarking", "Results", "Backups", vehicle_file_name_new)
            os.replace(path_results_vehicle, path_results_new)

        # Save the Benchmarking results as a .pkl file in the Results folder
        with open(path_results_vehicle, 'wb') as output:
            pickle.dump(results_benchmarking, output, pickle.HIGHEST_PROTOCOL)
    # endregion
