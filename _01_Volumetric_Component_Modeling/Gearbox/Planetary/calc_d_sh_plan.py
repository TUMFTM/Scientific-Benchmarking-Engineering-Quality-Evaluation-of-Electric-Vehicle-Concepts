"""
Description:    This function computes initial gear dimensions for the given transmission
                ratio according to the diameter of the output shaft.
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Master Thesis, TUM, 2020
            (2) K. Stahl, Documentation Lecture "Maschinenelemente", TUM, 2015/2016
            (3) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
         shaft: denotes which reduction stage is being considered (1 or 2; for the differential shaft a different calculation is used)
         d_ctlg: List of inner bearing diameters [mm]
------------
Output:  Minimum shaft diameter
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of inner diameter of hollow shaft
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
import numpy as np
# Import classes
# Import methods
# endregion


def calc_d_sh_plan(gearbox, parameters, shaft, d_ctlg):
    # region [1]: Initialization of required values
    # Parameters
    R_mn = parameters.gearbox.MatProp.R_mn              # Yield strength 16MnCr5 (Stahl, p. 135) [N/mm^2]
    S_Dt_min = parameters.gearbox.MinSafety.S_Dt_min    # Minimum safety factor against torsional fatigue fracture (Stahl, p. 33) [-]

    # Gearbox Values
    T_max = gearbox.Input.T_max * 1000                  # Maximum torque of el.motor[Nmm]
    if shaft == 1:
        d_f1 = gearbox.gears_12.d_f1                    # Root diameter of wheel 1 [mm]
        m_n = gearbox.gears_12.m_n_1                    # Normal module of stage 1 [mm]

        d_sh_3 = gearbox.shafts.d_sh_3                  # Outer diameter of output shafts [mm]
    else:  # if shaft == 2
        i_1p1 = gearbox.results.i_1p1
        T_max = 1/3*T_max*i_1p1                         # Maximum torque on planet [Nmm]

        d_f1 = gearbox.gears_12.d_fp2                   # Root diameter of planet [mm]
        m_n = gearbox.gears_12.m_n_2                    # Normal module of stage 2 [mm]

    m = len(d_ctlg)
    # endregion

    # region [2]: Calculation of inner diameter of hollow shaft
    # Selection of critical shaft diameter in mm
    if shaft == 1:
        d_sh_min = np.tile(d_f1, (m, 1))
    else:
        d_sh_rel = np.concatenate((d_ctlg, np.tile(d_f1, (m, 1))), axis=1)
        d_sh_min = np.nanmin(d_sh_rel, axis=1, keepdims=True)

    # Resistance to alternating stress for standard dimensions in N/mm^2 (Stahl, p. 19)
    tau_wsn = 0.58*0.4*R_mn                    # Factors (Stahl, Table 12, p. 20)
    # Technological size factor K_dm (Stahl, p. 10)
    K_dm = (1-(0.7686*0.5*np.log10(d_sh_min/7.5)))/(1-(0.7686*0.5*np.log10(11/7.5)))
    # Resistance to alternating stress in part in N/mm^2 (Stahl, p. 20)
    tau_ws = tau_wsn*K_dm
    # Neglect of notches for approximation (Zaehringer, p. 37)
    tau_ak = tau_ws

    # Initialization of array with possible inner shaft diameters in mm for coaxial and parallel axles
    # with empirical boundaries for shaft thickness and minimum bore diameter.
    if shaft == 1:
        # Minimum inner shaft diameter is determined by wheel 1
        # noinspection PyUnboundLocalVariable
        if (d_f1-6*m_n) > (d_sh_3+4):
            space = np.linspace(1, (d_sh_3+4)/(d_f1-6*m_n), 10).reshape(1, 10)
            d_inn_u = np.matmul((d_sh_min == d_f1), (d_f1-6*m_n)*space) + np.matmul((d_sh_min != d_f1), space)
        else:
            # If minimum shaft diameter is wheel 1, minimum inner shaft
            # diameter is determined by coaxial output shafts
            d_inn_u = d_sh_3+4
    else:
        # Creation of array with possible inner diameters for each bearing diameter d_sh
        space = np.linspace(1, 7.5/(d_f1-6*m_n), 9).reshape(1, 9)
        # Minimum inner shaft diameter is either determined by wheel 1 or smaller inner bearing diameter
        d_inn_u = np.matmul((d_sh_min == d_f1), (d_f1-6*m_n) * space) + np.matmul((d_sh_min != d_f1) * (d_sh_min-7), space)
        # Addition of column with zeros for shafts without hollow bores
        d_inn_u = np.concatenate((d_inn_u, np.zeros((m, 1))), axis=1)

    # Torsional resistance of a ring surface area in mm^3 (Stahl, p. 137)
    wt = math.pi*(np.power(d_sh_min, 4)-np.power(d_inn_u, 4))/(16*d_sh_min)
    # Occurring torsional stress in N/mm^2 (Stahl, p. 8)
    tau_occ = T_max/wt
    # Safety factor against torsional fatigue (Stahl, p. 33)
    S_dt = tau_ak/tau_occ

    # Selection of inner shaft diameter with minimum shaft thickness that fits
    # safety criterion of S_dt>2 (Zaehringer, p. 38)
    S_dt[S_dt < S_Dt_min] = np.nan

    # If no value fulfills safety criterion, the outer diameter has to increase --> parameter int stays 0
    if np.isnan(S_dt).all():
        setattr(gearbox.error, 'shaft', 'Shaft does not support torsional load')
        raise ValueError('Error! Shaft does not support torsional load')

    d_inn = (S_dt >= S_Dt_min) * d_inn_u
    d_inn = np.max(d_inn, axis=1, keepdims=True)
    S_dt = np.nanmin(S_dt, axis=1, keepdims=True)
    sh_mat = np.concatenate((d_ctlg, S_dt, d_inn), axis=1)
    # endregion

    # region [3]: Output assignment
    if shaft == 1:
        setattr(gearbox.shafts, 'shaft_1', sh_mat)        # Matrix of possible sun shaft configurations
    elif shaft == 2:
        setattr(gearbox.shafts, 'shaft_p', sh_mat)        # Matrix of possible planet shaft configurations
    # endregion

    return gearbox
