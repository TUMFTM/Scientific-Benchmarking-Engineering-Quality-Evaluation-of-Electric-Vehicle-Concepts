"""
Description: This function has the task to create an empty class for the parameters
             All desired attributes will be assigned dynamically based on the parameters struct of Matlab
------------
Sources: None
------------
Input: None
------------
Output: Class element for all the Parameters
------------

Implementation
[0] Import all necessary Classes from the subfolder Parameter_single_class
[1] Define Parameters class
[2] Define the necessary paths
[3] Load the parameters json file
[4] Loop through the first level of the parameters.json file
[5] Save the Parameters class as .pkl file
"""

# region [0] Import all necessary Classes and functions from the sub folders
# Import the class
from _00_Preprocessing_Python.Parameters_Class import Parameter

# Import the modules
import json
import pickle
import os
# endregion


def converting_json_in_python():
    # region [1] Define the Parameters class
    parameters = Parameter()
    # endregion

    # region [2] Define the necessary paths
    path_script = os.path.abspath(__file__)                         # Path of this script
    split_path_script = os.path.split(path_script)

    # path where the Parameters.pkl file will be stored
    directory_parameters_pkl = os.path.dirname(split_path_script[0])

    # path where the json File is stored
    path_project = os.getcwd()
    for folder in os.listdir(path_project):
        path_parameters_json = os.path.join(path_project, folder, "Parameters.json")
        if os.path.exists(path_parameters_json):
            # If json file exists, then this is the folder of the Parameters json file
            break
    else:
        raise Exception('Parameters file not found. Please enter a json file in the Preprocessing Matlab Folder')
    # endregion

    # region [3] Load the parameters json file
    with open(path_parameters_json, "r") as f:
        parameters_json = json.load(f)
    # endregion

    # region [4] Loop through the first level of the parameters.json file
    # This means that every subclass of the Parameters class is built
    for attr_main_class in parameters_json:

        # Extract all the elements saved in the subclass es
        values_main_class = parameters_json[attr_main_class]

        # Call the initialize_function to set all the desired class attributes for the parameter subclasses
        parameters.initialize_elements(attr_main_class, values_main_class, 'value')
    # endregion

    # region [5] Save the Parameters class as .pkl file
    # Get the complete pathname to save the class
    file_save_parameters = os.path.join(directory_parameters_pkl, "Parameters" + ".pkl")

    # Save as .pkl file
    with open(file_save_parameters, 'wb') as output:
        pickle.dump(parameters, output, pickle.HIGHEST_PROTOCOL)

    return parameters
    # endregion
