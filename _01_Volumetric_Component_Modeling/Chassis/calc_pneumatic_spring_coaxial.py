"""
Description: This function estimates the dimensions of the pneumatic spring at the rear axle (if present).
             First of all the unsprung mass is calculated, then knowing the position and inclination of the
             shock absorber the corresponding air suspension transmission ratio is calculated, finally the
             required air spring diameter is derived from the forces caused by the undamped mass.
------------
Sources: (1) M. Spreng, "Maßkettenanalyse am Hinterwagen zur Erstellung von Ersatzmodellen",“Bachelor thesis, Faculty of Mechanical Engineering, Ostbayerische Technische Hochschule Regensburg, Regensburg, 2020.
         More information to the shock absorber sizing can be found at (1)
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The diameter of the air spring will be assigned to the upper part of the shock absorber
        Same happens with the height of the air spring and the height of the upper part of the shock absorber
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Calculate the undamped mass at the rear axle
[3] Calculate the resulting force on the spring and therefore the required diameter
[4] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
import math
# endregion


def calc_pneumatic_spring_coaxial(vehicle, parameters):

    # region [1] Assign Inputs
    # General vehicle data
    width = vehicle.dimensions.GY.vehicle_width         # Vehicle width in mm
    axle_load_r_max = vehicle.masses.axle_load_r_max    # Maximum load on the rear axle in kg
    vehicle_form = vehicle.topology.frameform           # Frame form (SUV, Hatchback or Sedan)

    # Loads and axle dimensions axle load in kg
    axis_type = vehicle.topology.axis_type_r                                    # Type of selected axis
    EY_axis = vehicle.dimensions.EY.axis_vehicle_center                         # Minimum distance between axis rotation point and vehicle center in mm
    ax_len_lower_axis = vehicle.dimensions.CY.axis_length_r                     # Rear axle length in mm
    EY_lop = vehicle.dimensions.EY.lower_point_shock_absorber_vehicle_center    # Distance between lower shock absorber point and vehicle center in mm
    alpha_sa = vehicle.wheels.angle_shock_absorber_r                            # Inclination angle of the shock absorber in DEG!

    # Constant values (derived empirically) for the simulation
    sping_height = 255                  # Air spring height in mm -> Typical value from empirical analysis
    bellows_thickness_coaxial = 12      # Thickness of the bellows for the coaxial spring
    wall_thickness_coaxial = 2          # Wall thickness for the coaxial spring
    allowed_pressure = 1150000          # Maximum allowed spring pressure in Pa

    # Regressions and constant values for the mass calculation
    masses_brake_pads = parameters.masses.brake_pads
    regr_brake_caliper = parameters.regr.mass.brake_caliper.coefficients
    regr_brake_disc = parameters.regr.mass.brake_disc.coefficients
    regr_rim = parameters.regr.mass.rim.coefficients
    regr_tire = parameters.regr.mass.tire.coefficients

    # Further data required for the mass modeling
    rim_diameter_in_inches = vehicle.dimensions.CX.rim_diameter_r_inch  # Diameter of the rims in inches
    tire_width = vehicle.dimensions.CY.wheel_r_width                    # Width of the rear tires in mmm
    tire_diameter = vehicle.dimensions.CX.wheel_r_diameter              # Diameter of the rear tires in mm
    brake_disc_diameter = vehicle.dimensions.CX.brake_disc_r_diameter   # Diameter of the brake disc in mm

    # Initialize the undamped mass vector
    undamped_mass_vec = np.zeros(9)
    # endregion

    # region [2] Calculate the undamped mass at the rear axle
    # Sum of all the two brake calipers weight in kg
    undamped_mass_vec[0] = (regr_brake_caliper[0] + regr_brake_caliper[1] * brake_disc_diameter) * 2

    # Weight brake pads at front and rear axle in kg
    undamped_mass_vec[1] = masses_brake_pads

    # Weight of the two rear brake discs
    undamped_mass_vec[2] = (regr_brake_disc[0] + regr_brake_disc[1] * brake_disc_diameter) * 2

    # Weight of the two rear rims in kg
    undamped_mass_vec[3] = (regr_rim[0] + regr_rim[1] * rim_diameter_in_inches) * 2

    # Weight of the two rear tires in kg
    undamped_mass_vec[4] = (regr_tire[0] + regr_tire[1] * tire_width + regr_tire[2] * tire_diameter) * 2

    # Suspension control arms, subframe, ARB
    if axis_type.lower() == 'torsion_beam':
        undamped_mass_vec[5] = -103.155 + 0.008 * axle_load_r_max + 0.074 * width      # [kg]
    else:    # All other axle types
        undamped_mass_vec[5] = -145.310 + 0.009 * axle_load_r_max + 0.104 * width      # [kg]

    # Dampers weight
    undamped_mass_vec[6] = 2 * (-25.624 + 0.002 * axle_load_r_max + 0.015 * width)      # [kg]

    # Weight of air spring and its component
    if vehicle_form == 'SUV':
        undamped_mass_vec[7] = 2.42         # [kg]
    else:
        undamped_mass_vec[7] = 1.22         # [kg]

    # Air cushion, compressor, distributor, protection
    undamped_mass_vec[8] = 10.12            # [kg]

    # Total undamped mass in kg
    undamped_mass = np.sum(undamped_mass_vec)
    # endregion

    # region [3] Calculate the resulting force on the spring and therefore the required diameter
    # Calculate the transmission ratio for the shock absorber
    i_sa = (EY_lop - EY_axis) / ax_len_lower_axis

    # Correct the transmission ration for the inclination angle of the shock absorber
    # -> Thus deriving the transmission ratio for the coaxial spring
    i_sa = i_sa*math.cos(math.radians(alpha_sa))

    # Resulting coil force on the air spring (in N)
    coil_force = (((axle_load_r_max - undamped_mass) / 2) * 9.81) / i_sa

    # calculation effective surface (in m^2)
    effective_surface = coil_force / allowed_pressure   # [N/m] the needed effective surface for the allowed pressure

    # diameter of the effective surface (in mm)
    diameter_effective_surface = (2 * math.sqrt(effective_surface / math.pi) * 1000)

    # Calculate the total outer diameter, considering also the presence of the bellows (in mm)
    diameter_air_suspension = diameter_effective_surface + bellows_thickness_coaxial + 2 * wall_thickness_coaxial
    # endregion

    # region [4] Assign Outputs
    # Resulting air spring dimensions in mm
    setattr(vehicle.dimensions.CX, 'upper_bearing_diameter_shock_absorber', diameter_air_suspension)
    setattr(vehicle.dimensions.CZ, 'height_upper_bearing_shock_absorber', sping_height)
    # endregion

    return vehicle, parameters
