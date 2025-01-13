"""
Description: This function has the task to create an empty class for the manikin parameters
             All desired attributes will be assigned dynamically based on the parameters struct of Matlab
------------
Sources: None
------------
Input: None
------------
Output: Class element for all the battery parameters
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
class Parameter_manikin:
    # [1.1] Initialize the total Parameter_manikin class (Outer Class)
    def __init__(self):
        self.deltaelbow = self.deltaelbow()
        self.deltaroof = self.deltaroof()
        self.H61_2 = self.H61_2()
        self.SW16_1 = self.SW16_1()

    # [1.2] Initialize the inner class of deltaelbox (Distance between elbow and driver)
    class deltaelbow:
        def __init__(self):
            pass

    # [1.3] Initialize the inner class of deltaroof (Difference between height at tier 1 and tier 2)
    class deltaroof:
        def __init__(self):
            self.SUV = self.SUV()
            self.Sedan = self.Sedan()
            self.Hatchback = self.Hatchback()

        class SUV:
            def __init__(self):
                pass

        class Hatchback:
            def __init__(self):
                pass

        class Sedan:
            def __init__(self):
                pass

        def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
            initialize_values(self, attr_first_class, values_first_class, insert_mode)

    class H61_2:
        def __init__(self):
            pass

    class SW16_1:
        def __init__(self):
            pass

    # [1.4] Define the initialize function to set the attributes dynamically
    # Input:    self: Class which calls the initialize_elements method
    #           attr_first_class: Name of the added attribute
    #           values_first_class: Value of the added attribute (in the form of a dictionary)
    def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
        initialize_values(self, attr_first_class, values_first_class, insert_mode)
# endregion
