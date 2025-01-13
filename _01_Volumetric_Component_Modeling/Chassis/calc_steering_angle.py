"""
Description: This function calculates the steering angle at the front axle based on the turning diameter
             of the vehicle and the (if available) angle of the rear steering wheels.
             Therefore in a first step the steering angle of the outer wheel is estimated by the equations
             described by Kücükay (page 6-10) in (1). In a second step the steering angle of the inner wheel
             is estimated based on the descriptions of Pfeffer (2, page 51-56). A summary is given in Fundel (3, p.36-39)
------------
Sources: (1) Ferit Kücükay, Grundlagen der Fahrzeugtechnik, 2022, Springer Verlag, page 6-10, DOI: 10.1007/978-3-658-36727-5_1
         (2) Peter Pfeffer, "Lenkungshandbuch", 2011, Springer Verlag, page 51 -56. DOI: 10.1007/978-3-658-00977-9
         (3) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
------------
Input: turning_diameter: Turning diameter of the vehicle in meter
       delta_f_r_deg: Angle of the rear steering in degree
       wheelbase: Wheelbase of the vehicle in mm
       overhang_f: Overhang of the vehicle in mm
       width: Vehicle width in mm
       track_f: track width at the front wheels
------------
Output: delta_f_o_deg: Steering angle of the outer wheel at the front axle in degree
        delta_f_i_deg: Steering angle of the inner wheel at the front axle in degree
        turning_diameter: Calculated turning diameter (same as the given one in a given tolerance intervall)
------------

Implementation
[0] Import modules, classes and functions
[1] Define necessary parameters
[2] Calculate the simulated outer steering angle
[3] Calculate the inner steering angle
------------
"""

# region [0] Import modules, classes and functions
# import modules
import math
# endregion


def calc_steering_angle(turning_diameter, delta_f_r_deg, wheelbase, overhang_f, width, track_f):
    # region [1] Define necessary parameters
    # Auxiliary parameter to make the following equation easier to write:
    dis_wheelcenter_wheel = (width-track_f)/2

    # Get corresponding aim radius in mm
    turning_radius = turning_diameter * 1000 / 2

    # Transform rear axle steering angle into a negative angle for the calculations
    delta_f_r_deg = -1 * delta_f_r_deg

    # Rear axle steering angle in rad
    delta_f_r_rad = math.radians(delta_f_r_deg)

    # Start angle for the front wheel steering in deg
    delta_f_o_deg = 10

    # Iterations settings
    tolerance = 0.001
    iterations = 1

    # Angle between the center of the wheel and the outermost point of the car body
    helpangle_xi = math.atan(dis_wheelcenter_wheel / overhang_f)
    # Distance between the center of the wheel and the outermost point of the car body
    lcv = math.sqrt(math.pow(overhang_f, 2) + math.pow(dis_wheelcenter_wheel, 2))
    # endregion

    # region [2] Calculate the simulated outer steering angle
    while True:
        # Convert the steering angle of the front wheels into radian
        delta_f_o_rad = math.radians(delta_f_o_deg)

        # Calculate the turning radius of the wheel center
        turning_radius_wheel = wheelbase * math.cos(delta_f_r_rad) / math.sin(delta_f_o_rad - delta_f_r_rad)

        # Define help parameter
        help_epsilon_C = (lcv / turning_radius_wheel) * (1 / math.cos(delta_f_o_rad + helpangle_xi)) + \
                          math.tan(delta_f_o_rad + helpangle_xi)

        # Angle in the triangle (Wheelcenter, Outer Point and center of rotation)
        epsilon_C = math.atan(1 / help_epsilon_C)

        # Calculate the turning radius
        turning_radius_sim = turning_radius_wheel * math.cos(delta_f_o_rad + helpangle_xi) / math.sin(epsilon_C)

        # Check if the calculated turning radius is within a tolerance with the real turning_diameter
        if abs(turning_radius_sim - turning_radius) < tolerance or iterations > 250:
            break
        else:
            iterations += 1

            # Get scaling factor based on the results of the simulated turning radius
            scaling_factor = turning_radius_sim/turning_radius
            delta_f_o_deg = delta_f_o_deg * scaling_factor

    # Recalculate the simulated turning diameter
    turning_diameter_sim = turning_radius_sim * 2 / 1000
    # endregion

    # region [3] Calculate the inner steering angle
    # Ackermann condition: cot(delta_out) = cot(delta_inner) + j/l defined in (2, p. 51)
    ackermann_outer = (1/math.tan(delta_f_o_rad))

    # Define scrub radius as zero because for defining the front wheelhouse the rotational point of the wheel
    # is defined as its middle point (see graphics in (1 p. 1008, 2 p. 51))
    scrub_radius = 0

    # Calculate the spreading axis distance (2, p. 51)
    j = track_f - 2 * scrub_radius

    # Calculate the inner steering angle
    delta_f_i_rad = math.atan(1/(ackermann_outer - j/wheelbase))
    delta_f_i_deg = math.degrees(delta_f_i_rad)
    # endregion

    return delta_f_i_deg, delta_f_o_deg, turning_diameter_sim
