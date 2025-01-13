"""
Description:    This function derives the main dimensions of the passenger compartment along the Z direction
                based on the ground clearance and the dimensions of the underbody
------------
Sources:   (1) SAE J1100 - https://www.sae.org/standards/content/j1100_200911/
           (2) SAE J1052 - Motor Vehicle Driver and Passenger Head Position, 2010.
           (3) E. Elagamy, "Creation of a Parametric Model for the Derivation of the Conceptual Dimensions for Battery Electric Vehicle", Master Thesis, 2020
           (4) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Design", Ph.D. Thesis, 2022
           (5) P. Köhler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten für Elektrofahrzeuge", Master Thesis, TUM, 2021
------------
Input:   vehicle: Class element, which stores all the vehicle information
         parameters: Class element, which stores all necessary computation parameters
------------
Output:  Updated vehicle and parameter classes with the dimensions of the passenger compartment in z-direction
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Assign Inputs
[2] Calculate position of the front AHP and the FRP at the second seat row
[3] Calculating the H30-1 and H61-1 measure (in theory possible)
[4] Theoretical dimensions at the second seat row based on a 95-percentile male manikin
[5] Calculate second row dimensions based on real head clearance
[6] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
# Import classes
# Import methods
# endregion


def calc_passenger_compartment_z(vehicle, parameters):
    # region [1]: Assign Inputs
    # Overall parameters applying to the dimensional chain in z-direction
    topology = vehicle.topology.battery_topology
    H156 = vehicle.dimensions.GZ.H156                               # ground clearance in mm
    H100 = vehicle.dimensions.GZ.vehicle_height                     # vehicle height in mm
    CZ_batt_underfloor = vehicle.dimensions.CZ.CZ_batt_underfloor   # Height of the battery modules
    H61_2 = vehicle.manikin.H61_2                                   # Real vehicle head clearance of the second seat row

    # Parameters for the estimation of the roof thickness
    # Estimated thickness of the panoramic roof along the Z direction in mm
    thick_panoramic_roof = parameters.dimensions.CZ.panoramic_roof_thickness
    # Estimated thickness of the sliding roof along the Z direction in mm
    thick_sliding_roof = parameters.dimensions.CZ.sliding_roof_thickness
    # Estimated thickness of a normal roof (no openings) along the Z direction in mm
    thick_normal_roof = parameters.dimensions.CZ.roof_thickness

    # Necessary vehicle specific information about the used roof concept
    panorama_roof = vehicle.masses.optional_extras.panorama_roof    # Boolean (affects z dimension chain)
    sliding_roof = vehicle.masses.optional_extras.sliding_roof      # Boolean (affects z dimension chain)

    # Regressions for computing the position of the head contour
    regr_head_contour = parameters.regr.interior.roof2AHP
    regr_head_second_row = parameters.regr.interior.ground2Heat_second

    # Necessary thickness of battery elements for calculating the dimensional chain
    # Distance between passenger compartment floor and battery (including pass. compr. floor thickness) in mm (3)
    EZ_passenger_compartement_floor = parameters.dimensions.EZ.pass_compartement_battery
    # Distance between module top and top cover along the vertical (Z-) direction in mm (5, p. 76)
    EZ_free_space_mod2cover = parameters.dimensions.EZ.free_space_module_to_top_cover
    # Thickness of the battery top cover in mm (5, p. 76)
    CZ_battery_top_cover = parameters.dimensions.CZ.batt_top_cover
    # Thickness of the battery bottom cover along the Z direction in mm (5, p. 76)
    CZ_batt_bottom_cover = vehicle.dimensions.CZ.batt_bottom_cover

    # The presence of a sliding roof/panorama roof reduces the headroom and changes the roof thickness
    if panorama_roof == 0 and sliding_roof == 0:
        Sunroof = 0
        RT = thick_normal_roof
    elif panorama_roof == 1:
        Sunroof = 1
        RT = thick_panoramic_roof
    elif sliding_roof == 1:
        Sunroof = 1
        RT = thick_sliding_roof
    else:
        raise Exception("A vehicle can't have a panorama and sunroof at the same time")

    # Roof offset at the second seat row
    offset_roof = getattr(parameters.manikin.deltaroof, vehicle.topology.frameform)
    # endregion

    # region [2]: Calculate position of the front AHP and the FRP at the second seat row
    if topology.lower() == 'highfloor':
        # For highfloor vehicles the reference points of the passenger compartment are
        # shifted upwards by the battery (4, page 11-12)
        Underbody_height = CZ_batt_underfloor + EZ_passenger_compartement_floor + EZ_free_space_mod2cover + \
                           CZ_batt_bottom_cover + CZ_battery_top_cover

        AHP_Z_front_axle = H156 + Underbody_height      # Position of the drivers heel point (4, page 8)
        FRP_Z_front_axle = H156 + Underbody_height      # Position of the FRP at second seat row (4, page 8)
    elif topology.lower() == 'mixedfloor':

        # Mixedfloor vehicles are characterized by a so called footwell at the front seat. The battery is cut off in
        # x-direction, so that the AHP must not be shifted.In contrary the FRP at the second seat row is shifted
        # upwards caused by the battery underneath it (4, page 11-12).
        Underbody_height = CZ_batt_underfloor + EZ_passenger_compartement_floor + EZ_free_space_mod2cover + \
                           CZ_batt_bottom_cover + CZ_battery_top_cover
        AHP_Z_front_axle = H156 + EZ_passenger_compartement_floor
        FRP_Z_front_axle = H156 + Underbody_height
    else:
        Underbody_height = 0
        # In lowfloor vehicles only the tunnel and the space underneath the seats are filled with cells.
        # Therefore the reference points of the passenger compartment are not affected by the battery (4, page 11-12)
        AHP_Z_front_axle = H156 + EZ_passenger_compartement_floor
        FRP_Z_front_axle = H156 + EZ_passenger_compartement_floor
    # endregion

    # region [3]: Calculating the H30-1 and H61-1 measure (in theory possible)
    # Distance between top of interior and ground (road) for the 1st row of seats
    AHP2interior_top = H100 - RT - AHP_Z_front_axle

    # Calculate the distance between Interior Roof and Head Contour for first seating row
    coefficients = regr_head_contour.coefficients
    AHP2headcontour = coefficients[0] + coefficients[1] * AHP2interior_top + coefficients[2] * Sunroof

    # Calculate the theoretical H30_1 (4, page 34-36)
    # Delta head contour after rotation is calculated by substituting the rotation equation into the ellipse equation,
    # then equating the derivative of the resulting equation to zero and finally, solving the equation in x and z
    # (i.e. slope = 0 or the max point of the upper curve of the ellipse)
    delta_rot = 4.27     # difference in height after the rotation of the head contour given the constants of the ellipse equation a = 211.25mm and b = 133.5mm

    # Highest point of the rotated head contur for the equation of the centroid of the head contour,
    # see (2) page 6 & 7 for the dimensions of the head contour [2] page 5
    H30_1_theo = AHP2headcontour - 638 - 52.6 - 133.5 - delta_rot   # top of head contour in mm (2, page 6)

    # Effective headroom first seat row (H61_1) (1)
    Z = AHP2interior_top - H30_1_theo
    H61_1 = Z / math.cos(math.radians(8))       # Estimated head clearance in mm

    # Calculate H5-1 (Distance from SgRP to ground for first seat row, (1))
    H5_1 = AHP_Z_front_axle + H30_1_theo
    # endregion

    # region [4]: Theoretical dimensions at the second seat row based on a 95-percentile male manikin
    # Roof offset at second seat row
    if panorama_roof == 0 and sliding_roof == 0:
        offset = offset_roof.no_sunroof
    else:
        offset = offset_roof.sunroof

    # Distance between the ground and the interior point of the roof
    interior2ground_2SR = H100 - RT - offset    # in mm

    # Calculate the top head position at the second seat row
    coefficients_2SR = regr_head_second_row.coefficients
    head2ground_2SR = coefficients_2SR[0] + interior2ground_2SR * coefficients_2SR[1] + Sunroof * coefficients_2SR[2]

    # Position an 95% male manikin inside the second row and calculate the theoretically necessary H5-2 measure
    torso_angle = 25                                                            # (2, page 3)
    delta = 0.689 * torso_angle - 9.09                                          # (2, page 6)
    manikin_second_row = 619 * math.cos(math.radians(delta)) + 44.8 + 147.07    # (2, page 6)

    # Calculate the necessary H5-2 and H30-2 measures for the 95% male manikin
    H5_2_95_percentile = head2ground_2SR - manikin_second_row                    # in mm
    H30_2_95_percentile = H5_2_95_percentile - FRP_Z_front_axle                   # in mm

    # Calculate the head clearance for this manikin
    Z = interior2ground_2SR - H5_2_95_percentile
    H61_2_95_percentile = Z/math.cos(math.radians(8))                            # in mm
    # endregion

    # region [5]: Calculate second row dimensions based on real head clearance
    # Based on the H61_2 derive the distance between SgRP2 and ground (H5_2) in mm
    H5_2 = interior2ground_2SR - H61_2 * math.cos(math.radians(8))

    # Derive from the given H30_2 the position of the FRP of the 2nd seat row with respect to the ground
    H30_2_theo = H5_2 - FRP_Z_front_axle
    # endregion

    # region [6]: Assign Outputs
    # General heights
    setattr(vehicle.dimensions.GZ, 'underbody_height',  Underbody_height)

    # Position of the heel points at first and second seat row
    # Estimated distance between passenger compartment and drivers heel point
    setattr(vehicle.manikin, 'AHP_Z_front_axle', AHP_Z_front_axle)
    # Estimated distance between passenger compartment and the heel point at the second seat row
    setattr(vehicle.manikin, 'FRP_Z_front_axle', FRP_Z_front_axle)

    # passenger compartment heights at first seat row
    setattr(vehicle.manikin, 'H5_1', H5_1)               # Estimated H5-1 measure
    setattr(vehicle.manikin, 'H61_1', H61_1)             # Estimated head clearance at front seat row
    setattr(vehicle. manikin, 'H30_1_theo', H30_1_theo)  # Theoretically possible seat height at front seat row

    # passenger compartment heights at second seat row
    setattr(vehicle.manikin, 'H5_2', H5_2)              # Estimated H5-2 measure based on real head clearance
    setattr(vehicle.manikin, 'H30_2_theo', H30_2_theo)  # Theoretically possible seat height at second seat row

    # Dimension if the 95% male manikin at second seat row
    setattr(vehicle.manikin, 'H5_2_95_percentile', H5_2_95_percentile)      # Estimated H5-2 for the 95% male manikin
    setattr(vehicle.manikin, 'H30_2_95_percentile', H30_2_95_percentile)    # Estimated H30-2 for the 95% male manikin
    setattr(vehicle.manikin, 'H61_2_95_percentile', H61_2_95_percentile)    # Estimated H61-2 for the 95% male manikin

    # Save the distance between interieur and ground for the second seat row
    # This may be used to recalculate the H61-2 measure if there is a second level filling of the battery
    setattr(vehicle.dimensions.EZ, 'interior2ground_2SR', interior2ground_2SR)
    setattr(vehicle.dimensions.EZ, 'AHP2interior_top', AHP2interior_top)
    # endregion

    return vehicle, parameters
