"""
Description: This function has the task to load the vehicle and parameter object
------------
Sources: None
------------
Input:    None
------------
Output: Empty class element of the vehicle, benchmarking and the filled Parameters class.
------------

Implementation
[0] Import all necessary Classes from the subfolder Parameter_single_class
[1] Load the parameters' dictionary
[2] Create an empty vehicle Class
[3] Create an empty Benchmarking Class
"""

# region [0] Import all necessary Classes and functions from the sub folders
# Import the class
from .Vehicle_Class import Vehicle
from .Benchmarking_Class import Benchmarking
# Import the modules
import pickle
import os
from pathlib import Path    # necessary to get the file of the parameters class
# endregion


def load_vehicle():
    # region [1] Load the parameters dictionary
    # Get the path of the Parameters.pkl file
    path_complete = os.path.abspath(__file__)
    directory = os.path.dirname(path_complete)
    complete_name = os.path.join(directory, "Parameters" + ".pkl")

    # create a Path object with the path to the file
    check_path = Path(complete_name)

    # Check if the Parameters class file exists
    if check_path.is_file():

        # Parameters class file exists then load it
        with open(complete_name, 'rb') as input_parameters:
            parameters = pickle.load(input_parameters)
    else:
        # Parameters class file does not exist
        raise Exception("Parameters file not found.")
    # endregion

    # region [2] Create an empty vehicle Class
    vehicle = Vehicle()
    # endregion

    # region [3] Create an empty Benchmarking Class
    benchmarking = Benchmarking()
    # endregion

    return vehicle, parameters, benchmarking
