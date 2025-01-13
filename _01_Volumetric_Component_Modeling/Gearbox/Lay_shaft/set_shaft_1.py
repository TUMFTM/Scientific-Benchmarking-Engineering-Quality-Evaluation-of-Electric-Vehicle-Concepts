"""
Description:    This function dimensions the first shaft of the lay-shaft gearbox
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Master Thesis, TUM, 2020
            (2) Niemann and Winter, "Maschinenelemente - Band 2: Getriebe allgemein, Zahnradgetriebe", Springer Verlag, 2003, ISBN: 978-3-662-11874-0
            (3) Schaeffler, "Waelzlager", Bearing Catalogue, 2019
            (4) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  Dimensioning of all elements on the first shaft (gears, shaft, bearings)
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of shaft 1 data
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import numpy as np
# Import classes
# Import methods
from .calc_wheel_data import calc_wheel_data
from .set_bearings_shaft_1 import set_bearings_shaft_1
from .calc_factors import calc_factors
from .calc_S_F import calc_S_F
from .calc_S_H import calc_S_H
# endregion


def set_shaft_1(gearbox, parameters):
    # region [1]: Initialization of required values
    # Parameters
    b_d_1 = parameters.gearbox.GearingConst.b_d_1       # Ratio of width to pitch diameter of first wheel[-]
    S_H_min = parameters.gearbox.MinSafety.S_H_min      # Minimum safety factor against flank break (Niemann and Winter, p. 344)[-]
    S_F_min = parameters.gearbox.MinSafety.S_F_min      # Minimum safety factor against root break  (Niemann and Winter, p. 344)[-]

    # Loading and sorting of the bearing catalogue
    dgb = parameters.gearbox.BearCtlg.ball      # Loading of Schaeffler ball bearing catalogue(starting on p. 246)
    # Filter out bearings with insufficient inner diameter for coaxial design
    if gearbox.Input.axles.lower() == 'coaxial':
        dgb = dgb.drop(dgb[dgb.d < (gearbox.shafts.d_sh_3 + 4 + 7.5)].index, inplace=False)
        dgb.reset_index(inplace=True)

    length_ctlg = len(dgb)
    d_ctlg = np.array(dgb.d.values).reshape(length_ctlg, 1)             # List of inner bearing diameters[mm]
    d_A_ctlg = np.array(dgb.d_A.values).reshape(length_ctlg, 1)         # List of outer bearing diameters[mm]
    b_ctlg = np.array(dgb.b.values).reshape(length_ctlg, 1)             # List of bearing widths[mm]
    C_dyn_ctlg = np.array(dgb.C_dyn.values).reshape(length_ctlg, 1)     # List of dynamic load ratings[N]
    m_ctlg = np.array(dgb.m.values).reshape(length_ctlg, 1)             # List of bearing masses[kg]
    f0_ctlg = np.array(dgb.f0.values).reshape(length_ctlg, 1)           # List of bearing factors f0[-]
    C_stat_ctlg = np.array(dgb.C_stat.values).reshape(length_ctlg, 1)   # List of static load ratings[N]
    d_1_ctlg = np.array(dgb.d_1.values).reshape(length_ctlg, 1)         # List of diameters of inner bearing ring[mm]
    name_ctlg = dgb.Name                                                # List of bearing codes (not possible as np.array)

    # Constants
    shaft = 1                   # Switch for sub - functions
    iteration = 0               # Initialization of iteration counter
    # endregion

    # region [2]: Calculation of shaft 1 data
    while True:
        # Calculation of actual number of teeth and corresponding wheel dimensions
        gearbox = calc_wheel_data(gearbox, parameters, shaft)

        # Bearing hollow shaft calculation for shaft 1 according to input load and desired lifetime
        gearbox = set_bearings_shaft_1(gearbox, parameters, shaft, d_ctlg, d_A_ctlg, b_ctlg, C_dyn_ctlg, m_ctlg, f0_ctlg,
                                       C_stat_ctlg, d_1_ctlg, name_ctlg)

        # Determination of calculation factors needed for safety coefficients
        gearbox = calc_factors(gearbox, parameters, shaft)

        # Calculation of safety factors for critical pinion on shaft 1
        gearbox = calc_S_F(gearbox, parameters, shaft)
        gearbox = calc_S_H(gearbox, parameters, shaft)

        # Verification of safety factors, increase of gear width and diameter according to b/d-ratio
        if gearbox.results.S_H_12 < S_H_min or gearbox.results.S_F_12 < S_F_min:
            setattr(gearbox.gears_12, 'd_1', gearbox.gears_12.d_1+0.25/b_d_1)
            iteration = iteration+1

        # Iterative decrease of normal module if safety factors are sufficient
        cond_2 = True
        if gearbox.results.S_H_12 > (S_H_min+0.2) and gearbox.results.S_F_12 > (S_F_min+0.2) and gearbox.gears_12.m_n_1 > parameters.gearbox.GearingConst.m_n_1_min:
            setattr(gearbox.gears_12, 'm_n_1', gearbox.gears_12.m_n_1-0.1)
            cond_2 = False

        if gearbox.results.S_H_12 >= S_H_min and gearbox.results.S_F_12 >= S_F_min:
            cond_1 = True
        elif iteration > 150:
            cond_1 = True
        else:
            cond_1 = False

        # End condition for the calculation loop
        if cond_1 is True and cond_2 is True:
            break

    # Selection of maximum diameter of shaft 1 for outer gearbox dimensions
    d_1_arr = np.array([gearbox.gears_12.d_a1, gearbox.bearings_1.d_A_A, gearbox.bearings_1.d_A_B])
    d_1_max = max(d_1_arr)
    # endregion

    # region [3]: Output assignment
    setattr(gearbox.shafts, 'd_1_max', d_1_max)               # Maximum diameter of shaft 1 in mm

    setattr(gearbox.factors, 'it_sh_1', iteration)            # Number of iterations of shaft 1
    # endregion

    return gearbox
