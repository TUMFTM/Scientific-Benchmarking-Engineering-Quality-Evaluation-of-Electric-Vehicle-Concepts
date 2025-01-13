"""
Description:  This generates - starting from a given excel tab - the variables needed for benchmarking a real vehicle
------------
Sources:    (1) N. Rosenberger et al., "Scientific benchmarking: Engineering quality evaluation of electric vehicle concepts", e-Prime, 2024
------------
Input:      vehicle: Stores all the information of the computed vehicle
            parameters: Stores the constant values and regressions for volume and mass models
            benchmarking: Stores the benchmarking values of the real vehicle
            vehicle_index: Name of the vehicle or number of the column (Counting begins at 1 for first vehicle)
------------
Output:  Updated vehicle and parameters class with the vehicle specific information
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Load the sheets of the Excel table
[2] Get the vehicle name
[3] Extract vehicle and simulation data for the desired vehicle
[4] Realize inputs for vehicle class
[5] Overwrite Parameter with data from Excel file
[6] Fill the Benchmarking class from the data in the Excel sheet
[7] Adapt vehicle and parameter class with some postprocessing
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
from read_excel import read_excel
import pandas as pd
import os
# Import classes
# Import methods
# endregion


def read_real_vehicle_data(vehicle, parameters, benchmarking, vehicle_index):
    # region [1]: Load the sheets of the Excel table
    folder = os.getcwd()
    file = 'Benchmark_Excel.xlsx'
    path = os.path.join(folder, file)
    vehicle_parameters = pd.read_excel(path, sheet_name=0, header=1)

    # region [2]: Get the vehicle name
    # Check if user input is a name or an index and get vehicle name
    if isinstance(vehicle_index, str):
        vehicle_name = vehicle_index
    else:
        vehicle_name_list = vehicle_parameters.columns
        vehicle_name = vehicle_name_list[int(vehicle_index) + 1]

    # Extract column of desired vehicle
    vehicle_column = 0
    num_vehicles = vehicle_parameters.shape[1]  # Get number of all available vehicles
    for i in range(2, num_vehicles):
        header = vehicle_parameters.columns[i]
        if header == vehicle_name:              # Check if the header of the column equals the vehicle name
            vehicle_column = i
            break

    # Print error if no header match with the vehicle name
    if vehicle_column == 0:
        error_text = "Desired vehicle '" + vehicle_name + "' not found in database!"
        raise Exception(error_text)

    setattr(vehicle.Input, 'vehicle_name', vehicle_parameters.columns[vehicle_column])
    # endregion

    # region [3]: Extract vehicle and simulation data for the desired vehicle
    vehicle_data = vehicle_parameters.iloc[:, [0, vehicle_column]]
    # endregion

    # region [4]: Realize inputs for vehicle class
    vehicle = read_excel(vehicle_data, vehicle, 'vehicle')
    # endregion

    # region [5]: Overwrite Parameter with data from Excel file
    parameters = read_excel(vehicle_data, parameters, 'Parameters')
    # endregion

    # region [6]: Fill the Benchmarking class from the data in the Excel sheet
    benchmarking = read_excel(vehicle_data, benchmarking, 'Benchmarking')

    # Assign the real capacity to the benchmarking class --> used for the computation of the charging time
    setattr(benchmarking.performance, 'battery_net_energy', vehicle.Input.battery_net_energy)

    # Assign the acceleration time to the benchmarking class --> used for calculating the brakes
    setattr(benchmarking.performance, 'acceleration_time', vehicle.Input.acceleration_time)

    # Assign the real torque and power to the benchmarking class --> used for scaling the e-machine
    setattr(benchmarking.performance, 'T_max_Mot_f', vehicle.Input.T_max_Mot_f)
    setattr(benchmarking.performance, 'T_max_Mot_r', vehicle.Input.T_max_Mot_r)
    setattr(benchmarking.performance, 'P_max_Mot_f', vehicle.Input.P_max_Mot_f)
    setattr(benchmarking.performance, 'P_max_Mot_r', vehicle.Input.P_max_Mot_r)

    # Assign the H61-2 measure to the benchmarking class --> used for the calculation of the real SgRP-2
    setattr(benchmarking.comfort, 'H61_2', vehicle.Input.H61_2)
    # endregion

    # region [7]: Adapt vehicle and parameter class with some postprocessing
    # Set cell2pack factors
    if vehicle.Input.cell2pack == 1:
        setattr(parameters.dimensions.EZ.offset_cell2module, 'cylindrical', 0)
        setattr(parameters.dimensions.EZ.offset_cell2module, 'prismatic', 0)
        setattr(parameters.dimensions.EZ.offset_cell2module, 'pouch', 0)

    # Set some not necessary attributes to zero
    setattr(vehicle.masses.optional_extras, 'night_vision', 0)

    # For high torque machines the scaling might not be enough to reach the max cycle speed
    # --> These parameters is multiplied with the necessary rotational speed to ensure that the cycle can be driven
    setattr(parameters.e_machine, 'deviation_rescaling', 0.03)  # Assumption not based on sources
    # endregion

    return vehicle, parameters, benchmarking
