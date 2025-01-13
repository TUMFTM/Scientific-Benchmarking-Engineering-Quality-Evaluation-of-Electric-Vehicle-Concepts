"""
Description: This function has the task to create an empty class for the Benchmarking Values
             All desired attributes will be filled in by the function read_real_vehicle from the Excel sheet
------------
Sources: None
------------
Input: None
------------
Output: Class element for the Benchmarking values
------------

Implementation
[0] Import all necessary Classes from the subfolder Parameter_single_class
[1] Initialize the Class and define the Object-functions
"""

# region [0] Import all necessary Classes and functions from the sub folders
# Import the classes
from . Benchmarking_single_class.Benchmarking_performace_class import Performance   # Create performance class
from . Benchmarking_single_class.Benchmarking_comfort_class import Comfort          # Create comfort class
# Import functions
# endregion


# region [1] Initialize the vehicle class and define the Object-functions
class Benchmarking:
    # [1.1] Initialize the class
    def __init__(self):
        self.performance = Performance()
        self.comfort = Comfort()

    # [1.2] Define the initialize function to set the attributes dynamically
# endregion
