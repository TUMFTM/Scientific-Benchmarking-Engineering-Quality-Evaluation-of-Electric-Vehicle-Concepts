"""
Description: This function has the task to create an empty class for the regressions
             All desired attributes will be assigned dynamically based on the parameters struct of Matlab
------------
Sources: None
------------
Input: None
------------
Output: Class element for all the regression parameters
------------

Implementation
[0] Import all necessary Classes from the subfolder Parameter_single_class
[1] Initialize the Class and define the Object-functions
"""

# region [0] Import all necessary Classes and functions from the sub folders
# Import functions
from .initialize_values import initialize_values_regr    # Function to set attributes dynamically
# endregion


# region [1] Initialize the Class and define the Object-functions
class Parameters_regr:
    # [1.1] Initialize the total Parameter_battery class (Outer Class)
    def __init__(self):
        self.exterior = self.exterior()
        self.mass = self.mass()
        self.wheel = self.wheel()
        self.gearbox = self.gearbox()
        self.interior = self.interior()
        self.LDS = self.LDS()
        self.e_machine = self.e_machine()

    # [1.2] Initialize the inner class for the exterior regressions
    class exterior:
        def __init__(self):
            pass

    # [1.3] Initialize the inner class for the mass regressions
    class mass:
        def __init__(self):
            self.door_driver = self.door_driver()
            self.door_rear = self.door_rear()
            self.front_fenders = self.front_fenders()
            self.headlights = self.headlights()
            self.hood = self.hood()
            self.tailgate = self.tailgate()

        # [1.3.1] Initialize the nested class for the driver's door mass (alu, steel)
        class door_driver:
            def __init__(self):
                pass

            def initialize_elements(self, attr_first_class, values_first_class):
                initialize_values_regr(self, attr_first_class, values_first_class)
        # [1.3.2] Initialize the nested class for the rear door mass (alu, steel)
        class door_rear:
            def __init__(self):
                pass

            def initialize_elements(self, attr_first_class, values_first_class):
                initialize_values_regr(self, attr_first_class, values_first_class)
        # [1.3.3] Initialize the nested class for the front fenders mass (alu, steel)
        class front_fenders:
            def __init__(self):
                pass

            def initialize_elements(self, attr_first_class, values_first_class):
                initialize_values_regr(self, attr_first_class, values_first_class)
        # [1.3.4] Initialize the nested class for the headlights mass (halogen, LED, Xenon)
        class headlights:
            def __init__(self):
                pass

            def initialize_elements(self, attr_first_class, values_first_class):
                initialize_values_regr(self, attr_first_class, values_first_class)
        # [1.3.5] Initialize the nested class for the hood mass (alu, steel)
        class hood:
            def __init__(self):
                pass

            def initialize_elements(self, attr_first_class, values_first_class):
                initialize_values_regr(self, attr_first_class, values_first_class)
        # [1.3.6] Initialize the nested class for the tailgate mass (alu, steel)
        class tailgate:
            def __init__(self):
                pass

            def initialize_elements(self, attr_first_class, values_first_class):
                initialize_values_regr(self, attr_first_class, values_first_class)

        # [1.3.7] Define the initialize function for the regression to set the regression attributes dynamically
        # Input:    self: Class which calls the initialize_elements method
        #           attr_first_class: Name of the added attribute
        #           values_first_class: Value of the added attribute (in the form of a dictionary)
        def initialize_elements(self, attr_first_class, values_first_class):
            initialize_values_regr(self, attr_first_class, values_first_class)

    # [1.4] Initialize the inner class for the wheel regressions
    class wheel:
        def __init__(self):
            pass

    # [1.5] Initialize the inner class for the gearbox regressions
    class gearbox:
        def __init__(self):
            pass

    # [1.6] Initialize the inner class for the interior regressions
    class interior:
        def __init__(self):
            self.L115_2 = self.L115_2()

        # [1.6.1] Initialize the nested class for the estimation of the L115-2 measure (SUV, Sedan, Hatchback)
        class L115_2:
            def __init__(self):
                pass

            def initialize_elements(self, attr_first_class, values_first_class):
                initialize_values_regr(self, attr_first_class, values_first_class)

        # [1.6.2] Define the initialize function for the regression to set the regression attributes dynamically
        # Input:    self: Class which calls the initialize_elements method
        #           attr_first_class: Name of the added attribute
        #           values_first_class: Value of the added attribute (in the form of a dictionary)
        def initialize_elements(self, attr_first_class, values_first_class):
            initialize_values_regr(self, attr_first_class, values_first_class)

    # [1.7] Initialize the inner class for the wheel regressions
    class LDS:
        def __init__(self):
            pass

    # [1.8] Initialize the inner class for the e-machine regressions
    class e_machine:
        def __init__(self):
            pass

    # [1.9] Define the initialize function for the regression to set the regression attributes dynamically
    # Input:    self: Class which calls the initialize_elements method
    #           attr_first_class: Name of the added attribute
    #           values_first_class: Value of the added attribute (in the form of a dictionary)
    def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
        initialize_values_regr(self, attr_first_class, values_first_class)
# endregion
