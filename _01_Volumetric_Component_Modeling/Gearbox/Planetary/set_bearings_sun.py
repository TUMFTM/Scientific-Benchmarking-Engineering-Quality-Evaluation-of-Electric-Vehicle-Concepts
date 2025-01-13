"""
Description:
This function selects ball bearings for the first shaft of
the gearbox from the Schaeffler bearing catalog.
SHAFT 1:
Fixed bearing combination in O arrangement with two angular ball bearings
          _
  B----A-|_|
        |-a|  (bearing distance)

 System of coordinates for calculation of forces:
   y ↑
     |
   z ⦿--> x
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
            (2) K. Stahl, Documentation Lecture "Maschinenelemente", TUM, 2015/2016
            (3) Kirchner, "Leistungsuebertragung in Fahrzeuggetrieben", Springer Verlag, 2007, ISBN: 978-3-540-35288-4
            (4) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
            (5) Schaeffler, "Waelzlager", Bearing Catalogue, 2019
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
         shaft: denotes which shaft is being considered
         d_ctlg: List of inner bearing diameters [mm]
         d_A_ctlg: List of outer bearing diameters [mm]
         b_ctlg: List of bearing widths [mm]
         C_dyn_ctlg: List of dynamic load ratings [N]
         m_ctlg: List of bearing masses [kg]
         f0_ctlg: List of bearing factors f0 [-]
         C_stat_ctlg: List of static load ratings [N]
         d_1_ctlg: List of diameters of inner bearing ring [mm]
         name_ctlg: List of bearing codes
------------
Output:  Dimensions of the bearings on the first shaft (input shaft from the machine)
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of bearing loads and shaft design
[2.1] Calculation of pressure angle and gearing forces
[2.2] Calculation of bearing loads (Stahl, pp. 82)
[2.3] Calculation of shaft
[2.4] Check if all conditions are met for bearing combinations and selection of optimum
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
import numpy as np
# Import classes
# Import methods
from .calc_d_sh_plan import calc_d_sh_plan
# endregion


def set_bearings_sun(gearbox, parameters, shaft, d_ctlg, d_A_ctlg, b_ctlg, a_ctlg, C_dyn_ctlg, m_ctlg, C_stat_ctlg, d_1_ctlg, name_ctlg):
    # region [1]: Initialization of required values
    # Gearbox Values
    T_nom = gearbox.Input.T_nom*1000                    # Nominal torque of el. motor [Nmm]
    overload_factor = gearbox.Input.overload_factor     # Overload factor of el. motor [-]

    m_n_1 = gearbox.gears_12.m_n_1                      # Normal module of first stage [mm]
    alpha_t_1 = gearbox.gears_12.alpha_t_1              # Pressure angle in transverse section [rad]
    beta_1 = gearbox.gears_12.beta_1                    # Helix angle of gearing [rad]
    z_1 = gearbox.gears_12.z_1                          # Number of teeth of sun gear
    z_p1 = gearbox.gears_12.z_p1                        # Number of teeth of planet 1
    d_1 = gearbox.gears_12.d_1                          # Pitch diameter of sun gear [mm]
    b_1 = gearbox.gears_12.b_1                          # Width of first stage gears [mm]
    d_p1 = gearbox.gears_12.d_p1                        # Pitch diameter of planet 1 [mm]

    d_sh_3 = gearbox.shafts.d_sh_3                      # Diameter of output shafts [mm]

    # Parameters
    L_10 = parameters.gearbox.CalcFactors.L_10          # Lifetime factor regarding input speed [10^6 revolutions]
    S_Dt_min = parameters.gearbox.MinSafety.S_Dt_min    # Minimum safety factor against torsional fatigue fracture (Stahl, p. 33) [-]

    # Initialization of bearing matrices for vectorial calculations
    # Variation over the rows means variation of bearing A, variation over the columns varies bearing B
    m = len(d_ctlg)
    # m x m matrices where the static and dynamic load ratings of the bearings are varied over the rows
    C_stat_mat = np.tile(C_stat_ctlg, (1, m))
    C_dyn_mat = np.tile(C_dyn_ctlg, (1, m))
    # endregion

    # region [2]: Calculation of bearing loads and shaft design
    # region [2.1]: Calculation of pressure angle and gearing forces
    # Calculation of the operating pressure angle in rad (Kirchner, p. 189)
    alpha_wt_1 = math.acos((((z_1+z_p1)*m_n_1)/(d_1+d_p1))*(math.cos(alpha_t_1)/math.cos(beta_1)))

    # Calculation of occurring gearing forces in N (Stahl, p. 2)
    F_u_1 = 2*T_nom/d_1                 # Circumferential force on the sun gear
    F_ax_1 = F_u_1*math.tan(beta_1)     # Axial force on the sun gear

    # Minimum diameter of sun shaft in mm
    d_sh_min = d_sh_3+4+10              # output shafts + 2 mm gap + 5 mm shaft thickness

    # Axial force only on bearing A in N, no radial forces (central shaft)
    F_axA = F_ax_1
    # endregion

    # region [2.2]: Calculation of bearing loads (Stahl, pp. 82)
    # region Bearing A
    # Static load ratings for bearing A (Schaeffler, p. 268)
    P_stat_A = 0.26*F_axA*overload_factor      # Equivalent static load rating in N (in relation to T_max)
    C_stat_req_A = 2.1*P_stat_A                # Required static load rating in N, Safety factor according to Stahl, p. 83 and Zaehringer, p. 29

    # Dynamic load ratings for bearing A (Schaeffler, p. 267)
    P_dyn_A = 0.57*F_axA                        # Equivalent dynamic load rating in N (in relation to T_nom)
    C_dyn_req_A = math.pow(L_10, (1/3))*P_dyn_A  # Required equivalent dynamic load rating in N

    # Check for static (cond_A1) and dynamic (cond_A2) load for bearing A
    cond_A1 = (C_stat_mat >= C_stat_req_A)
    cond_A2 = (C_dyn_mat >= C_dyn_req_A)
    # endregion

    # region Bearing B
    # Static load ratings for bearing B (Schaeffler, p. 268)
    P_stat_B = 0                               # No nominal radial or axial forces on bearing B
    C_stat_req_B = 2.1*P_stat_B                # Required static load rating in N, Safety factor according to Stahl, p. 83 and Zaehringer, p. 29

    # Dynamic load ratings (Stahl, p. 84)
    P_dyn_B = 0                                # No nominal radial or axial forces on bearing B
    C_dyn_req_B = math.pow(L_10, (1/3))*P_dyn_B         # Required equivalent dynamic load rating in N

    # Check for static (cond_B1) and dynamic (cond_B2) load for bearing B
    cond_B1 = (C_stat_mat.T >= C_stat_req_B)
    cond_B2 = (C_dyn_mat.T >= C_dyn_req_B)
    # endregion
    # endregion

    # region [2.3]: Calculation of shaft
    # Calculation of shaft safety and inner diameter of hollow shaft
    gearbox = calc_d_sh_plan(gearbox, parameters, shaft, d_ctlg)
    sh_mat = gearbox.shafts.shaft_1

    # Check if shaft endures torsional load
    S_sh_min = np.minimum(np.tile(sh_mat[:, 1], (m, 1)), np.tile(sh_mat[:, 1].reshape(1, m), (m, 1)))
    cond_s1 = (S_sh_min > S_Dt_min)

    # Check if minimum bearing diameter is larger than the minimum shaft diameter
    d_bear_min = np.minimum(np.tile(d_ctlg, (1, m)), np.tile(d_ctlg.reshape(1, m), (m, 1)))
    cond_s2 = (d_bear_min >= d_sh_min)
    # endregion

    # region [2.4]: Check if all conditions are met for bearing combinations and selection of optimum
    # Bearing and shaft conditions are combined
    all_cond = cond_A1 * cond_A2 * cond_B1 * cond_B2 * cond_s1 * cond_s2

    # Find best bearing combination
    poss_all = np.asarray(np.where(all_cond == True))
    poss = sum(poss_all)

    if np.size(poss) == 0:
        setattr(gearbox.error, 'ratio_C_dyn_A', C_dyn_mat/C_dyn_req_A)
        setattr(gearbox.error, 'ratio_C_dyn_B', C_dyn_mat.T/C_dyn_req_B)
        raise ValueError('Error! No bearing combination was found for sun shaft !')

    idx = np.argmin(poss)

    # Calculation of the bearing distances for calc_factors
    # Distances a and b on shaft 1 for chosen bearing combination in mm
    a = (b_ctlg[poss_all[0, idx], 0] - a_ctlg[poss_all[0, idx], 0]) + 5 + b_1 / 2
    # endregion

    # region [3]: Output Assignment
    setattr(gearbox.gears_12, 'alpha_wt_1', alpha_wt_1)                   # working transverse pressure angle in rad

    setattr(gearbox.bearings_1, 'a', a)                                   # distance between wheel 1 and bearing point A in mm
    setattr(gearbox.bearings_1, 'd_sh_A', d_ctlg[poss_all[0, idx], 0])    # inner diameter of bearing A in mm
    setattr(gearbox.bearings_1, 'd_sh_B', d_ctlg[poss_all[1, idx], 0])    # inner diameter of bearing B in mm
    setattr(gearbox.bearings_1, 'm_A', m_ctlg[poss_all[0, idx], 0])       # mass of bearing A in kg
    setattr(gearbox.bearings_1, 'm_B', m_ctlg[poss_all[1, idx], 0])       # mass of bearing B in kg
    setattr(gearbox.bearings_1, 'd_A_A', d_A_ctlg[poss_all[0, idx], 0])   # outer diameter of bearing A in mm
    setattr(gearbox.bearings_1, 'd_A_B', d_A_ctlg[poss_all[1, idx], 0])   # outer diameter of bearing B in mm
    setattr(gearbox.bearings_1, 'b_A', b_ctlg[poss_all[0, idx], 0])       # width of bearing A in mm
    setattr(gearbox.bearings_1, 'b_B', b_ctlg[poss_all[1, idx], 0])       # width of bearing B in mm
    setattr(gearbox.bearings_1, 'd_1_A', d_1_ctlg[poss_all[0, idx], 0])   # outer diameter of inner bearing ring of bearing A in mm
    setattr(gearbox.bearings_1, 'd_1_B', d_1_ctlg[poss_all[1, idx], 0])   # outer diameter of inner bearing ring of bearing B in mm
    setattr(gearbox.bearings_1, 'ID_A', name_ctlg[poss_all[0, idx]])      # Name of bearing A from bearing catalog
    setattr(gearbox.bearings_1, 'ID_B', name_ctlg[poss_all[1, idx]])      # Name of bearing B from bearing catalog

    setattr(gearbox.forces, 'F_u_1', F_u_1)                               # Circumferential force on sun gear in N
    setattr(gearbox.forces, 'F_ax_1', F_ax_1)                             # Axial force on sun gear in N

    d_sh_1 = min(sh_mat[min(poss_all[0, idx], poss_all[1, idx]), 0], gearbox.gears_12.d_f1)
    S_dt_1 = sh_mat[min(poss_all[0, idx], poss_all[1, idx]), 1]
    d_inn_1 = sh_mat[min(poss_all[0, idx], poss_all[1, idx]), 2]
    setattr(gearbox.shafts, 'd_sh_1', d_sh_1)              # Critical diameter of sun shaft in mm
    setattr(gearbox.shafts, 'S_dt_1', S_dt_1)              # Safety factor against torsional fatigue of sun shaft
    setattr(gearbox.shafts, 'd_inn_1', d_inn_1)            # Inner diameter of sun shaft in mm
    # endregion

    return gearbox
