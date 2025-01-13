"""
Description: This function has the task to create an empty class for the gearbox parameters
             All desired attributes will be assigned dynamically based on the parameters struct of Matlab
------------
Sources: (1) Köhler: "Semi-physikalische Modellierung von Antriebsstrangkomponenten für Elektrofahrzeuge"
------------
Input: None
------------
Output: Class element for all the gearbox parameters
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
class Parameter_gearbox:
    # [1.1] Initialize the total Parameter_gearbox class (Outer Class)
    def __init__(self):
        self.MatProp = self.MatProp()
        self.GearingConst = self.GearingConst()
        self.MinSafety = self.MinSafety()
        self.ConstDim = self.ConstDim()
        self.CalcFactors = self.CalcFactors()
        self.BearCtlg = self.BearCtlg()

    # [1.2] Initialize the inner class of the mathematical constants (density, elastic modulus, etc...)
    class MatProp:
        def __init__(self):
            pass

    # [1.2] Initialize the inner class of the gearing constants (see (1) for more information)
    class GearingConst:
        def __init__(self):
            pass

    # [1.3] Initialize the inner class of the safety barriers
    class MinSafety:
        def __init__(self):
            pass

    # [1.4] Initialize the inner class of the constants of the gearbox dimensions
    class ConstDim:
        def __init__(self):
            pass

    # [1.4] Initialize the inner class of the necessary calculation factors (See (1) for more information)
    class CalcFactors:
        def __init__(self):
            pass

    # [1.5] Initialize the inner class of bearing catalogue
    class BearCtlg:
        def __init__(self):
            pass

    # [1.7] Define the initialize function to set the attributes dynamically
    # Input:    self: Class which calls the initialize_elements method
    #           attr_first_class: Name of the added attribute
    #           values_first_class: Value of the added attribute (in the form of a dictionary)
    def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
        initialize_values(self, attr_first_class, values_first_class, insert_mode)
# end region
