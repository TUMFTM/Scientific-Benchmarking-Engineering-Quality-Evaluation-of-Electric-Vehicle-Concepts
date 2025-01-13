"""
Description:    This function computes the inner diameter of the hollow shaft
                and ensures sufficient torsional strength according to Stahl.
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
            (2) K. Stahl, Documentation Lecture "Maschinenelemente", TUM, 2015/2016
            (3) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
------------
Input:   gearbox: The class where all results of the gearbox calculation are saved
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


def calc_d_sh(gearbox, parameters, shaft, d_ctlg):
    # region [1]: Initialization of required values
    # Gearbox Values
    T_max = gearbox.Input.T_max                         # Maximum torque of el. motor [Nm]
    i_12 = gearbox.results.i_12                         # Transmission ratio of first stage [-]

    # Parameters
    R_mn = parameters.gearbox.MatProp.R_mn  # Yield strength 16MnCr5 (Stahl, p. 135) [N/mm^2]
    S_Dt_min = parameters.gearbox.MinSafety.S_Dt_min    # Minimum safety factor against torsional fatigue fracture (Stahl, p. 33) [-]

    if shaft == 1:
        T_rel = T_max*1000                     # Maximum torque of shaft 1 [Nmm]
        d_f1 = gearbox.gears_12.d_f1           # Root diameter of wheel 1 [mm]
        m_n = gearbox.gears_12.m_n_1           # Normal module of stage 1 [mm]
    else:
        T_rel = T_max*1000*i_12                # Maximum torque of shaft 2 [Nmm]
        d_f1 = gearbox.gears_34.d_f3           # Root diameter of wheel 3 [mm]
        m_n = gearbox.gears_34.m_n_3           # Normal module of stage 2 [mm]

    m = len(d_ctlg)
    # endregion

    # region [2]: Calculation of inner diameter of hollow shaft
    # Selection of minimum shaft diameter in mm (either wheel 1 or bearing)
    d_sh_rel = np.concatenate((d_ctlg, d_f1*np.ones((m, 1))), axis=1)
    d_sh_min = np.amin(d_sh_rel, axis=1).reshape(m, 1)
    # Resistance to alternating stress for standard dimensions in N/mm^2 (Stahl, p. 19)
    tau_wsn = 0.58*0.4*R_mn                    # Factors (Stahl: Table 12, p. 20)
    # Technological size factor K_dm according to Stahl, p. 10
    K_dm = (1-(0.7686*0.5*np.log10(d_sh_min/7.5)))/(1-(0.7686*0.5*np.log10(11/7.5)))
    # Resistance to alternating stress in part in N/mm^2 (Stahl, p. 20)
    tau_ws = tau_wsn*K_dm
    # Neglect of notches for approximation (Zaehringer, p. 37)
    tau_ak = tau_ws

    # Initialization of array with possible inner shaft diameters in mm for coaxial and parallel axles
    # with empirical boundaries for shaft thickness and minimum bore diameter
    if shaft == 1 and gearbox.Input.axles.lower() == 'coaxial':
        d_sh_3 = gearbox.shafts.d_sh_3
        # Minimum inner shaft diameter is either determined by wheel 1 or
        # bearing with smaller inner diameter
        if d_f1-6*m_n > d_sh_3+4:
            d_inn_u = np.zeros((d_sh_min.shape[0], 10))
            d_inn_min = (d_sh_min == d_f1) * (d_f1-6*m_n)+(d_sh_min != d_f1) * (d_sh_min-7)
            for i in range(0, d_sh_min.shape[0]):
                d_inn_u[i, :] = np.linspace(d_inn_min[i], (d_sh_3 + 4), 10).reshape(1, 10)
        else:
            # If minimum shaft diameter is wheel 1, minimum inner shaft
            # diameter is determined by coaxial output shafts
            d_inn_u = d_sh_3+4

    else:
        # Creation of array with possible inner diameters for each bearing diameter d_sh
        space = np.expand_dims(np.linspace(1, 7.5/(d_f1-6*m_n), 9), axis=0)
        # Minimum inner shaft diameter is either determined by wheel 1 or
        # smaller inner bearing diameter
        d_inn_u = np.matmul((d_sh_min == d_f1)*(d_f1-6*m_n), space)+np.matmul((d_sh_min != d_f1) * (d_sh_min-7), space)
        # Addition of column with zeros for shafts without hollow bores
        d_inn_u = np.concatenate((d_inn_u, np.zeros((m, 1))), axis=1)

    d_sh_min = np.tile(d_sh_min, (1, 10))
    # Torsional resistance of a ring surface area in mm^3 (Stahl, p. 137)
    wt = math.pi*(np.power(d_sh_min, 4)-np.power(d_inn_u, 4))/(16*d_sh_min)
    # Occurring torsional stress in N/mm^2 (Stahl, p. 8)
    tau_occ = T_rel/wt
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
    d_inn = np.max(d_inn, axis=1).reshape(m, 1)
    S_dt = np.nanmin(S_dt, axis=1).reshape(m, 1)
    sh_mat = np.concatenate((d_ctlg, S_dt, d_inn), axis=1)
    # endregion

    # region [3]: Output Assignment
    if shaft == 1:
        setattr(gearbox.shafts, 'shaft_1', sh_mat)        # Matrix of possible first shaft configurations
    elif shaft == 2:
        setattr(gearbox.shafts, 'shaft_2', sh_mat)        # Matrix of possible second shaft configurations
    # endregion

    return gearbox
