"""
Description: This function has the task to create an empty class for the battery parameters
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
class Parameter_battery:
    # [1.1] Initialize the total Parameter_battery class (Outer Class)
    def __init__(self):
        self.packagefactor = self.packagefactor()
        self.cell = self.cell()
        self.cell_energy_density_grav = self.cell_energy_density_grav()
        self.cell_energy_density_vol = self.cell_energy_density_vol()
        self.massfactor_cell_to_module = self.massfactor_cell_to_module()
        super(Parameter_battery).__init__()

    # [1.2] Initialize the inner class of the packagefactor
    class packagefactor:
        def __init__(self):
            pass

    # [1.3] Initialize the inner class of the cell
    class cell:
        def __init__(self):
            self.dimensions_x = self.dimensions_x()
            self.dimensions_y = self.dimensions_y()
            self.dimensions_z = self.dimensions_z()

        class dimensions_x:
            def __init__(self):
                pass

        class dimensions_y:
            def __init__(self):
                pass

        class dimensions_z:
            def __init__(self):
                pass

        def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
            initialize_values(self, attr_first_class, values_first_class, insert_mode)

    # [1.4] Initialize the inner class of the gravimetric energy density of the cells
    class cell_energy_density_grav:
        def __init__(self):
            pass

    # [1.5] Initialize the inner class of the volumetric energy density of the cells
    class cell_energy_density_vol:
        def __init__(self):
            pass

    # [1.6] Initialize the inner class of the massfactor of the cells
    class massfactor_cell_to_module:
        def __init__(self):
            pass

    # [1.7] Define the initialize function to set the attributes dynamically
    # Input:    self: Class which calls the initialize_elements method
    #           attr_first_class: Name of the added attribute
    #           values_first_class: Value of the added attribute (in the form of a dictionary)
    def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
        initialize_values(self, attr_first_class, values_first_class, insert_mode)
# endregion
