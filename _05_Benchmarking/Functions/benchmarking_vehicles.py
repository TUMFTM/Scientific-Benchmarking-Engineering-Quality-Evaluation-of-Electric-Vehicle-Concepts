"""
Description: This function has to task:
                1.) Create the spiderplots to visualize the difference between real vehicle and simulated digital
                    reference model. This is done for each vehicle individually
                2.) Compute the engineering score for each vehicle. This is done in relation to the simulated digital
                    reference models of other vehicles

                In the entire script the order of the benchmarking criteria is important in all arrays regarding
                the analysis. E.g. in all arrays the first element refers to the consumption, the second to the range,
                the third to the dimensional chain in Z-direction and so on (Check line 66)
------------
Sources:  (1) Rosenberger et al., "Scientific benchmarking: Engineering quality evaluation of electric vehicle concepts", e-Prime - Advances in Electrical Engineering, Electronics and Energy 9, 2024
          (2) Koening, "Bewertung von elektrischen Fahrzeugkonzepten anhand eines weiterentwickelten Simulationsmodells", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
          (3) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
------------
Input: vehicle_names: list of all vehicles that can be evaluated
       save_plot: String to define the fileformat the spiderplot should be stored. Options are "svg | pgf | None "
       bool_spiderplot: Boolean to activate/deacitvate the creation of the spiderplots
------------
Output: Benchmark Analysis of all the vehicles
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Preliminaries
[2] Collect vehicle data
[3] Calculate the boundaries for the absolute spider plots
[4] Create absolute Spiderplots
[5] Calculate assessment coefficients
[6] Calculate final scores for all vehicle
[6.1] Calculate raw points based on deviations
[6.2] Calculate final points based on raw points
[6.3] Plot spider plot with the relative points
[6.4] Calculate final score
[7] Create Score dataframe
[8] Create multiplot spiderplot
endregion
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import os
import pickle
import pandas as pd
import numpy as np
# Import classes
# Import methods
from .create_spider_plot import create_spiderplot
# endregion


def benchmarking_vehicles(vehicles_names, settings_plot):
    # region [1] Preliminaries
    # define path
    path_main = os.getcwd()
    path_benchmarking = os.path.join(path_main, "_05_Benchmarking")
    path_results = os.path.join(path_main, "_05_Benchmarking", "Results")

    # Load already calculated assessment coefficients (set to True when already computed assessment coefficients shall be used)
    load_assess_coeff = False

    # Names of the columns in the score evaluation
    columns_score = ['Performance_Score', 'Comfort_Score', 'Engineering_Score']

    # Names of the spiderplot categories --> Are also used in the computation of the engineering score
    list_dict_points = ['Consumption', 'Range', 'Z', 'Trunk_volume', 'X', 'Charging_time', 't0_100', 'slalom']

    # If one of the spiderplot categories has a negative scale (smallest values on the outer ring, highest values on the
    # inner ring), this values has to be negated. The first element of this array refers to the first element of the
    # list_dict_points array defined before
    invert = np.array([-1, 1, 1, 1, 1, -1, -1, 1])

    # Names of the axes in the spiderplots (need to be in the same order as the variable list_dict_points)
    columns_plots_abs = ['Energy consumption in kWh/100km', 'Electric range in km', 'Z-measure in mm',
                         'Trunk volume in L', 'X-measure in mm', 'Charging time in min',
                         'Acceleration time in s', 'Slalom velocity in km/h']

    columns_plots_rel = ['Energy consumption in -', 'Electric range in -', 'Z-measure in -',
                         'Trunk volume in -', 'X-measure in -', 'Charging time in -',
                         'Acceleration time in -', 'Slalom velocity in -']

    # Initialize plot settings
    do_plots = settings_plot['do_spiderplot']
    save_plot = settings_plot['save_plots']
    multiplot_list = settings_plot['multiplot_vehicles']
    multiplot_results = np.zeros((len(multiplot_list), len(list_dict_points)))
    custom_colors = settings_plot['plot_colors']
    num_rings = 5            # Stores the number of rings inside the spiderplots

    # Initialize lists and arrays
    result_total = np.empty((0, len(list_dict_points)))     # Array which stores all the absolute results for the real and the simulated vehicles
    score_results = []          # Stores the computed store for each vehicle as new list inside this variable
    vehicle_list = []           # All vehicle names will be stored inside this list
    deviations = dict()         # For each vehicle the deviations are stored inside this dictionary (key is the vehicle name)

    # Set up the deviation vectors (The deviation of each vehicle will be stored in the corresponding array)
    t0_100 = np.array([])           # in %: Deviation between simulated and real acceleration time
    Range = np.array([])            # in %: Deviation between the simulated and the real Ecotest range
    Consumption = np.array([])      # in %: Deviation between the simulated and the real WLTP consumption
    H61_1 = np.array([])            # in %: Deviation between the simulated and real H61-1 measure
    H61_2 = np.array([])            # in %: Deviation between the simulated (based on the 95%-manikin) and the real H61-2 measure
    L50_2 = np.array([])            # in %: Deviation between the simulated and the real L50-2 measure
    H5_2 = np.array([])             # in %: Deviation between the simulated and the real H5-2 measure
    Trunk_volume = np.array([])     # in %: Deviation between the simulated and the real trunk volume
    Charging_time = np.array([])    # in %: Deviation between the simulated and the real charging time
    Slalom = np.array([])           # in %: Deviation between the simulated and the real slalom velocity

    # Define the weights for the Z dimensions weights
    z_weights = np.array([1, 1])  # Weight factors for the head clearance of the front and rear seat, weighted equally (1)
    # endregion

    # region [2] Collect vehicle data
    # Load all vehicle deviations
    for vehicle_file in vehicles_names:

        # Extract the vehicle name from the list (remove the .pkl suffix)
        vehicle_name = vehicle_file[0:-4]

        # Initialize both dictionaries
        sim_data = dict()           # Stores the simulated values from the vehicle
        real_data = dict()          # Stores the real values from the vehicle

        # Concatenate the full file for each vehicle
        path_vehicle = os.path.join(path_results, vehicle_file)
        with open(path_vehicle, 'rb') as input_vehicle:
            #  Load data from file
            vehicle_loaded = pickle.load(input_vehicle)

        # Assign vehicle specific dictionaries
        deviations[vehicle_name] = vehicle_loaded['deviation']  # Fill the deviations dictionary for each vehicle (key = vehicle_name)
        all_sim_data = vehicle_loaded['sim']                    # Extract the simulated vehicle values
        all_real_data = vehicle_loaded['real']                  # Extract the real vehicle values

        # Fill each deviations array with the values from the specific vehicle
        # -----------------Comment: Some values are inverted here, because bigger values-----------------
        # -----------------of the real vehicle mean a better score. Thus the deviation-----------------
        # -----------------between real and simulated must be inverted-----------------
        # Performance values
        t0_100 = np.append(t0_100, deviations[vehicle_name]['t0_100'])                          # Acceleration deviation
        Range = np.append(Range, -deviations[vehicle_name]['Range'])                            # Range deviation
        Consumption = np.append(Consumption, deviations[vehicle_name]['Consumption'])           # Consumption deviation
        Charging_time = np.append(Charging_time, deviations[vehicle_name]['charging_time'])     # Charging time dev.
        Slalom = np.append(Slalom, -deviations[vehicle_name]['slalom'])

        # Comfort values
        H61_1 = np.append(H61_1, -deviations[vehicle_name]['H61_1'])                            # H61-1 deviation
        H61_2 = np.append(H61_2, -deviations[vehicle_name]['H61_2'])                            # H61-2 deviation
        L50_2 = np.append(L50_2, -deviations[vehicle_name]['L50_2'])                            # L50-2 deviation
        H5_2 = np.append(H5_2, -deviations[vehicle_name]['H5_2'])                               # H5-2 deviation
        Trunk_volume = np.append(Trunk_volume, -deviations[vehicle_name]['Trunk_volume'])       # Trunk volume deviation

        # Collect spider data (used to plot the absolute values for each vehicle)
        # Collect simulated and real consumption times
        sim_data['Consumption'] = all_sim_data['Consumption']
        real_data['Consumption'] = all_real_data['Consumption']

        # Collect simulated and real acceleration time
        sim_data['Range'] = all_sim_data['Range']
        real_data['Range'] = all_real_data['Range']

        # Compute the simulated and real values for the Z-measure
        sim_data['Z'] = (z_weights[0] * all_sim_data['H61_1'] + z_weights[1] * all_sim_data['H5_2'])/np.sum(z_weights)
        real_data['Z'] = (z_weights[0] * all_real_data['H61_1'] + z_weights[1] * all_real_data['H5_2'])/np.sum(z_weights)

        # Collect the simulated and real trunk volume
        sim_data['Trunk_volume'] = all_sim_data['Trunk_volume']
        real_data['Trunk_volume'] = all_real_data['Trunk_volume']

        # Compute the simulated and real values for the X-measure (is right now only the L50-2 measure)
        sim_data['X'] = all_sim_data['L50_2']
        real_data['X'] = all_real_data['L50_2']

        # Collect simulated and real acceleration time
        sim_data['t0_100'] = all_sim_data['t0_100']
        real_data['t0_100'] = all_real_data['t0_100']

        # Collect the simulated and real charging time
        sim_data['Charging_time'] = all_sim_data['charging_time']
        real_data['Charging_time'] = all_real_data['charging_time']

        # Collect the simulated and real slalom velocity
        sim_data['slalom'] = all_sim_data['slalom']
        real_data['slalom'] = all_real_data['slalom']

        # Create a array where all the real and simulated values are stored
        results_abs_arr = np.zeros((2, len(list_dict_points)))
        for i, key in enumerate(list_dict_points):
            results_abs_arr[0, i] = real_data[key]  # Assign the real values to the first row (order based on the list_dict_points)
            results_abs_arr[1, i] = sim_data[key]   # Assign the simulated values to the second row (same order)

        # Store all so far calculated values inside one single array (used to computed the boundaries of the spiderplot)
        result_total = np.row_stack((result_total, results_abs_arr))
    # endregion

    # region [3] Calculate the boundaries for the absolute spider plots
    # Calculate the minimum and maximum value for each spiderplot category
    min_total_results = np.floor(np.min(result_total, axis=0) * 0.9)        # Buffer of 10 percent
    max_total_results = np.ceil(np.max(result_total, axis=0) * 1.1)         # Buffer of 10 percent

    # Calculate the step size between the max and the
    step_size = np.ceil((max_total_results - min_total_results)/(num_rings - 1))

    # Recalculate the maximum values (necessary because of rounding errors)
    max_total_results = min_total_results + step_size * (num_rings - 1)

    # Create a matrix which combines min and max values (Here is the invert array integrated to ensure negative notated axis)
    min_max_matrix_abs = np.row_stack((min_total_results * invert, max_total_results * invert))

    # Calculate the minimum and maximum value for the axis scale for each spiderplot category
    min_per_variable_abs = np.abs(np.min(min_max_matrix_abs, axis=0))
    max_per_variable_abs = np.abs(np.max(min_max_matrix_abs, axis=0))
    min_max_per_variable_abs = zip(min_per_variable_abs, max_per_variable_abs)

    # Create dataframe from the minimum and maximum values
    columns_min_max = ['min', 'max']
    min_max_per_variable_abs = pd.DataFrame(min_max_per_variable_abs, columns=columns_min_max, index=columns_plots_abs)
    # endregion

    # region [4] Create absolute Spiderplots
    for i, vehicle_file in enumerate(vehicles_names):
        # Extract the vehicle name (remove .pkl suffix)
        vehicle_name = vehicle_file[0:-4]

        # Extract the specific vehicle results from all results (always two rows of the result_total matrix)
        results_vehicle = result_total[2*i:2*i+2, :]

        # Create dataframe from vehicle results
        result = pd.DataFrame(results_vehicle, columns=columns_plots_abs)

        # Define the legend and the title based on the vehicle name and the method
        legend = [vehicle_name + '- Real', vehicle_name + '- Simulation']
        title = vehicle_name + '- absolut values'
        method = '_abs'

        # Define plotting colors
        color_index = len(results_vehicle)

        # Define axis labels
        variables = list(result.columns)

        # Define range (min and max value) for each axis
        ranges = list(min_max_per_variable_abs.itertuples(index=False, name=None))

        # Create spiderplot
        if do_plots:
            create_spiderplot(vehicle_name, result, variables, ranges, num_rings, custom_colors[0:color_index],
                          legend, title, save_plot, method)
    # endregion

    # region [5] Calculate assessment coefficients
    path_assessment_coeff = os.path.join(path_benchmarking, 'rating_coeff.pkl')
    if load_assess_coeff and os.path.exists(path_assessment_coeff):
        # Import assessment coefficient if desired
        with open(path_assessment_coeff, 'rb') as input_vehicle:
            rating_coeff = pickle.load(input_vehicle)

    else:
        # Calculate assessment coefficients
        min_max_values = np.array([0, 100])             # Values are between 0 and 100
        rating_coeff = dict()                           # Initialize rating_coeff dictionary

        # Calculate a straight line through the minimum and maximum point of acceleration deviations
        rating_coeff['t0_100'] = np.polyfit(np.array([np.min(t0_100), np.max(t0_100)]), min_max_values, 1)
        # Calculate a straight line through the minimum and maximum point of range deviations
        rating_coeff['Range'] = np.polyfit(np.array([np.min(Range), np.max(Range)]), min_max_values, 1)
        # Calculate a straight line through the minimum and maximum point of consumption deviations
        rating_coeff['Consumption'] = np.polyfit(np.array([np.min(Consumption), np.max(Consumption)]), min_max_values, 1)
        # Calculate a straight line through the minimum and maximum point of charging time deviations
        rating_coeff['Charging_time'] = np.polyfit(np.array([np.min(Charging_time), np.max(Charging_time)]), min_max_values, 1)
        # Calculate a straight line through the minimum and maximum point of slalom velocity deviations
        rating_coeff['Slalom'] = np.polyfit(np.array([np.min(Slalom), np.max(Slalom)]), min_max_values, 1)

        # Calculate a straight line through the minimum and maximum point of H61-1 deviations
        rating_coeff['H61_1'] = np.polyfit(np.array([np.min(H61_1), np.max(H61_1)]), min_max_values, 1)
        # Calculate a straight line through the minimum and maximum point of H61-2 deviations
        rating_coeff['H61_2'] = np.polyfit(np.array([np.min(H61_2), np.max(H61_2)]), min_max_values, 1)
        # Calculate a straight line through the minimum and maximum point of L50-2 deviations
        rating_coeff['L50_2'] = np.polyfit(np.array([np.min(L50_2), np.max(L50_2)]), min_max_values, 1)
        # Calculate a straight line through the minimum and maximum point of H5-2 deviations
        rating_coeff['H5_2'] = np.polyfit(np.array([np.min(H5_2), np.max(H5_2)]), min_max_values, 1)
        # Calculate a straight line through the minimum and maximum point of trunk volume deviations
        rating_coeff['Trunk_volume'] = np.polyfit(np.array([np.min(Trunk_volume), np.max(Trunk_volume)]), min_max_values, 1)

        # Save those rating coefficients
        with open(path_assessment_coeff, 'wb') as output:
            pickle.dump(rating_coeff, output, pickle.HIGHEST_PROTOCOL)

        # Print point <-> deviation relationship
        one_point_deviation = round(abs((1 - rating_coeff['t0_100'][1]) / rating_coeff['t0_100'][0] - (2 - rating_coeff['t0_100'][1])/rating_coeff['t0_100'][0]), 2)
        print("One point in acceleration means a deviation of " + str(one_point_deviation) + " %.")
        one_point_deviation = round(abs((1 - rating_coeff['Range'][1]) / rating_coeff['Range'][0] - (2 - rating_coeff['Range'][1]) / rating_coeff['Range'][0]), 2)
        print("One point in range means a deviation of " + str(one_point_deviation) + " %.")
        one_point_deviation = round(abs((1 - rating_coeff['Charging_time'][1]) / rating_coeff['Charging_time'][0] - (2 - rating_coeff['Charging_time'][1]) / rating_coeff['Charging_time'][0]), 2)
        print("One point in charging time means a deviation of " + str(one_point_deviation) + " %.")
        one_point_deviation = round(abs((1 - rating_coeff['Consumption'][1]) / rating_coeff['Consumption'][0] - (2 - rating_coeff['Consumption'][1]) / rating_coeff['Consumption'][0]), 2)
        print("One point in consumption means a deviation of " + str(one_point_deviation) + " %.")
        one_point_deviation = round(abs((1 - rating_coeff['Slalom'][1]) / rating_coeff['Slalom'][0] - (2 - rating_coeff['Slalom'][1]) / rating_coeff['Slalom'][0]), 2)
        print("One point in slalom velocity a deviation of " + str(one_point_deviation) + " %.")

        one_point_deviation = round(abs((1 - rating_coeff['H61_1'][1]) / rating_coeff['H61_1'][0] - (2 - rating_coeff['H61_1'][1]) / rating_coeff['H61_1'][0]), 2)
        print("One point in H61_1 means a deviation of " + str(one_point_deviation) + " %.")
        one_point_deviation = round(abs((1 - rating_coeff['H61_2'][1]) / rating_coeff['H61_2'][0] - (2 - rating_coeff['H61_2'][1]) / rating_coeff['H61_2'][0]), 2)
        print("One point in H61_2 means a deviation of " + str(one_point_deviation) + " %.")
        one_point_deviation = round(abs((1 - rating_coeff['L50_2'][1]) / rating_coeff['L50_2'][0] - (2 - rating_coeff['L50_2'][1]) / rating_coeff['L50_2'][0]), 2)
        print("One point in L50_2 means a deviation of " + str(one_point_deviation) + " %.")
        one_point_deviation = round(abs((1 - rating_coeff['H5_2'][1]) / rating_coeff['H5_2'][0] - (2 - rating_coeff['H5_2'][1])/rating_coeff['H5_2'][0]), 2)
        print("One point in H5_2 means a deviation of " + str(one_point_deviation) + " %.")
        one_point_deviation = round(abs((1 - rating_coeff['Trunk_volume'][1]) / rating_coeff['Trunk_volume'][0] - (2 - rating_coeff['Trunk_volume'][1])/rating_coeff['Trunk_volume'][0]), 2)
        print("One point in trunk volume means a deviation of " + str(one_point_deviation) + " %.")
    # endregion

    # region [6] Calculate final scores for all vehicle
    for vehicle_file in vehicles_names:
        # Extract the vehicle names from the list (remove .pkl file)
        vehicle_name = vehicle_file[0:-4]

        # region [6.1] Calculate raw points based on deviations
        Raw_Points = dict()

        # Acceleration
        factor_acc = 1             # Lower acceleration is better --> factor = positive
        Raw_Points['t0_100'] = round(rating_coeff['t0_100'][0] * factor_acc * deviations[vehicle_name]['t0_100'] + rating_coeff['t0_100'][1], 1)

        # Range
        factor_range = -1  # Higher range is better --> factor = negative
        Raw_Points['Range'] = round(rating_coeff['Range'][0] * factor_range * deviations[vehicle_name]['Range'] + rating_coeff['Range'][1], 1)

        # Consumption
        factor_cons = 1  # Lower consumption is better --> factor = positive
        Raw_Points['Consumption'] = round(rating_coeff['Consumption'][0] * factor_cons * deviations[vehicle_name]['Consumption'] + rating_coeff['Consumption'][1], 1)

        # Charging time
        factor_charg = 1  # Lower charging time is better --> factor = positive
        Raw_Points['Charging_time'] = round(rating_coeff['Charging_time'][0] * factor_charg * deviations[vehicle_name]['charging_time'] + rating_coeff['Charging_time'][1], 1)

        # Slalom
        factor_slalom = -1  # Higher slalom velocity  is better --> factor = negative
        Raw_Points['Slalom'] = round(rating_coeff['Slalom'][0] * factor_slalom * deviations[vehicle_name]['slalom'] + rating_coeff['Slalom'][1], 1)

        # H61_1
        factor_H61_1 = -1  # Higher H61-1 measure is better --> factor = negative
        Raw_Points['H61_1'] = round(rating_coeff['H61_1'][0] * factor_H61_1 * deviations[vehicle_name]['H61_1'] + rating_coeff['H61_1'][1], 1)

        # H61_2
        factor_H61_2 = -1  # Higher H61-2 measure is better --> factor = negative
        Raw_Points['H61_2'] = round(rating_coeff['H61_2'][0] * factor_H61_2 * deviations[vehicle_name]['H61_2'] + rating_coeff['H61_2'][1], 1)

        # L50_2
        factor_L50_2 = -1  # Higher L50-2 measure is better --> factor = negative
        Raw_Points['L50_2'] = round(rating_coeff['L50_2'][0] * factor_L50_2 * deviations[vehicle_name]['L50_2'] + rating_coeff['L50_2'][1], 1)

        # Trunk_volume
        factor_trunk = -1  # Higher trunk volume measure is better --> factor = negative
        Raw_Points['Trunk_volume'] = round(rating_coeff['Trunk_volume'][0] * factor_trunk * deviations[vehicle_name]['Trunk_volume'] + rating_coeff['Trunk_volume'][1], 1)
        # endregion

        # region [6.2] Calculate final points based on raw points
        # Initialize the dictionary
        Points = dict()

        # Consumption
        Points['Consumption'] = Raw_Points['Consumption']

        # Acceleration
        Points['t0_100'] = Raw_Points['t0_100']

        # Range
        Points['Range'] = Raw_Points['Range']

        # Comfort-Z
        Points['Z'] = (z_weights[0] * Raw_Points['H61_1'] + z_weights[1] * Raw_Points['H61_2'])/np.sum(z_weights)

        # Trunk volume
        Points['Trunk_volume'] = Raw_Points['Trunk_volume']

        # Comfort-X
        Points['X'] = Raw_Points['L50_2']

        # Charging time
        Points['Charging_time'] = Raw_Points['Charging_time']

        # Slalom velocity
        Points['slalom'] = Raw_Points['Slalom']

        # Bring variables in order such that they can be plotted in spider plot
        results_rel_arr = np.zeros((1, len(list_dict_points)))
        for i, key in enumerate(list_dict_points):
            results_rel_arr[0, i] = Points[key]                  # Store the deviations for each spiderplot category

            if vehicle_name in multiplot_list:
                # Store the multiplot vehicles in a separat matrix
                index_multiplot = multiplot_list.index(vehicle_name)
                multiplot_results[index_multiplot, i] = Points[key]
        # endregion

        # region [6.3] Plot spider plot with the relative points
        # Bounds for spider plot
        min_per_variable_rel = np.zeros((len(list_dict_points), 1)) - 0.01
        max_per_variable_rel = np.ones((len(list_dict_points), 1)) * 100 + 0.01
        min_max_per_variable_rel = np.column_stack((min_per_variable_rel, max_per_variable_rel))
        min_max_per_variable_rel = pd.DataFrame(min_max_per_variable_rel, columns=columns_min_max, index=columns_plots_rel)

        # Create relative results dataframe
        result_rel = pd.DataFrame(results_rel_arr, columns=columns_plots_rel)

        # Extract spiderplots categories and their ranges
        variables = list(result_rel.columns)
        ranges = list(min_max_per_variable_rel.itertuples(index=False, name=None))

        # Set the title, legend and the color of the plot
        legend = [vehicle_name + '']
        title = vehicle_name + '- single score'
        method = '_rel'
        color_index = len(result_rel)
        if do_plots:
            create_spiderplot(vehicle_name, result_rel, variables, ranges, num_rings, custom_colors[0:color_index],
                              legend, title, save_plot, method)
        # endregion

        # region [6.4] Calculate final score
        # Define weights here! (Look (1) on how these weights were determined)
        weights_performance = np.array([269, 442, 560, 504, 276])    # [Acceleration time, Consumption, Range, Charging time, Slalom]
        weights_comfort = np.array([188, 291, 314])      # [X-measure, Z-measure, trunk volume]
        weights_engineering = np.array([2051, 793])    # [performance, comfort]

        # Calculation of factors
        factor_performance = weights_performance/np.sum(weights_performance)
        factor_comfort = weights_comfort/np.sum(weights_comfort)
        factor_engineering = weights_engineering/np.sum(weights_engineering)

        # Calculation of the performance score (Acceleration, Consumption and Charging time)
        Score_performance = factor_performance[0] * Points['t0_100'] + factor_performance[1] * Points['Consumption'] + \
                            factor_performance[2] * Points['Range'] + factor_performance[3] * Points['Charging_time'] + factor_performance[4] * Points['slalom']

        # Calculation of the comfort score (X, Z, and trunk volume)
        Score_comfort = factor_comfort[0] * Points['X'] + factor_comfort[1] * Points['Z'] + factor_comfort[2] * Points['Trunk_volume']

        # Calculation of the engineering score (performance and comfort)
        Score_engineering = factor_engineering[0] * Score_performance + factor_engineering[1] * Score_comfort

        # Concatenate all three score values into on list
        list_score = [Score_performance, Score_comfort, Score_engineering]

        # Update vehicle_list and score_results with the currently calculated scores
        vehicle_list.append(vehicle_name)
        score_results.append(list_score)
        # endregion
    # endregion

    # region [7] Create Score dataframe
    df_benchmarking = pd.DataFrame(score_results, columns=columns_score, index=vehicle_list)
    df_benchmarking.sort_values(by=columns_score[2], ascending=False, inplace=True)
    print(df_benchmarking)
    # endregion

    # region [8] Create multiplot spiderplot
    # Create multiplot dataframe with all the relative results of all vehicles
    result_multiplot = pd.DataFrame(multiplot_results, columns=columns_plots_rel)

    # Define the axis of each spiderplot category and their range
    variables = list(result_multiplot.columns)
    # noinspection PyUnboundLocalVariable
    ranges = list(min_max_per_variable_rel.itertuples(index=False, name=None))

    # Define the legend, title and the color of the spiderplots
    legend = multiplot_list
    title = ''
    color_index = len(result_multiplot)
    method = '_rel'
    if do_plots:
        create_spiderplot('multiplot', result_multiplot, variables, ranges, num_rings, custom_colors[0:color_index],
                          legend, title, save_plot, method)
    # endregion
