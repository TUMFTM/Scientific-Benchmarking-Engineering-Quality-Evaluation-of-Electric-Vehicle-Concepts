"""
Description:    This function dimensions the second shaft of the lay-shaft gearbox
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Master Thesis, TUM, 2020
            (2) Niemann and Winter, "Maschinenelemente - Band 2: Getriebe allgemein, Zahnradgetriebe", Springer Verlag, 2003, ISBN: 978-3-662-11874-0
            (3) Schaeffler, "Waelzlager", Bearing Catalogue, 2019
            (4) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  Dimensioning of all elements on the second shaft (gears, shaft, bearings)
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Verification of space for differential cage
[3] Calculation of shaft 2 data
[4] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import numpy as np
import math
# Import classes
# Import methods
from .calc_wheel_data import calc_wheel_data
from .set_bearings_shaft_2 import set_bearings_shaft_2
from .calc_factors import calc_factors
from .calc_S_F import calc_S_F
from .calc_S_H import calc_S_H
# endregion


def set_shaft_2(gearbox, parameters):
    # region [1]: Initialization of required values
    # Gearbox Values
    T_max = gearbox.Input.T_max                # Maximum torque of el. motor [Nm]

    i_12 = gearbox.results.i_12                # Transmission ratio of first stage [-]
    i_34 = gearbox.results.i_34                # Transmission ratio of second stage [-]
    a_23 = gearbox.results.a_23                # Distance between shafts 2&3 [mm]

    d_a2 = gearbox.gears_12.d_a2               # Outer diameter of wheel 2 [mm]

    # Parameters
    b_d_3 = parameters.gearbox.GearingConst.b_d_3  # Ratio of width to pitch diameter of first wheel [-]
    d_bevel = parameters.gearbox.GearingConst.d_bevel  # Empirical ratio between smaller and larger bevel gears of the diffferential ([4], pp. 46) [-]
    S_H_min = parameters.gearbox.MinSafety.S_H_min  # Minimum safety factor against flank break (Niemann and Winter, p. 344) [-]
    S_F_min = parameters.gearbox.MinSafety.S_F_min  # Minimum safety factor against root break (Niemann and Winter, p. 344) [-]
    t_diffcage = parameters.gearbox.ConstDim.t_diffcage  # Thickness of differential housing [mm]
    regr_d_bevel = parameters.regr.gearbox.d_bevel  # Regression formula for the diameter of the larger differential gears in mm ([1], p. 46)

    # Loading of the bearing catalogue
    dgb = parameters.gearbox.BearCtlg.ball     # Loading of Schaeffler ball bearing catalogue (starting on p. 246)
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
    shaft = 2                                 # Switch for sub-functions
    iteration = 0                              # Initialization of iteration counter
    # endregion

    # region [2]: Verification of space for differential cage
    if gearbox.Input.num_EM == 1:
        # Calculate dimensions of the differential gears and the differential cage ([4], pp. 46)
        d_bev_l = regr_d_bevel.coefficients[0] + regr_d_bevel.coefficients[1]*(T_max*i_12*i_34)                    # Empirical diameter of larger bevel gears in mm
        d_bev_s = d_bevel*d_bev_l                                  # Empirical diameter of smaller bevel gears in mm
        d_diffcage = d_bev_l+(math.sqrt(2)-1)*d_bev_s+2*t_diffcage      # Diameter of differential cage in mm

        # Check differential orientation ([1], pp. 51)
        if gearbox.Input.axles.lower() == 'parallel':
            # % Check if there is a given differential orientation
            if hasattr(gearbox.differential, 'diff_orientation'):
                # Check if the differential cage and wheel 2 fit within the second stage axle distance
                if gearbox.differential.diff_orientation == 'in' and (d_diffcage / 2 + d_a2 / 2 + 5) < a_23:
                    # Axle distance of second stage is increased to fit differential orientation
                    a_23 = d_diffcage / 2 + d_a2 / 2 + 5
                    # Update of pitch diameters of the second stage with new axle distance
                    d_3 = (2 * a_23) / (1 + i_34)
                    d_4 = i_34 * d_3
                    # Storing of updated pitch diameters and distance between shafts
                    setattr(gearbox.results, 'a_23', a_23)
                    setattr(gearbox.gears_34, 'd_3', d_3)
                    setattr(gearbox.gears_34, 'd_4', d_4)
                else:  # An 'in' position was chosen but the differential does not fit // the chosen option is 'out' -> set 'out'
                    setattr(gearbox.differential, 'diff_orientation', 'out')
            else:
                # Increase of stage 2 wheel diameters if differential does not fit (applies only for parallel axles)
                if (d_diffcage / 2 + d_a2 / 2 + 5) <= a_23:
                    setattr(gearbox.differential, 'diff_orientation', 'in')
                else:
                    setattr(gearbox.differential, 'diff_orientation', 'out')
        else:
            setattr(gearbox.differential, 'diff_orientation', 0)
    # endregion

    # region [3]: Calculation of shaft 2 data
    while True:
        # Calculation of actual number of teeth and corresponding wheel dimensions
        gearbox = calc_wheel_data(gearbox, parameters, shaft)

        # Bearing hollow shaft calculation for shaft 2 according to input load and desired lifetime
        gearbox = set_bearings_shaft_2(gearbox, parameters, shaft, d_ctlg, d_A_ctlg, b_ctlg, C_dyn_ctlg, m_ctlg,
                                       f0_ctlg, C_stat_ctlg, d_1_ctlg, name_ctlg)

        # Determination of calculation factors needed for safety coefficients
        gearbox = calc_factors(gearbox, parameters, shaft)

        # Calculation of safety factors for critical pinion on shaft 2
        gearbox = calc_S_F(gearbox, parameters, shaft)
        gearbox = calc_S_H(gearbox, parameters, shaft)

        # Verification of safety factors, increase of gear width and diameter according to b/d-ratio
        if gearbox.results.S_H_34 < S_H_min or gearbox.results.S_F_34 < S_F_min:
            # gearbox.gears_34.b_3 = gearbox.gears_34.b_3+0.25;
            if gearbox.Input.axles.lower() != 'coaxial':
                gearbox.gears_34.d_3 = gearbox.gears_34.d_3+0.25/b_d_3
            iteration = iteration+1

        # Iterative decrease of normal module if safety factors are sufficient
        cond_2 = True
        if gearbox.results.S_H_34 > (S_H_min+0.2) and gearbox.results.S_F_34 > (S_F_min+0.2) and gearbox.gears_34.m_n_3 > parameters.gearbox.GearingConst.m_n_3_min:
            gearbox.gears_34.m_n_3 = gearbox.gears_34.m_n_3-0.2
            cond_2 = False

        # Condition for end of loop: safety factors and overlap ratio sufficient or iterations>150
        if gearbox.results.S_H_34 <= 5 or gearbox.results.S_F_34 <= 5 or iteration > 100:
            if gearbox.results.S_H_34 >= S_H_min and gearbox.results.S_F_34 >= S_F_min:
                cond_1 = True
            elif iteration > 150:
                cond_1 = True
            else:
                cond_1 = False
        else:
            cond_1 = False

        # End condition for the calculation loop
        if cond_1 is True and cond_2 is True:
            break
    # endregion

    # region [4]: Output assignment
    if gearbox.Input.num_EM == 1:
        # noinspection PyUnboundLocalVariable
        setattr(gearbox.differential, 'd_bev_l', d_bev_l)           # Diameter of larger differential bevel gears in mm
        # noinspection PyUnboundLocalVariable
        setattr(gearbox.differential, 'd_bev_s', d_bev_s)           # Diameter of smaller differential bevel gears in mm
        # noinspection PyUnboundLocalVariable
        setattr(gearbox.differential, 'd_diffcage', d_diffcage)     # Diameter of differential cage in mm
    setattr(gearbox.factors, 'it_sh_2', iteration)                  # Number of iterations of shaft 2
    # endregion

    return gearbox
