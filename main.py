"""
Description:  This function is the main function and calls every single functions to compute a benchmark analysis of
              different battery electric vehicles
------------
Sources:    (1) N. Rosenberger et al., "Scientific benchmarking: Engineering quality evaluation of electric vehicle concepts", e-Prime, 2024
            (2) M. Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, TUM, 2024
------------
Input:      None
------------
Output:  Benchmark Analysis of all the vehicles
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Preliminaries
[2] Create empty vehicle and parameters class and assign the parameter class
[3] Assign datas from Excel Sheet
[4] Initialize the vehicle class based on its inputs
[5] Calculate the chassis dimensions of the vehicle
[6] Calculate the dimensional concept
[7] Calculate the powertrain dimensions (e-machine, gearbox and battery)
[8] Calculate the dimension and position of the remaining components
[9] Calculate the trunk volume
[10] Calculate the vehicles weights
[11] Calculate the longitudinal dynamics of the vehicle
[12] Calculate the charging time
[13] Calculate the lateral dynamics simulation
[14] Save the vehicle and parameters struct
[15] Define deviation table
[16] Calculate the deviations for all vehicles
[17] Calculate Benchmarking
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import os
import pickle
import pandas as pd
import warnings
# Import classes
# Import methods
from _00_Preprocessing_Python.load_vehicle import load_vehicle
from _01_Volumetric_Component_Modeling.Chassis.calc_chassis_dimensions import calc_chassis_dimensions
from _01_Volumetric_Component_Modeling.Dimensional_Concept.calc_dimension_trunk import calc_dimension_trunk
from _01_Volumetric_Component_Modeling.calc_powertrain_dimensions import calc_powertrain_dimensions
from _01_Volumetric_Component_Modeling.Dimensional_Concept.calc_dimensional_concept import calc_dimensional_concept
from _01_Volumetric_Component_Modeling.Others.calc_remaining_components import calc_remaining_components
from _03_Gravimetric_Component_Modeling.calc_vehicle_weight import calc_vehicle_weight
from read_real_vehicle_data import read_real_vehicle_data
from _00_Preprocessing_Python.initialize_vehicle import initialize_vehicle
from _02_LDS.calc_longitudinal_simulation import calc_longitudinal_simulation
from _02_LDS.Functions.calc_functions import calc_charging_time
from _05_Benchmarking.Functions import evaluate_vehicle
from _05_Benchmarking.Functions import get_comparison_list
from _05_Benchmarking.Functions import benchmarking_vehicles
from _02_LDS.calc_lateral_simulation import calc_lateral_simulation
# endregion


def main():
    # region [1]: Preliminaries
    warnings.filterwarnings(action='ignore', message='All-NaN slice encountered')

    # Initialize the deviations and vehicle names list
    deviations = []
    vehicle_name = []

    # Initialize the column names for the dataframe (can easily be adapted by adding/removing a column name)
    col_names = ['Max_Power', 't_0_100', 'Consumption', 'Battery_capacity', 'Range',
                 'Mass', 'Trunk_volume', 'Charge_time', 'Charge_power_mean', 'Slalom']

    # Set some attributes for printing the vehicle dataframe
    desired_width = 300
    pd.set_option('display.width', desired_width)
    pd.set_option('display.max_columns', len(col_names))

    # Set the desired indexes for the vehicles from the Excel sheet:
    # (1 equals the first vehicle, 2 the second one and so on, the vehicle name is also possible)
    index_all_vehicles = [1, 2]


    # Define settings for the spiderplots
    settings_plots = dict()
    settings_plots['do_spiderplot'] = True   # (True/False) --> Activate the spiderplots in the evaluation part
    settings_plots['save_plots'] = 'svg'    # (None/svg/pgf) --> Information if the spiderplots shall be saved
    settings_plots['multiplot_vehicles'] = ['Tesla Model 3', 'VW ID.3']     # Define the names of the vehicles as in the Excel-Sheet

    # Set the colors for the spiderplot. The first entry is used for the absolute and relative spiderplots.
    # Additional colors are used in the multiplot
    settings_plots['plot_colors'] = [[0, 101/255, 189/255], [227/255, 114/255, 34/255]] # TUM blue, TUM orange

    if len(settings_plots['multiplot_vehicles']) >= 1 and len(settings_plots['multiplot_vehicles']) != len(settings_plots['plot_colors']):
        raise Exception("Multiplot and colors array do not have the same length. Ensure both arrays have the same lenght")
    # endregion

    for vehicle_index in index_all_vehicles:

        # region [2]: Create empty vehicle and parameters class and assign the parameter class
        vehicle, parameters, benchmarking = load_vehicle()
        # endregion

        list_cycle = ['WLTP', 'ECOTEST']
        vehicle.Input.list_cycle = list_cycle

        # region [3]: Assign datas from Excel Sheet
        vehicle, parameters, benchmarking = read_real_vehicle_data(vehicle, parameters, benchmarking, vehicle_index)
        print(" ")
        print("Vehicle model: ", vehicle.Input.vehicle_name)
        # endregion

        # region [4]: Initialize the vehicle class based on its inputs
        vehicle = initialize_vehicle(vehicle, parameters)
        # endregion

        # region [5]: Calculate the chassis dimensions of the vehicle
        vehicle, parameters = calc_chassis_dimensions(vehicle, parameters)
        # endregion

        # region [6]: Calculate the dimensional concept
        vehicle, parameters = calc_dimensional_concept(vehicle, parameters)
        # endregion

        # region [7]: Calculate the powertrain dimensions (e-machine, gearbox and battery)
        vehicle, parameters = calc_powertrain_dimensions(vehicle, parameters)
        # endregion

        # region [8]: Calculate the dimension and position of the remaining components
        vehicle, parameters = calc_remaining_components(vehicle, parameters)
        # endregion

        # region [9]: Calculate the trunk volume
        vehicle, parameters = calc_dimension_trunk(vehicle, parameters)
        # endregion

        # region [10]: Calculate the vehicles weights
        vehicle, parameters = calc_vehicle_weight(vehicle, parameters)
        # endregion

        # region [11]: Calculate the longitudinal dynamics of the vehicle
        vehicle, parameters = calc_longitudinal_simulation(vehicle, parameters)
        # endregion

        # region [12]: Calculate the charging time
        vehicle, parameters = calc_charging_time(vehicle, parameters)
        # endregion

        # region [13]: Calculate the lateral dynamics simulation
        vehicle = calc_lateral_simulation(vehicle, parameters, benchmarking)

        # region [14]: Save the vehicle and parameters struct
        evaluate_vehicle(vehicle, parameters, benchmarking, save_option=True)
        # endregion

        # region [15]: Define deviation table
        vehicle_name.append(vehicle.Input.vehicle_name)
        deviations.append(get_comparison_list(vehicle, benchmarking))
        df_vehicle = pd.DataFrame(deviations, columns=col_names, index=vehicle_name)
        print(" ")
        print(df_vehicle)
        # endregion

    # region [16]: Calculate the deviations for all vehicles
    # Get a list of all .pkl files in the "Results" folder
    path_main = os.getcwd()
    path_results = os.path.join(path_main, "_05_Benchmarking", "Results")
    all_files = [file for file in os.listdir(path_results) if file.endswith('.pkl')]

    # Set the deviation and vehicle variables as an empty list
    deviations = []
    vehicle_name = []

    # Iterate through all possible .pkl files in the "Results" directory
    for file in all_files:

        # Concatenate the full file for each vehicle
        path_vehicle = os.path.join(path_results, file)
        with open(path_vehicle, 'rb') as input_vehicle:
            vehicle_loaded = pickle.load(input_vehicle)

        # Add corresponding vehicle name to the column
        vehicle_name.append(vehicle_loaded['vehicle'].Input.vehicle_name)
        deviations.append(get_comparison_list(vehicle_loaded['vehicle'], vehicle_loaded['benchmarking']))

    # Create DataFrame and print it
    df_vehicle = pd.DataFrame(deviations, columns=col_names, index=vehicle_name)
    print(" ")
    print(df_vehicle)
    # endregion

    # region [17]: Calculate Benchmarking
    print(" ")
    benchmarking_vehicles(all_files, settings_plots)
    # endregion


if __name__ == "__main__":
    main()
