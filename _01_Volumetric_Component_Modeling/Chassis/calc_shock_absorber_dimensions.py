"""
Description: This function calculates the dimensions of the shock absorber. The upper
             part of the shock absorber has a different diameter than the lower part.
             ------------------ Overview dimensions shock absorber ---------------------
             ------------------------------------
             |<-height upper bearing     >|     |<upper_bearing_diameter_shock_absorber
             -----------------------------|     |
                                           |   |
                                           |   |
                                           |   |
                                          >|   |< piston_diameter
                                           |   |
                                           -----
------------
Sources: (1) M. Spreng, „Maßkettenanalyse am Hinterwagen zur Erstellung von Ersatzmodellen,“Bachelor thesis, Faculty of Mechanical Engineering, Ostbayerische Technische Hochschule Regensburg, Regensburg, 2020.
         More information to the shock absorber sizing can be found at (1)
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: he vehicle structure updated with the shock absorber dimensions
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Size the shock absorber
[2] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
# endregion

def calc_shock_absorber_dimensions(vehicle, parameters):
    # region [1] Assign Inputs
    # Weight limit for the assignment of the shock absorber diameter.
    # Above this weight limit the diameter of the shock absorber has to increase
    weight_limit = parameters.rear_axle.weight_limit_shock_absorber   # in kg

    # Axis load and type
    axis_load_rear = vehicle.masses.axle_load_r_max     # in kg
    axis_type = vehicle.topology.axis_type_r
    # endregion

    # region [2] Size the shock absorber
    # Size the shock absorber based on the weight limit and the axle type (analysis conducted by (1))
    if axis_load_rear < weight_limit:
        match axis_type:
            case 'torsion_beam':
                # [mm] Average after categorisation
                piston_diameter = parameters.dimensions.CX.piston_diameter_r.torsion_beam

            case 'trapezoidal_link':
                # [mm] Average after categorisation
                piston_diameter = parameters.dimensions.CX.piston_diameter_r.trapezoidal_link

            case 'sword_arm_link':
                # [mm] Average after categorisation
                piston_diameter = parameters.dimensions.CX.piston_diameter_r.sword_arm_link

            case _:     # five_link
                # [mm] Average after categorisation
                piston_diameter = parameters.dimensions.CX.piston_diameter_r.five_link
    else:
        # the axle load has a particularly high value, a schock absorber with a bigger diameter is therefore required
        # [mm] Average after categorisation
        piston_diameter = parameters.dimensions.CX.piston_diameter_r.max_weight

    # Assign the diameter the upper part of the shock absorber (constant for all vehicles)
    upper_bearing_diameter_shock_absorber = parameters.dimensions.CX.upper_bearing_diameter_shock_absorber  # in mm

    # Assign the height of the shock absorber upper part in mm (constant from all the vehicles)
    height_upper_bearing_shock_absorber = parameters.dimensions.CZ.height_upper_bearing_shock_absorber
    # endregion

    # region [3] Assign Outputs
    # Position and dimensions of the shock absorber in mm
    setattr(vehicle.dimensions.CX, 'piston_diameter', piston_diameter)
    setattr(vehicle.dimensions.CX, 'upper_bearing_diameter_shock_absorber', upper_bearing_diameter_shock_absorber)
    setattr(vehicle.dimensions.CZ, 'height_upper_bearing_shock_absorber', height_upper_bearing_shock_absorber)
    # endregion

    return vehicle, parameters
