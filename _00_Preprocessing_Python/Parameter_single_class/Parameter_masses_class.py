"""
Description: This function has the task to create an empty class for the mass parameters
             All desired attributes will be assigned dynamically based on the parameters struct of Matlab
------------
Sources: None
------------
Input: None
------------
Output: Class element for all the mass parameters
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
class Parameter_masses:
    # [1.1] Initialize the total Parameter_masses class (Outer Class)
    def __init__(self):
        pass
        self.payload = self.payload()
        self.reserve = self.reserve()
        self.loads = self.loads()
        self.battery_electrics = self.battery_electrics()
        self.cluster_system = self.cluster_system()
        self.coolant = self.coolant()
        self.fenders = self.fenders()
        self.noise_insulation = self.noise_insulation()
        self.speaker = self.speaker()
        self.toolbox = self.toolbox()

    # [1.2] Initialize the inner class of the payload
    class payload:
        def __init__(self):
            pass

    # [1.3] Initialize the inner class of the reserve of the tires (88 and 100 rule)
    class reserve:
        def __init__(self):
            pass

    # [1.4] Initialize the inner class of the loads based on the drive train (AWD,RWD,FWD)
    class loads:
        def __init__(self):
            self.axle_load_front = self.axle_load_front()

        class axle_load_front:
            def __init__(self):
                pass

        def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
            initialize_values(self, attr_first_class, values_first_class, insert_mode)

    # [1.5] Initialize the inner class of the battery_electrics
    class battery_electrics:
        def __init__(self):
            pass

    # [1.6] Initialize the inner class of the cluster system (analog or digital)
    class cluster_system:
        def __init__(self):
            pass

    # [1.7] Initialize the inner class of the coolant fluid
    class coolant:
        def __init__(self):
            pass

    # [1.8] Initialize the inner class of the fenders (alu or steel)
    class fenders:
        def __init__(self):
            pass

    # [1.9] Initialize the inner class of the noise_insulation based on car segment
    class noise_insulation:
        def __init__(self):
            pass

    # [1.10] Initialize the inner class of the speaker
    class speaker:
        def __init__(self):
            pass

    # [1.11] Initialize the inner class of the toolbox
    class toolbox:
        def __init__(self):
            pass

    # [1.12] Define the initialize function to set the attributes dynamically
    # Input:    self: Class which calls the initialize_elements method
    #           attr_first_class: Name of the added attribute
    #           values_first_class: Value of the added attribute (in the form of a dictionary)
    def initialize_elements(self, attr_first_class, values_first_class, insert_mode):
        initialize_values(self, attr_first_class, values_first_class, insert_mode)
# endregion
