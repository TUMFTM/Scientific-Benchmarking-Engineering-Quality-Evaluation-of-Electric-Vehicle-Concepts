"""
Description: This function calculates the distance between the cooling system and the
             cross member on the front axle. This function calculates a minimal
             distance in order to ensure that the cooling system does not get damaged for the AZT test
------------
Sources: (1) Stephan Wagner, Master Thesis, “Erstellung geometrischer Ersatzmodelle für die Konzeptauslegung von Komponentenabständen im Vorderwagen“, 2018
         (2) M. Felgenhauer, Automated Development of Modular Systems for the Vehicle Front of Passenger Cars, Ph.D. Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2019.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: Free space for ATZ test. This space cannot be used as installation space at the vehicle's front-end
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Calculate minimum distance for ATZ Test
[3] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
import math
# endregion


def calc_cooling_system(vehicle):
    # region [1] Assign Inputs
    vehicle_weight = vehicle.masses.vehicle_max_weight

    # 0 = Only one crossbeam member (no distinction between lower and upper cross member)
    # 1 = There is a lower and an upper cross member
    second_level = 0
    # endregion

    # region [2] Calculate minimum distance for ATZ Test
    # Crash speed in km/h (1, pag. 72)
    crash_speed = 16

    # Efficiency CMS (1, pag. 77)
    eta_CMS = 0.788

    # Energy percentage which is absorbed elastic, i.e. without deformation (1, page 67)
    Energy_elastic_percentage = 0.1

    # Absolute value in kJ of the energy, which is absorbed by the other components (lights etc...). Value from the Audi data
    Energy_other_components = 4965.65   # in kJ

    Peak_level_second_level = 30        # kN

    # Calculation energies:
    E_kin = 0.5 * vehicle_weight * math.pow((crash_speed/3.6), 2)    # Calculation energy before crash
    E_defo = (1 - Energy_elastic_percentage) * E_kin    # Calculation of the percentage, which has to be absorbed in deformation energy
    E_defo_CMS = E_defo - Energy_other_components       # Calculation of the deformation energy which has to be absorbed by the CMS

    # Tickbox:
    if second_level == 0:   # No second level
        Peak_force = -4.4575 + vehicle_weight * 0.0866  # Regression

    else:   # With a second level
        Peak_force = -4.4575 + vehicle_weight * 0.0866 + Peak_level_second_level

    dist_crossmember_cooling_system = E_defo_CMS/(eta_CMS * Peak_force)
    # endregion

    # region [3] Assign Outputs
    # All outputs in mm
    setattr(vehicle.dimensions.EX, 'cooling_system_crossmember', dist_crossmember_cooling_system)

    # The point, where the cooling system can start! We have to add the thickness of the cooling system (which we do not have)
    cooling_system_front_axle = vehicle.dimensions.EX.crossmember_front_axle - dist_crossmember_cooling_system
    setattr(vehicle.dimensions.EX, 'cooling_system_front_axle', cooling_system_front_axle)
    # endregion

    return vehicle
