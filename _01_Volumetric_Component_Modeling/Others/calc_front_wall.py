"""
Description:  This function calculates the position and dimensions of the front wall.
              For the estimation the BOF and the BOF at the deceleration point are taken as reference.
------------
Sources: (1) Andreas Krohn, Master Thesis, “Designing Geometric Substitute Models for Automated Concept Development“, Technical University of Munich, Institute of Automotive Technology, 2018
         (2) Tim Schröder, Term Thesis, “Entwicklung geometrischer Ersatzmodelle für Komponenten des Vorderwagens“, Technical University of Munich, Institute of Automotive Technology, 2018
         (3) E. Elagamy, „Creation of a Parametric Model for the Derivation of the Conceptual Dimensions for Battery Electric Vehicles,“ Master thesis, Institute for Automotive Engineering, RWTH Aachen University, Aachen, 2020.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The vehicle structure updated with the position and dimensions of the front wall
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Calculate the position of the front wall
[3] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
import numpy as np
# endregion


def calc_front_wall(vehicle):
    # region [1] Assign Inputs
    EX_BOF_decelerator = 30                                     # in mm, see (2)
    EX_front_wall_decelerator = 256.68                          # in mm, see (2)
    CX_front_wall = 2                                           # in mm, see (1)
    BOF_X = vehicle.manikin.BOF_X_front_axle                    # in mm, distance between front axle and BOF
    AHP_Z = vehicle.manikin.AHP_Z_front_axle                    # in mm, distance between ground and AHP
    manwidth = vehicle.manikin.elbow2elbow_ANSURII              # Distance between the two elbow in Y according to the ANSURII analysis see (3)
    CX_wheelhouse = vehicle.wheels.wheelhouse_f[0, :]           # Point of the front wheelhouse in the X direction
    CY_wheelhouse = vehicle.wheels.wheelhouse_f[1, :]           # Point of the front wheelhouse in the Y direction
    CX_frameform = vehicle.exterior.frameform_middle_sec[:, 0]  # Point of the frameform in X direction
    CZ_frameform = vehicle.exterior.frameform_middle_sec[:, 2]  # Point of the frameform in Z direction
    # endregion

    # region [2] Calculate the position of the front wall
    # Distance in X between BOF and decelerator (see (2) from page 85) in mm
    EX_front_wall_BOF = EX_front_wall_decelerator - EX_BOF_decelerator

    # Distance in X between front axle and front wall (see (1) from page 85) in mm
    EX_front_wall_front_axle = BOF_X - EX_front_wall_BOF - CX_front_wall

    # Calculate the width of the front wall depending on its X-position in mm
    if EX_front_wall_front_axle < max(CX_wheelhouse):   # The front wall is comprised between the wheelhouses

        # Retrieve the wheelhouse width at the X-position of the front wall
        idx = np.argmin(abs(CX_wheelhouse - EX_front_wall_front_axle))
        CY_front_wall = CY_wheelhouse[idx] * 2

    else:   # The front wall is placed behind the wheelhouses

        # Calculate front wall width: Simplified as the distance between the drivers and front passenger's outer elbows
        CY_front_wall = vehicle.manikin.W20_1 * 2 + manwidth

    # Calculate the front height of the front wall in mm
    idx = np.argmin(abs(CX_frameform - EX_front_wall_front_axle))   # Find the height of the frameform at the X position of the front wall
    CZ_front_wall = CZ_frameform[idx] - AHP_Z
    # endregion

    # region [3] Assign Outputs
    # Assign resulting dimensions and position of the front wall (all in mm)
    setattr(vehicle.dimensions.EX, 'front_wall_front_axle', EX_front_wall_front_axle)
    setattr(vehicle.dimensions.EZ, 'front_wall_front_axle', AHP_Z)
    setattr(vehicle.dimensions.CX, 'front_wall', CX_front_wall)
    setattr(vehicle.dimensions.CY, 'front_wall', CY_front_wall)
    setattr(vehicle.dimensions.CZ, 'front_wall', CZ_front_wall)
    # endregion

    return vehicle
