"""
Description: This function has the task to create an empty class for the dimension parameters
             All desired attributes will be assigned dynamically based on the parameters struct of Matlab
------------
Sources: None
------------
Input: None
------------
Output: Class element for all the dimension parameters
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

class Parameter_dimensions:
    # [1.1] Initialize the total Parameter_dimensions class (Outer Class)
    def __init__(self):
        self.CX = self.CX()
        self.CY = self.CY()
        self.CZ = self.CZ()
        self.EX = self.EX()
        self.EY = self.EY()
        self.EZ = self.EZ()
        self.GZ = self.GZ()

    # [1.2] Initialize the inner class of the CX dimension (X-Dimension of the chassis)
    class CX:
        def __init__(self):
            self.piston_diameter_r = self.piston_diameter_r()

        class piston_diameter_r:
            def __init__(self):
                pass

        def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
            initialize_values(self, attr_first_class, values_first_class, insert_mode)

    # [1.3] Initialize the inner class of the CX dimension (Y-Dimension of the chassis)
    class CY:
        def __init__(self):
            self.axis_length_rear = self.axis_length_rear()
            self.wheel_carrier = self.wheel_carrier()

        class axis_length_rear:
            def __init__(self):
                pass

        class wheel_carrier:
            def __init__(self):
                pass

        def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
            initialize_values(self, attr_first_class, values_first_class, insert_mode)

    # [1.4] Initialize the inner class of the CX dimension (Z-Dimension of the chassis)
    class CZ:
        def __init__(self):
            self.batt_cooling = self.batt_cooling()
            self.batt_bottom_cover = self.batt_bottom_cover()
            self.wheel_carrier = self.wheel_carrier()

        class batt_bottom_cover:
            def __init__(self):
                pass

        class batt_cooling:
            def __init__(self):
                pass

        class wheel_carrier:
            def __init__(self):
                pass

        def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
            initialize_values(self, attr_first_class, values_first_class, insert_mode)

    # [1.5] Initialize the inner class of the EX dimension (X-Dimension of the battery)
    class EX:
        def __init__(self):
            pass

        def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
            initialize_values(self, attr_first_class, values_first_class, insert_mode)

    # [1.6] Initialize the inner class of the EY dimension (Y-Dimension of the battery)
    class EY:
        def __init__(self):
            self.sa_wheelcarrier = self.sa_wheelcarrier()
            self.battery_width_factor = self.battery_width_factor()

        class sa_wheelcarrier:
            def __init__(self):
                pass

        class battery_width_factor:
            def __init__(self):
                pass
        def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
            initialize_values(self, attr_first_class, values_first_class, insert_mode)

    # [1.6] Initialize the inner class of the EZ dimension (Z-Dimension of the battery)
    class EZ:
        def __init__(self):
            self.offset_cell2module = self.offset_cell2module()


        class offset_cell2module:
            def __init__(self):
                pass

        def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
            initialize_values(self, attr_first_class, values_first_class, insert_mode)

    # [1.7] Initialize the inner class of the GZ dimension (Z-Dimension of the entire vehicle)
    class GZ:
        def __init__(self):
            self.H156 = self.H156()

        class H156:
            def __init__(self):
                pass

        def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
            initialize_values(self, attr_first_class, values_first_class, insert_mode)

    # [1.8] Define the initialize function to set the attributes dynamically
    # Input:    self: Class which calls the initialize_elements method
    #           attr_first_class: Name of the added attribute
    #           values_first_class: Value of the added attribute (in the form of a dictionary)
    def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
        initialize_values(self, attr_first_class, values_first_class, insert_mode)
# endregion
