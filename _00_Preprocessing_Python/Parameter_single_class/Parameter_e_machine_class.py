"""
Description: This function has the task to create an empty class for the e-machine parameters
             All desired attributes will be assigned dynamically based on the parameters struct of Matlab
------------
Sources: None
------------
Input: None
------------
Output: Class element for all the e-machine parameters
------------

Implementation
[0] Import all necessary Classes from the subfolder Parameter_single_class
[1] Initialize the Class and define the Object-functions
"""

# region [0] Import all necessary Classes and functions from the sub folders
# Import functions
from .initialize_values import initialize_values    # Function to set attributes dynamically
# endregion


# region [1] Initialize the Class and define the Object-functions
class Parameter_e_machine:
    # [1.1] Initialize the total Parameter_e_machine class (Outer Class)
    def __init__(self):
        self.CX = self.CX()
        self.EY = self.EY()
        self.stator_ratio = self.stator_ratio()

    # [1.2] Initialize the inner class of CX-Class (Housing thickness)
    class CX:
        def __init__(self):
            pass

    # [1.3] Initialize the inner class of the CY-Class (stator to machine length
    class EY:
        def __init__(self):
            pass

    # [1.4] Initialize the inner class of the stator_ratio (relation between stator and rotor length)
    class stator_ratio:
        def __init__(self):
            pass

    # [1.5] Define the initialize function to set the attributes dynamically
    # Input:    self: Class which calls the initialize_elements method
    #           attr_first_class: Name of the added attribute
    #           values_first_class: Value of the added attribute (in the form of a dictionary)
    def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
        initialize_values(self, attr_first_class, values_first_class, insert_mode)
# endregion
