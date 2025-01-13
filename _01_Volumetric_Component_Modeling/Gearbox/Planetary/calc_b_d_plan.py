"""
Description:    This function computes initial gear dimensions for the given transmission
                ratio according to the diameter of the output shaft.
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Master Thesis, TUM, 2020
            (2) Decker and Kabus, "Maschinenelemente - Formeln", Carl Hanser Verlag, 2011, ISBN: 978-3-446-42990-1
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  First rough dimensioning of the gearbox gears
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of initial wheel widths
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
# Import classes
# Import methods
# endregion


def calc_b_d_plan(gearbox, parameters):
    # region [1]: Initialization of required values
    # Parameters
    epsilon_beta = parameters.gearbox.GearingConst.epsilon_beta
    # endregion

    # region [2]: Calculation of initial gear widths
    # Approximation of first stage gear width with helix angle (30 deg) and
    # minimum normal module (1.3) in mm (Decker, p. 136)
    b_1 = epsilon_beta*1.3*math.pi/math.sin(math.pi/6)
    # Approximation of second stage gear width according to empirical
    # stage-width-ratio in mm (Koehler, p. 51)
    b_2 = 1.6*b_1
    # endregion

    # region [3]: Output Assignment
    setattr(gearbox.gears_12, 'b_1', b_1)        # Width of first stage gears in mm
    setattr(gearbox.gears_12, 'b_2', b_2)        # Width diameter of second stage gears in mm
    # endregion

    return gearbox
