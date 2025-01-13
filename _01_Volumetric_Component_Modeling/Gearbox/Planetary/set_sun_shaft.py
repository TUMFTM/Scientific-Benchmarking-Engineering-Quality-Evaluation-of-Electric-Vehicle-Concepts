"""
Description:    This function dimensions the sun shaft of the planetary gearbox
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Master Thesis, TUM, 2020
            (2) Niemann and Winter, "Maschinenelemente - Band 2: Getriebe allgemein, Zahnradgetriebe", Springer Verlag, 2003, ISBN: 978-3-662-11874-0
            (3) Schaeffler, "Waelzlager", Bearing Catalogue, 2019
            (4) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  Dimensioning of all elements on the sun shaft (gears, shaft, bearings)
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of sun shaft data
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import numpy as np
# Import classes
# Import methods
from .calc_wheel_data_plan import calc_wheel_data_plan
from .set_bearings_sun import set_bearings_sun
from .calc_factors_plan import calc_factors_plan
from .calc_S_F_plan import calc_S_F_plan
from .calc_S_H_plan import calc_S_H_plan
# endregion


def set_sun_shaft(gearbox, parameters):
    # region [1]: Initialization of required values
    # Parameters
    S_H_min = parameters.gearbox.MinSafety.S_H_min  # Minimum safety factor against flank break (Niemann and Winter, p. 344) [-]
    S_F_min = parameters.gearbox.MinSafety.S_F_min  # Minimum safety factor against root break (Niemann and Winter, p. 344) [-]
    m_n_plan_min = 1.3                              # Minimum normal module of planetary gears from BEV gearbox database (Koehler [1]) [mm]

    # Loading of the bearing catalogue
    ab = parameters.gearbox.BearCtlg.ang_ball                  # Loading of Schaeffler angular ball bearing catalogue (starting on p. 272)

    # Filter out bearings with insufficient inner diameter for coaxial design
    ab = ab.drop(ab[ab.d < (gearbox.shafts.d_sh_3+4+7.5)].index, inplace=False)
    ab.reset_index(inplace=True)

    length_ctlg = len(ab)
    d_ctlg = np.array(ab.d.values).reshape(length_ctlg, 1)               # List of inner bearing diameters [mm]
    d_A_ctlg = np.array(ab.d_A.values).reshape(length_ctlg, 1)           # List of outer bearing diameters [mm]
    b_ctlg = np.array(ab.b.values).reshape(length_ctlg, 1)               # List of bearing widths [mm]
    a_ctlg = np.array(ab.a.values).reshape(length_ctlg, 1)               # List of bearing point distances [mm]
    C_dyn_ctlg = np.array(ab.C_dyn.values).reshape(length_ctlg, 1)       # List of dynamic load ratings [N]
    m_ctlg = np.array(ab.m.values).reshape(length_ctlg, 1)               # List of bearing masses [kg]
    C_stat_ctlg = np.array(ab.C_stat.values).reshape(length_ctlg, 1)     # List of static load ratings [N]
    d_1_ctlg = np.array(ab.d_1.values).reshape(length_ctlg, 1)           # List of diameters of inner bearing ring [mm]
    name_ctlg = ab.Name                                                  # List of bearing codes

    # Constants
    shaft = 1                                                           # Switch for sub-functions
    iteration = 0                                                       # Initialization of iteration counter
    # endregion

    # region [2]: Calculation of sun shaft data
    while True:
        # Calculation of actual number of teeth and corresponding wheel dimensions
        gearbox = calc_wheel_data_plan(gearbox, parameters)

        # Bearing and hollow shaft calculation for sun shaft according to input load and desired lifetime
        gearbox = set_bearings_sun(gearbox, parameters, shaft, d_ctlg, d_A_ctlg, b_ctlg, a_ctlg, C_dyn_ctlg, m_ctlg, C_stat_ctlg, d_1_ctlg, name_ctlg)

        # Determination of calculation factors needed for safety coefficients
        gearbox = calc_factors_plan(gearbox, parameters, shaft)

        # Calculation of safety factors for critical pinion on sun gear
        gearbox = calc_S_F_plan(gearbox, parameters, shaft)
        gearbox = calc_S_H_plan(gearbox, parameters, shaft)

        # Verification of safety factors, increase of gear width if not sufficient
        if gearbox.results.S_H_1p1 < S_H_min or gearbox.results.S_F_1p1 < S_F_min:
            b_1_new = gearbox.gears_12.b_1 + 0.2
            setattr(gearbox.gears_12, 'b_1', b_1_new)
            iteration = iteration+1

        # Iterative decrease of normal module if safety factors are sufficient and overlap ratio is <2 until minimum module
        cond_2 = True
        if gearbox.results.S_H_1p1 > (S_H_min+0.1) and gearbox.results.S_F_1p1 > (S_F_min+0.1) and gearbox.gears_12.m_n_1 > m_n_plan_min:
            m_n_1_new = gearbox.gears_12.m_n_1 - 0.1
            setattr(gearbox.gears_12, 'm_n_1', m_n_1_new)
            cond_2 = False

        if gearbox.results.S_H_1p1 >= S_H_min and gearbox.results.S_F_1p1 >= S_F_min:
            cond_1 = True
        elif iteration > 150:
            cond_1 = True
        else:
            cond_1 = False

        # End condition for the calculation loop
        if cond_1 is True and cond_2 is True:
            break
    # endregion

    # region [3]: Output assignment
    setattr(gearbox.factors, 'it_sh_1', iteration)            # Number of iterations of sun shaft
    # endregion

    return gearbox
