"""
Description:
This function selects taper roller bearings for the second shaft of
the gearbox from the Schaeffler bearing catalog.
SHAFT 2:
Fixed bearing combination in X arrangement with two taper roller bearings
        _
       | |  _
   -C--|1|-|2|--D-
       |_|

    |-a-|-b-|-c-|

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
Output:  Dimensions of the bearings on planet shafts
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization required values
[2] Calculation of bearing loads and shaft design
[2.1] Calculation of pressure angle and gearing forces
[2.2] Calculation of bearing distances a, b and c
[2.3] Calculation of bearing forces
[2.4] Calculation of bearing loads (Stahl, pp. 82)
[2.5] Calculation of shaft
[2.6] Check if all conditions are met for bearing combinations and select optimum
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


def set_bearings_planet(gearbox, parameters, shaft, d_ctlg, d_A_ctlg, b_ctlg, C_dyn_ctlg, m_ctlg, a_ctlg, e_ctlg, Y_ctlg, C_stat_ctlg, Y_0_ctlg, d_1_ctlg, name_ctlg):
    # region [1]: Initialization of required values
    # Gearbox Values
    overload_factor = gearbox.Input.overload_factor         # Overload factor of el. motor [-]

    m_n_1 = gearbox.gears_12.m_n_1                          # Normal module of first stage [mm]
    m_n_2 = gearbox.gears_12.m_n_2                          # Normal module of second stage [mm]
    alpha_t_1 = gearbox.gears_12.alpha_t_1                  # Pressure angle in transverse section of the first stage [rad]
    alpha_t_2 = gearbox.gears_12.alpha_t_2                  # Pressure angle in transverse section of the second stage [rad]
    beta_1 = gearbox.gears_12.beta_1                        # Helix angle of first stage [rad]
    beta_2 = gearbox.gears_12.beta_2                        # Helix angle of second stage [rad]
    z_1 = gearbox.gears_12.z_1                              # Number of teeth of sun gear
    z_p1 = gearbox.gears_12.z_p1                            # Number of teeth of planet 1
    z_p2 = gearbox.gears_12.z_p2                            # Number of teeth of planet 2
    z_2 = gearbox.gears_12.z_2                              # Number of teeth of ring gear (negative)
    b_1 = gearbox.gears_12.b_1                              # Width of sun gear [mm]
    b_2 = gearbox.gears_12.b_2                              # Width of planet 2 [mm]
    d_1 = gearbox.gears_12.d_1                              # Pitch diameter of sun gear [mm]
    d_p1 = gearbox.gears_12.d_p1                            # Pitch diameter of planet 1 [mm]
    d_p2 = gearbox.gears_12.d_p2                            # Pitch diameter of planet 2 [mm]
    d_2 = gearbox.gears_12.d_2                              # Pitch diameter of ring gear [mm]

    i_p_rel = abs(gearbox.results.i_p_rel)                  # Relative transmission ratio of the planets (is negative) [-]

    F_u_1 = gearbox.forces.F_u_1                            # Circumferential force on sun gear [N]

    # Parameters
    b_gap = parameters.gearbox.ConstDim.b_gap               # Gap between components on the shafts [mm]
    L_10 = parameters.gearbox.CalcFactors.L_10/i_p_rel      # Lifetime factor regarding speed of planets [10^6 revolutions]
    S_Dt_min = parameters.gearbox.MinSafety.S_Dt_min        # Minimum safety factor against torsional fatigue fracture (Stahl, p. 33) [-]
    d_sh_p = parameters.gearbox.ConstDim.d_planbolt         # Diameter of planet bolt [mm]

    # Initialization of bearing matrices for vectorial calculations
    # Variation over the rows means variation of bearing C, variation over the columns varies bearing D
    m = len(d_ctlg)
    b_vert = np.tile(b_ctlg, (1, m))      # m x m matrix where the width of bearing C is varied over the rows
    b_hor = b_vert.T                    # m x m matrix where the width of bearing D is varied over the columns
    a_vert = np.tile(a_ctlg, (1, m))      # m x m matrix where the bearing point distance of bearing C is varied over the rows
    a_hor = a_vert.T                    # m x m matrix where the bearing point distance of bearing D is varied over the columns
    e_mat = np.tile(e_ctlg, (1, m))       # m x m matrix where the axial to radial load ratio of the bearings is varied over the rows
    # m x m matrices where the static and dynamic load ratings of the bearings are varied over the rows
    C_stat_mat = np.tile(C_stat_ctlg, (1, m))
    C_dyn_mat = np.tile(C_dyn_ctlg, (1, m))
    # endregion

    # region [2]: Calculation of bearing loads and shaft design
    # region [2.1]: Calculation of pressure angle and gearing forces
    # Calculation of the operating pressure angle in rad according (Kirchner, p. 189)
    alpha_wt_1 = math.acos((((z_1+z_p1)*m_n_1)/(d_1+d_p1))*(math.cos(alpha_t_1)/math.cos(beta_1)))
    alpha_wt_2 = math.acos((((z_p2+z_2)*m_n_2)/(d_p2-d_2))*(math.cos(alpha_t_2)/math.cos(beta_2)))

    # Calculation of occurring gearing forces in N according (Stahl, p. 2)
    F_u_p1 = 1/3*F_u_1                      # Circumferential force of planet gear 1
    F_ax_p1 = F_u_p1*math.tan(beta_1)       # Axial force of planet gear 1
    F_rad_p1 = F_u_p1*math.tan(alpha_wt_1)  # Radial force of planet gear 1
    F_u_p2 = F_u_p1*d_p1/d_p2               # Circumferential force of planet gear 2
    F_ax_p2 = F_u_p2*math.tan(beta_2)       # Axial force of planet gear 2
    F_rad_p2 = F_u_p2*math.tan(alpha_wt_2)  # Radial force of planet gear 2

    # Calculation of the circumferential and axial forces on the planet as a whole in N
    F_u_sp = F_u_p2-F_u_p1                  # Circumferential force on the planet bolt
    F_ax_p = F_ax_p2-F_ax_p1                # Axial force on the planet bolt
    # endregion

    # region [2.2]: Calculation of bearing distances a, b and c
    # Auxiliary parameters of distances on planet shaft
    a = b_vert-a_vert+b_gap+b_1/2
    b = (b_1+b_2)/2+b_gap
    c = b_hor-a_hor+b_gap+b_2/2
    # endregion

    # region [2.3]: Calculation of bearing forces
    # Bearing reaction forces in N in Y-direction
    F_Cy = (1/(a+b+c))*(F_rad_p2*c-F_rad_p1*(b+c)+F_ax_p1*d_p1/2+F_ax_p2*d_p2/2)
    F_Dy = F_rad_p2-F_rad_p1-F_Cy
    # Bearing reaction forces in N in Z-direction
    F_Cz = (1/(a+b+c))*(F_u_p2*c-F_u_p1*(b+c)-F_u_sp*(b/2+c))
    F_Dz = -F_Cz-F_u_p1-F_u_sp+F_u_p2
    # Radial bearing forces in N
    F_radC = np.sqrt(np.power(F_Cy, 2)+np.power(F_Cz, 2))
    F_radD = np.sqrt(np.power(F_Dy, 2)+np.power(F_Dz, 2))

    # Determination of the distribution of axial forces (Stahl, pp. 82)
    val_C = F_radC/Y_ctlg
    val_D = F_radD/Y_ctlg.T

    # Axial bearing forces in N
    F_axC = ((val_C < val_D) & (abs(F_ax_p) <= abs(0.5*val_D-val_C))) * (0.5*val_D-F_ax_p)
    F_axD = (val_C >= val_D) * (F_ax_p+(0.5*val_C)) +\
            ((val_C < val_D) & (abs(F_ax_p) > abs(0.5*val_D-val_C))) * (F_ax_p+(0.5*val_C))
    # endregion

    # region [2.4]: Calculation of bearing loads (Stahl, pp. 82)
    #  region Bearing C
    # Static load ratings (Stahl, pp. 82)
    P_stat_C = (0.5*F_radC+Y_0_ctlg*F_axC)*overload_factor  # Equivalent static load rating in N (in relation to T_max)
    C_stat_req_C = 4.1*P_stat_C                             # Required static load rating in N, Safety factor according to Stahl, p. 83 and Zaehringer, p. 29

    # Determination of equivalent dynamic load ratings in N (Stahl, p. 84) (in relation to T_nom)
    par_C = F_axC/F_radC
    P_next_C = (par_C <= e_mat) * (F_radC+(1.12*Y_ctlg*F_axC)) +\
               (par_C > e_mat) * ((0.67*F_radC) + (1.68*Y_ctlg*F_axC))
    C_dyn_req_C = math.pow(L_10, (3/10))*P_next_C                       # Required equivalent dynamic load rating in N

    # Check for static (cond_C1) and dynamic (cond_C2) load for bearing C
    cond_C1 = (C_stat_mat >= C_stat_req_C)
    cond_C2 = (C_dyn_mat >= C_dyn_req_C)
    # endregion

    # region Bearing D
    # Static load ratings (Schaeffler, p. 268)
    P_stat_D = (0.5*F_radD+Y_0_ctlg.T*F_axD)*overload_factor   # Equivalent static load rating in N (in relation to T_max)
    C_stat_req_D = 4.1*P_stat_D                                # Required static load rating in N, Safety factor according to Stahl, p. 83 and Zaehringer, p. 29

    # Determination of equivalent dynamic load ratings in N (Stahl, p. 84) (in relation to T_nom)
    par_D = F_axD/F_radD
    P_next_D = (par_D <= e_mat.T) * (F_radD+(1.12*Y_ctlg.T*F_axD)) +\
               (par_D > e_mat.T) * ((0.67*F_radD)+(1.68*Y_ctlg.T*F_axD))
    C_dyn_req_D = math.pow(L_10, (3/10))*P_next_D                       # Required equivalent dynamic load rating in N

    # Check for static (cond_D1) and dynamic (cond_D2) load for bearing D
    cond_D1 = (C_stat_mat.T >= C_stat_req_D)
    cond_D2 = (C_dyn_mat.T >= C_dyn_req_D)
    # endregion
    # endregion

    # region [2.5]: Calculation of shaft
    # Calculation of shaft safety and inner diameter of hollow shaft
    gearbox = calc_d_sh_plan(gearbox, parameters, shaft, d_ctlg)
    sh_mat = gearbox.shafts.shaft_p

    # Check if shaft endures torsional load
    S_sh_min = np.minimum(np.tile(sh_mat[:, 1], (m, 1)), np.tile(sh_mat[:, 1].reshape(1, m), (m, 1)))
    cond_s1 = (S_sh_min > S_Dt_min)

    # Check if minimum bearing diameter is larger than the minimum shaft diameter
    d_bear_min = np.minimum(np.tile(d_ctlg, (1, m)), np.tile(d_ctlg.reshape(1, m), (m, 1)))
    cond_s2 = (d_bear_min >= d_sh_p)
    # endregion

    # region [2.6]: Check if all conditions are met for bearing combinations and select optimum
    # Bearing and shaft conditions are combined
    all_cond = cond_C1 * cond_C2 * cond_D1 * cond_D2 * cond_s1 * cond_s2

    # Find best bearing combination
    poss_all = np.asarray(np.where(all_cond == True))
    poss = sum(poss_all)

    if np.size(poss) == 0:
        setattr(gearbox.error, 'ratio_C_dyn_C', C_dyn_mat/C_dyn_req_C)
        setattr(gearbox.error, 'ratio_C_dyn_D', C_dyn_mat.T/C_dyn_req_D)
        raise ValueError('Error! No bearing combination was found for planets!')

    idx = np.argmin(poss)

    # region Calculation of the bearing distances for calc_factors
    # Distances a and c on planet shaft for chosen bearing combination in mm
    a = a[poss_all[0, idx], 0]
    c = c[0, poss_all[1, idx]]
    # Distance of the bearing points on planet shaft in mm
    l_2 = a+b+c
    # Distances of the force application points and the middle of the bearings for planet wheel 1 and 2 in mm
    s_p1 = (-a+b+c)/2
    s_p2 = (a+b-c)/2
    # endregion
    # endregion

    # region [3]: Output Assignment
    setattr(gearbox.gears_12, 'alpha_wt_2', alpha_wt_2)                     # working transverse pressure angle in rad

    setattr(gearbox.bearings_2, 's_p1', s_p1)                               # distance between middle of the shaft and planet 1 in mm
    setattr(gearbox.bearings_2, 's_p2', s_p2)                               # distance between middle of the shaft and planet 2 in mm
    setattr(gearbox.bearings_2, 'l_2', l_2)                                 # bearing distance in mm
    setattr(gearbox.bearings_2, 'a', a)                                     # distance between bearing point C and planet 1 in mm
    setattr(gearbox.bearings_2, 'b', b)                                     # distance between the middles of planet 1 and 2 in mm
    setattr(gearbox.bearings_2, 'c', c)                                     # distance between planet 2 and bearing point D in mm
    setattr(gearbox.bearings_2, 'd_sh_C', d_ctlg[poss_all[0, idx], 0])      # inner diameter of bearing C in mm
    setattr(gearbox.bearings_2, 'd_sh_D', d_ctlg[poss_all[1, idx], 0])      # inner diameter of bearing D in mm
    setattr(gearbox.bearings_2, 'm_C', m_ctlg[poss_all[0, idx], 0])         # mass of bearing C in kg
    setattr(gearbox.bearings_2, 'm_D', m_ctlg[poss_all[1, idx], 0])         # mass of bearing D in kg
    setattr(gearbox.bearings_2, 'd_A_C', d_A_ctlg[poss_all[0, idx], 0])     # outer diameter of bearing C in mm
    setattr(gearbox.bearings_2, 'd_A_D', d_A_ctlg[poss_all[1, idx], 0])     # outer diameter of bearing D in mm
    setattr(gearbox.bearings_2, 'b_C', b_ctlg[poss_all[0, idx], 0])         # width of bearing C in mm
    setattr(gearbox.bearings_2, 'b_D', b_ctlg[poss_all[1, idx], 0])         # width of bearing D in mm
    setattr(gearbox.bearings_2, 'd_1_C', d_1_ctlg[poss_all[0, idx], 0])     # outer diameter of inner bearing ring of bearing C in mm
    setattr(gearbox.bearings_2, 'd_1_D', d_1_ctlg[poss_all[1, idx], 0])     # outer diameter of inner bearing ring of bearing D in mm
    setattr(gearbox.bearings_2, 'ID_C', name_ctlg[poss_all[0, idx], 0])     # Name of bearing C from bearing catalog
    setattr(gearbox.bearings_2, 'ID_D', name_ctlg[poss_all[1, idx], 0])     # Name of bearing D from bearing catalog

    setattr(gearbox.forces, 'F_u_p1', F_u_p1)                               # Circumferential force on planet 1 in N
    setattr(gearbox.forces, 'F_ax_p1', F_ax_p1)                             # Axial force of planet 1 in N
    setattr(gearbox.forces, 'F_rad_p1', F_rad_p1)                           # Radial force of planet 1 in N
    setattr(gearbox.forces, 'F_u_p2', F_u_p2)                               # Circumferential force of planet 2 in N
    setattr(gearbox.forces, 'F_ax_p2', F_ax_p2)                             # Axial force of planet 2 in N
    setattr(gearbox.forces, 'F_rad_p2', F_rad_p2)                           # Radial force of planet 2 in N
    setattr(gearbox.forces, 'F_ax_p', F_ax_p)                               # Resulting axial force on every planet in N

    d_sh_p = sh_mat[min(poss_all[0, idx], poss_all[1, idx]), 0]
    S_dt_p = sh_mat[min(poss_all[0, idx], poss_all[1, idx]), 1]
    d_inn_p = sh_mat[min(poss_all[0, idx], poss_all[1, idx]), 2]
    setattr(gearbox.shafts, 'd_sh_p', d_sh_p)       # Critical diameter of planet bolts in mm
    setattr(gearbox.shafts, 'S_dt_p', S_dt_p)       # Safety factor against torsional fatigue of planet bolts
    setattr(gearbox.shafts, 'd_inn_p', d_inn_p)     # Inner diameter of planet bolts in mm
    # endregion

    return gearbox
