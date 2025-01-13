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
[1] Initialize the Class and define the Object-functions
"""

# region [0] Import all necessary Classes and functions from the sub folders
# Import the classes
from .Parameter_single_class.Parameter_battery_class import Parameter_battery                   # Battery parameters
from .Parameter_single_class.Parameter_dimension_class import Parameter_dimensions              # Dimension Parameters
from .Parameter_single_class.Parameter_e_machine_class import Parameter_e_machine               # E-Machine Parameters
from .Parameter_single_class.Parameter_gearbox_class import Parameter_gearbox                   # Gearbox Parameters
from .Parameter_single_class.Parameter_groundclearance_class import Parameter_groundclearance   # Ground clearance Parameters
from .Parameter_single_class.Parameter_LDS_class import Parameter_LDS                           # LDS Parameters
from .Parameter_single_class.Parameter_manikin_class import Parameter_manikin                   # manikin Parameters
from. Parameter_single_class.Parameter_masses_class import Parameter_masses                     # Mass Parameters
from. Parameter_single_class.Parameter_rear_axle_class import Parameter_rear_axle               # Rear Axle Parameters
from. Parameter_single_class.Parameter_regr_class import Parameters_regr                         # Regression_Parameters
from .Parameter_single_class.Parameter_wheels_class import Parameter_wheels                     # Wheel Parameters

# Import functions
from .Parameter_single_class.initialize_values import initialize_values      # Function to set attributes dynamically
# endregion


# region [1] Initialize the Class and define the Object-functions
class Parameter:
    # [1.1] Initialize the class
    def __init__(self):
        self.LDS = Parameter_LDS()
        self.battery = Parameter_battery()
        self.dimensions = Parameter_dimensions()
        self.e_machine = Parameter_e_machine()
        self.gearbox = Parameter_gearbox()
        self.groundclearance = Parameter_groundclearance()
        self.manikin = Parameter_manikin()
        self.masses = Parameter_masses()
        self.rear_axle = Parameter_rear_axle()
        self.regr = Parameters_regr()
        self.wheels = Parameter_wheels()

    # [1.2] Define the initialize function to set the attributes dynamically
    # Input:    self: Class which calls the initialize_elements method
    #           attr_first_class: Name of the added attribute
    #           values_first_class: Value of the added attribute (in the form of a dictionary)
    def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
        initialize_values(self, attr_first_class, values_first_class, insert_mode)
# endregion
