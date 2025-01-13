"""
Description:    This function computes the planet shaft of the planetary gearbox
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Master Thesis, TUM, 2020
            (2) Niemann and Winter, "Maschinenelemente - Band 2: Getriebe allgemein, Zahnradgetriebe", Springer Verlag, 2003, ISBN: 978-3-662-11874-0
            (3) Schaeffler, "Waelzlager", Bearing Catalogue, 2019
            (4) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  Dimensioning of all elements on the planets (gears, shaft, bearings)
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of planet data
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import numpy as np
# Import classes
# Import methods
from .set_bearings_planet import set_bearings_planet
from .calc_factors_plan import calc_factors_plan
from .calc_S_F_plan import calc_S_F_plan
from .calc_S_H_plan import calc_S_H_plan
# endregion


def set_planets(gearbox, parameters):
    # region [1]: Initialization of required values
    # Parameters
    S_H_min = parameters. gearbox.MinSafety.S_H_min     # Minimum safety factor against flank break (Niemann and Winter, p. 344) [-]
    S_F_min = parameters.gearbox.MinSafety.S_F_min      # Minimum safety factor against root break (Niemann and Winter, p. 344) [-]

    # Loading of the bearing catalogue
    tr = parameters.gearbox.BearCtlg.roller                             # Loading of Schaeffler taper roller bearing catalogue (starting on p. 590)
    length_ctlg = len(tr)
    d_ctlg = np.array(tr.d.values).reshape(length_ctlg, 1)               # List of inner bearing diameters [mm]
    d_A_ctlg = np.array(tr.d_A.values).reshape(length_ctlg, 1)           # List of outer bearing diameters [mm]
    b_ctlg = np.array(tr.b.values).reshape(length_ctlg, 1)               # List of bearing widths [mm]
    C_dyn_ctlg = np.array(tr.C_dyn.values).reshape(length_ctlg, 1)       # List of dynamic load ratings [N]
    m_ctlg = np.array(tr.m.values).reshape(length_ctlg, 1)               # List of bearing masses [kg]
    a_ctlg = np.array(tr.a.values).reshape(length_ctlg, 1)               # List of bearing distances [mm]
    e_ctlg = np.array(tr.e.values).reshape(length_ctlg, 1)               # List of bearing factors e [-]
    Y_ctlg = np.array(tr.Y.values).reshape(length_ctlg, 1)               # List of bearing factors Y [-]
    d_1_ctlg = np.array(tr.d_1.values).reshape(length_ctlg, 1)           # List of diameters of inner bearing ring [mm]
    C_stat_ctlg = np.array(tr.C_stat.values).reshape(length_ctlg, 1)     # List of static load ratings [N]
    Y_0_ctlg = np.array(tr.Y_0.values).reshape(length_ctlg, 1)           # List of bearing factors Y_0 [-]
    name_ctlg = np.array(tr.Name.values).reshape(length_ctlg, 1)         # List of bearing codes

    # Constants
    shaft = 2                              # Switch for sub-functions
    iteration = 0                          # Initialization of iteration counter
    # endregion

    # region [2]: Calculation of planet data
    while True:
        # Bearing hollow shaft calculation for shaft 2 according to input load and desired lifetime
        gearbox = set_bearings_planet(gearbox, parameters, shaft, d_ctlg, d_A_ctlg, b_ctlg, C_dyn_ctlg, m_ctlg, a_ctlg, e_ctlg, Y_ctlg, C_stat_ctlg, Y_0_ctlg, d_1_ctlg, name_ctlg)

        # Determination of calculation factors needed for safety coefficients
        gearbox = calc_factors_plan(gearbox, parameters, shaft)

        # Calculation of safety factors for critical pinion on shaft 2
        gearbox = calc_S_F_plan(gearbox, parameters, shaft)
        gearbox = calc_S_H_plan(gearbox, parameters, shaft)

        # Verification of safety factors, increase of gear width
        if gearbox.results.S_H_p22 < S_H_min or gearbox.results.S_F_p22 < S_F_min:
            setattr(gearbox.gears_12, 'b_2', gearbox.gears_12.b_2+1)
            iteration = iteration+1

        # Condition for end of loop: safety factors and overlap ratio okay, or iterations>150
        if gearbox.results.S_H_p22 >= S_H_min and gearbox.results.S_F_p22 >= S_F_min:
            cond_1 = True
        elif iteration > 150:
            cond_1 = True
        else:
            cond_1 = False

        # End condition for the calculation loop
        if cond_1:
            break
    # endregion

    # region [3]: Output Assignment
    setattr(gearbox.factors, 'it_sh_2',  iteration)            # Number of iterations of shaft 2
    # endregion

    return gearbox
