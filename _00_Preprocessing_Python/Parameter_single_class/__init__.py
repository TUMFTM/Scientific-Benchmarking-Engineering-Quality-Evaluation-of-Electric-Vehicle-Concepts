# Function to connect the different path elements so that the subfolder struct is working
# Import classes
from .Parameter_LDS_class import Parameter_LDS                          # LDS Parameter class
from .Parameter_battery_class import Parameter_battery                  # Battery Parameter class
from .Parameter_dimension_class import Parameter_dimensions             # Dimensions Parameter class
from .Parameter_e_machine_class import Parameter_e_machine              # E-Machine Parameter class
from .Parameter_gearbox_class import Parameter_gearbox                  # Gearbox Parameter class
from .Parameter_groundclearance_class import Parameter_groundclearance  # Ground clearance Parameter class
from .Parameter_manikin_class import Parameter_manikin                  # Manikin Parameter class
from .Parameter_masses_class import Parameter_masses                    # Masses Parameter class
from .Parameter_regr_class import Parameters_regr                        # Regression Parameter class
from .Parameter_rear_axle_class import Parameter_rear_axle              # Rear Axle Parameter class
from .Parameter_wheels_class import Parameter_wheels                    # Wheel Parameter class

# Import methods
from .initialize_values import initialize_values  # Method to set class attributes dynamically
