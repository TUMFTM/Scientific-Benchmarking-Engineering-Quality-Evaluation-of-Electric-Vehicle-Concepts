"""
Description: This function has the task to create an empty class for the vehicle
             All desired attributes will then later be assigned dynamically based on the computations of the files
------------
Sources: None
------------
Input: None
------------
Output: Class element for the vehicle
------------

Implementation
[0] Import all necessary Classes from the subfolder Parameter_single_class
[1] Initialize the Class and define the Object-functions
"""

# region [0] Import all necessary Classes and functions from the sub folders
# Import the classes
from .Vehicle_single_class import E_Machine         # Create E_machine class
from .Vehicle_single_class import Gearbox           # Create Gearbox class
from .Vehicle_single_class import Input             # Create Input class
from .Vehicle_single_class import Battery           # Create Battery class
from .Vehicle_single_class import Dimensions        # Create Dimensions class
from .Vehicle_single_class import Wheels            # Create Wheels class
from .Vehicle_single_class import Masses            # Create Masses class
from .Vehicle_single_class import Settings          # Create Settings class
from .Vehicle_single_class import Manikin           # Create Manikin class
from .Vehicle_single_class import Topology          # Create Topology class
from .Vehicle_single_class import Exterior          # Create Exterior class
from .Vehicle_single_class import LDS               # Create the LDS class
from .Vehicle_single_class import Lateral_Dynamics  # Create the Lateral Dynamics Class
# endregion


# region [1] Initialize the vehicle class and define the Object-functions
class Vehicle:
    # [1.1] Initialize the class
    def __init__(self):
        self.Input = Input()
        self.e_machine = {'front': E_Machine(),
                          'rear': E_Machine()}
        self.gearbox = {'front': Gearbox(),
                        'rear': Gearbox()}
        self.battery = Battery()
        self.dimensions = Dimensions()
        self.wheels = Wheels()
        self.masses = Masses()
        self.manikin = Manikin()
        self.topology = Topology()
        self.settings = Settings()
        self.exterior = Exterior()
        self.LDS = LDS()
        self.Lateral_Dynamics = Lateral_Dynamics()
        self.errorlog = []

    # [1.2] Define the initialize function to set the attributes dynamically
# endregion
