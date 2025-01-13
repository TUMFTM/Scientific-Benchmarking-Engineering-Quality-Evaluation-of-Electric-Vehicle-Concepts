"""
Description: Assign the Inputs from the Excel-Table into the respective classes inside the vehicle class
------------
Sources:  (1) SAE J1100, https://www.sae.org/standards/content/j1100_200911/
------------
Input: vehicle: Stores the calculated component volumes and masses
------------
Output: Updated vehicle class with the initialized dimensions, e-machine and battery class
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Assign vehicle outer and inner dimensions (dimensional concept)
[2] Assign the topology variables
[3] Initialization variables for the axle sizing
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import numpy as np
import copy
# endregion


def initialize_inputs(vehicle):
    # region [1] Define some parameters which have not been assigned yet
    setattr(vehicle.Input, 'ground_clearance_norm', 'EU')  # Necessary for the ground clearance computation if H156 is not given
    setattr(vehicle.Input, 'max_deflection_r', 100)  # Define the maximum deflection of the rear tires in mm
    setattr(vehicle.Input, 'extra_equipment', 0)  # No extra equipment is defined, but can be changed here
    # endregion

    # region [1] Assign vehicle outer and inner dimensions (dimensional concept)
    setattr(vehicle.dimensions.GY, 'vehicle_width', vehicle.Input.vehicle_width)        # Vehicle width W116 in mm as defined by (1)
    setattr(vehicle.dimensions.GZ, 'vehicle_height', vehicle.Input.vehicle_height)      # Vehicle height H100 in mm as defined by (1)
    setattr(vehicle.dimensions.GX, 'wheelbase', vehicle.Input.wheelbase)                # Vehicle wheelbase L101 in mm as defined by (1)
    setattr(vehicle.dimensions.GX, 'vehicle_overhang_f', vehicle.Input.overhang_front)  # Overhang front L104 in mm as defined by (1)
    setattr(vehicle.dimensions.GX, 'vehicle_overhang_r', vehicle.Input.overhang_rear)   # Overhang rear L105 in mm as defined by (1)
    vehicle_length = vehicle.dimensions.GX.wheelbase + vehicle.dimensions.GX.vehicle_overhang_f + vehicle.dimensions.GX.vehicle_overhang_r
    setattr(vehicle.dimensions.GX, 'vehicle_length', vehicle_length)                    # Calculate vehicle length L103 in mm as defined by (1)

    setattr(vehicle.dimensions.GX, 'L113', vehicle.Input.L113)      # Dash to axle ratio L113 in mm as defined by (1)
    setattr(vehicle.manikin, 'H30_1', vehicle.Input.H30)            # H30 at the design SgRP as defined by (1)
    setattr(vehicle.manikin, 'H30_2', vehicle.Input.H30_2)          # H30 at the SgRP-2 as defined by (1)
    setattr(vehicle.manikin, 'H61_2', vehicle.Input.H61_2)          # H61_2 at the SgRP-2 as defined by (1), (without the described 102 mm)

    # They user may or may have not assigned a fixed turning diameter
    if hasattr(vehicle.Input, 'turning_circle'):
        setattr(vehicle.dimensions.GY, 'turning_diameter', vehicle.Input.turning_circle)
    else:
        setattr(vehicle.dimensions.GY, 'turning_diameter', np.nan)

    # Vehicles ground clearance (If not known it will be computed in the function calc_dimensional_concept)
    setattr(vehicle.dimensions.GZ, 'H156', vehicle.Input.H156)

    # Get the rear steering angle from the Excel-Table
    rear_steering_angle = vehicle.Input.rear_steering_angle
    if np.isnan(rear_steering_angle):
        rear_steering_angle = 0
    setattr(vehicle.wheels, 'steering_angle_r', rear_steering_angle)
    # endregion

    # region [2] Assign the topology variables
    setattr(vehicle.topology, 'number_of_seats', vehicle.Input.number_of_seats)
    setattr(vehicle.topology, 'topology', vehicle.Input.topology)
    setattr(vehicle.topology, 'frameform', vehicle.Input.frameform)
    setattr(vehicle.topology, 'ground_clearance_norm', vehicle.Input.ground_clearance_norm)
    setattr(vehicle.topology, 'battery_topology', vehicle.Input.battery_integration)

    # Get the gearbox orientation from the Excel-table
    gearbox_orientation_list = vehicle.Input.machine_orientation

    # Initialize the axles and the possible gearbox position and the orientation dictionary
    axles = ['front', 'rear']
    gearbox_orientation = {'position': '', 'ID': np.nan}

    # The gearbox can be mounted in front of, behind or coaxial to the axis
    gearbox_position = ['rear', 'coaxial', 'front']
    orientation = dict()

    # Iterate through both axles and get the respective gearbox orientation
    for idx, axle in enumerate(axles):
        try:    # Check for Nans: A Nan in the orientation list means, that there is no gearbox at the respective axle
            gearbox_orientation_axle = int(gearbox_orientation_list[idx])   # Orientation at respective axle
            position = gearbox_position[int(gearbox_orientation_axle) + 1]  # Get the position of the gearbox

            # Fill in the dictionary and set the attribute to the corresponding gearbox
            gearbox_orientation['position'] = position
            gearbox_orientation['ID'] = gearbox_orientation_axle
            orientation[axle] = copy.deepcopy(gearbox_orientation)
            setattr(vehicle.gearbox[axle].Input, 'gear_orientation', orientation[axle])
        except ValueError:
            pass

    # Determine drive type according to the number of machines
    if vehicle.Input.topology.count('G') > 1:
        setattr(vehicle.topology, 'drive', 'AWD')
    else:
        if vehicle.Input.topology[-1] == 'X':
            setattr(vehicle.topology, 'drive', 'FWD')
        else:
            setattr(vehicle.topology, 'drive', 'RWD')

    for axle in vehicle.Input.gearbox_type.keys():
        try:
            if vehicle.Input.gearbox_type[axle].lower() == 'planetary':
                # The user could have chosen a planetary gearbox, but kept the 'parallel' axle layout (not feasible!).
                # To avoid this error, this for loop automatically overwrites the axle value when 'planetary' is chosen.
                gearbox_axles = getattr(vehicle.Input, 'gearbox_axles')
                gearbox_axles[axle] = 'coaxial'
                setattr(vehicle.Input, 'gearbox_axles', gearbox_axles)
        except AttributeError:
            pass
    # endregion

    # region [3] Initialization variables for the axle sizing
    setattr(vehicle.topology, 'axis_type_r', vehicle.Input.axis_type_r)
    setattr(vehicle.topology, 'spring_layout_r', vehicle.Input.spring_layout_r)

    # Assign and maximum deflection for the wheel rear model
    setattr(vehicle.dimensions.EZ, 'max_deflection_r', vehicle.Input.max_deflection_r)
    # endregion

    return vehicle
