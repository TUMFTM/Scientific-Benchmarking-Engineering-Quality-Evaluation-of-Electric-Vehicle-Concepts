"""
Description:    This calculates the ground clearance of the vehicles between front and rear axis.
                To do so it differentiates between highfloor (SUVs) and flatfloor (Passenge cars).
                It is possible to assign a different ground clearance (as defined by the corresponding norms).
                The ground clearance will be calculated according to the chosen norm.
------------
Sources:    (1) ISO 612: Description of ramp angle, approach angle etc.
            (2) DIN 70020: German equivalent to ISO 612
            (3) EG 2007/46: Law for the ground clearance of SUV in Europa
            (4) 49 CFR: Law for the ground clearance of SUV in the USA
            (5) KMVSS MOLIT 577: Law for the ground clearance for ALL VEHICLE TYPES in South Korea
            (6) SAE J689: Typical ramp angles and approach angles for flatfloor vehicles
            (7) Assumptions from: Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Design", FTM, 2022
------------
Input:   vehicle: Class element, which stores all the vehicle information
         parameters: Class element, which stores all necessary computation parameters
------------
Output:  The values required for drawing the ground clearance surfaces
         The ground clearance between the axis (H156) required for positioning the battery
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Assign Inputs
[2] Calculate the ground clearance depending on the chosen norm
[3] Assign Outputs
[4] Subfunctions
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import numpy as np
import math
# Import classes
# Import methods
# endregion


def calc_ground_clearance(vehicle, parameters):
    # region [1]: Assign Inputs
    wheelbase = vehicle.dimensions.GX.wheelbase                         # in mm
    radius_f = vehicle.dimensions.CX.wheel_f_diameter/2                 # in mm
    radius_r = vehicle.dimensions.CX.wheel_r_diameter/2                 # in mm
    ground_clearance_norm = vehicle.topology.ground_clearance_norm      # Ground clearance norm

    offset_tire = parameters.groundclearance.offset_tire                # in mm, to compensate for tire flatness
    H156_min_highfloor_axle = parameters.groundclearance.at_the_axle    # Minimum value between the axle for LDT and M1G
    H156_min_highfloor = parameters.dimensions.GZ.H156.highfloor        # Minimum value between the axle for LDT and M1G
    H156_min_corea = parameters.dimensions.GZ.H156.flatfloor            # Minimum ground clearance for Corea norm in mm#
    # endregion

    # region [2]: Calculate the ground clearance depending on the chosen norm
    match ground_clearance_norm:
        case 'Corea':   # Value modeled according to (1)
            H156 = H156_min_corea   # Equal to 100 mm
            x_max_ramp = wheelbase/2

            # Assign value for the ground clearance at the axle
            ground_clearance_axle = H156_min_corea

        case 'EU':
            # Combination of values from (6) and own assumptions (7)

            # Angles in deg
            ramp_angle = 12                 # (6)
            H156_min_flatfloorEU = 135      # (7)

            # Calculate the required ground clearance to ensure the ramp angle
            GZ_H156_ramp_angle, x_max_ramp = calc_ramp_angle(wheelbase, radius_f, radius_r, offset_tire, ramp_angle)

            # Take the stricter requirement as ground clearance requirement
            H156 = max(GZ_H156_ramp_angle, H156_min_flatfloorEU)

            # Assign value for the ground clearance at the axle
            ground_clearance_axle = H156_min_corea

        case 'LDT':  # Based on (4)
            # Angles in degree
            ramp_angle = parameters.groundclearance.ramp_angle_LDT          # Ramp angle front according to CFR49

            # Calculate the required ground clearance to ensure the ramp angle
            GZ_H156_ramp_angle, x_max_ramp = calc_ramp_angle(wheelbase, radius_f, radius_r, offset_tire, ramp_angle)
            H156 = max(GZ_H156_ramp_angle, H156_min_highfloor)

            # Assign value for the ground clearance at the axle
            ground_clearance_axle = H156_min_highfloor_axle

        case 'M1G':  # Based on (3)

            # Ramp angle in deg, EG norm for M1G class
            ramp_angle = parameters.groundclearance.ramp_angle_EG       # Ramp angle front according to M1G

            # Calculate the required ground clearance to ensure the ramp angle
            GZ_H156_ramp_angle, x_max_ramp = calc_ramp_angle(wheelbase, radius_f, radius_r, offset_tire, ramp_angle)

            # Take the stricter requirement as ground clearance requirement
            H156 = max(GZ_H156_ramp_angle, H156_min_highfloor)

            # Assign value for the ground clearance at the axle
            ground_clearance_axle = H156_min_highfloor_axle

        case 'personalized':    # It is also possible to give a 'personalized' value of the H156

            H156 = vehicle.dimensions.GZ.H156
            ground_clearance_axle = vehicle.dimensions.GZ.H156

            # Set the ramps and approach angle surface so, that no matter what the value in Z is always 120 mm
            x_max_ramp = wheelbase/2
        case _:
            # Abandond the calculation
            raise Exception('THE CHOSEN GROUND CLEARANCE OPTION IS NOT IMPLEMENTED')
    # endregion

    # region [3]: Assign Outputs
    setattr(vehicle.dimensions.GZ, 'H156', H156)
    setattr(vehicle.dimensions.GZ, 'X_pos_max_ramp_height', x_max_ramp)
    setattr(vehicle.dimensions.GZ, 'ground_clearance_axle', ground_clearance_axle)
    return vehicle, parameters


# region [4]: Subfunctions
def calc_ramp_angle(wheelbase, radius_f, radius_r, offset_tire, ramp_angle):
    """
    Description: This function calculates the required ground clearance for the given
    ramp angle and generates a point cloud to describe the ramp angle surface
    """

    # For the calculation of the tangents, half of the ramp angle needs to be used -> see norm EG 2007/46
    ramp_angle = (math.pi/180) * (ramp_angle/2)

    # Find one point where the tangent to the front wheel passes through
    X_tan_f = offset_tire                                   # The point would actually be at X=0 (at the X of the wheel center), correct it with an offset, to take into account the
    Z_tan_f = -(radius_f/math.cos(ramp_angle) - radius_f)   # The corresponding Z coordinate

    # The slope of the tangent is equal to the ramp angle/2
    m = math.tan(ramp_angle)

    # Calculate intersect of the tanget
    q1 = Z_tan_f - m*X_tan_f

    # Draw the tangent of the front wheel
    x_tan_f = np.linspace(0, wheelbase, 20000)
    z_tan_f = m * x_tan_f + q1

    # Find one point where the tangent to the rear wheel passes through
    X_tan_r = wheelbase-offset_tire
    Z_tan_r = -(radius_r/math.cos(ramp_angle) - radius_r)

    # Find the intercept of the tangent at the rear wheel
    q2 = Z_tan_r + m * X_tan_r

    # Draw the tangent of the rear wheel
    x_tan_r = np.linspace(0, wheelbase, 20000)
    z_tan_r = -m * x_tan_r + q2

    # Find the minimum difference between the two tangents (intersecting point)
    idx = np.argmin(np.abs(z_tan_f - z_tan_r))

    # resulting ground clearance, considering the ramp angle requirement
    GZ_H156_ramp_angle = z_tan_f[idx]

    # Find X position with the max ramp height
    x_max_ramp = x_tan_r[idx]

    # Function handle for the ramp surface
    # rampsurface = lambda x: x*[m(x <= x_tan_r[idx]),-m(x > x_tan_r[idx])] + 1 * [q1(x <= x_tan_r[idx]), q2(x > x_tan_r[idx])]
    return GZ_H156_ramp_angle, x_max_ramp
