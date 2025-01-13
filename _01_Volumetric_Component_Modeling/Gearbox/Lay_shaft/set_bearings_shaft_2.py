"""
Description:
This function selects deep groove ball bearings for the second shaft of the gearbox from the Schaeffler bearing catalog.
 SHAFT 2:
 Fixed/floating bearings with two deep groove ball bearings
       _
      | |  _
   C--|2|-|3|--D
      |_|

   |-a-|-b-|-c-|   (bearing distances)

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
         shaft: denotes which reduction stage is being considered (1 or 2; for the differential shaft a different calculation is used)
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
Output:  Dimensions of the bearings on the second shaft (input shaft from the machine)
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of bearing loads and shaft design
[2.1] Calculation of pressure angle and gearing forces
[2.2] Calculation of bearing distances a, b and c for bearing force calculation
[2.3] Calculation of bearing forces
[2.4] Calculation of bearing loads (Stahl, starting p. 82)
[2.5] Calculation of shaft
[2.6] Check if all conditions are met for bearing combinations and select optimum
[2.7] Calculation of the bearing distances for calc_factors
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
import numpy as np
# Import classes
# Import methods
from .calc_d_sh import calc_d_sh
# endregion


def set_bearings_shaft_2(gearbox, parameters, shaft, d_ctlg, d_A_ctlg, b_ctlg, C_dyn_ctlg,
                         m_ctlg, f0_ctlg, C_stat_ctlg, d_1_ctlg, name_ctlg):

    # region [1]: Initialization of required values
    # Gearbox Values
    T_nom = gearbox.Input.T_nom*1000                    # Nominal torque of el. motor [Nmm]
    overload_factor = gearbox.Input.overload_factor     # Overload factor of el. motor [-]

    b_1 = gearbox.gears_12.b_1  # Width of wheel 1 [mm]
    d_2 = gearbox.gears_12.d_2  # Pitch diameter of wheel 2 [mm]

    m_n_3 = gearbox.gears_34.m_n_3                      # Normal module of second stage [mm]
    alpha_t = gearbox.gears_34.alpha_t_2                # Pressure angle in transverse section of second stage [rad]
    beta_2 = gearbox.gears_34.beta_2                    # Helix angle of second stage [rad]
    z_3 = gearbox.gears_34.z_3                          # Number of teeth of wheel 3
    z_4 = gearbox.gears_34.z_4                          # Number of teeth of wheel 4
    b_3 = gearbox.gears_34.b_3  # Width of wheel 3 [mm]
    d_3 = gearbox.gears_34.d_3  # Pitch diameter of wheel 3 [mm]

    b_B = gearbox.bearings_1.b_B                        # Width of bearing B [mm]

    a_23 = gearbox.results.a_23                         # Distance between shafts 2&3 [mm]
    i_12 = gearbox.results.i_12                         # Transmission ratio of first stage [-]

    F_u_1 = gearbox.forces.F_u_1                        # Circumferential force on wheel 1 [N]
    F_rad_1 = gearbox.forces.F_rad_1                    # Radial force on wheel 1 [N]
    F_ax_1 = gearbox.forces.F_ax_1                      # Axial force on wheel 1 [N]

    # Parameters
    L_10 = parameters.gearbox.CalcFactors.L_10 / i_12  # Lifetime factor regarding speed of second shaft [10^6 revolutions]
    S_Dt_min = parameters.gearbox.MinSafety.S_Dt_min  # Minimum safety factor against torsional fatigue fracture (Stahl, p. 33) [-]
    b_gap = parameters.gearbox.ConstDim.b_gap  # Gap between components on the shafts [mm]

    # Initialization of bearing matrices for vectorial calculations
    # Variation over the rows means variation of bearing C, variation over the columns varies bearing D
    m = np.size(d_ctlg)
    b_vert = np.tile(b_ctlg, (1, m))        # m x m matrix where the width of bearing C is varied over the rows
    b_hor = b_vert.T                        # m x m matrix where the width of bearing D is varied over the columns
    # m x m matrices where the static and dynamic load ratings of the bearings are varied over the rows
    C_stat_mat = np.tile(C_stat_ctlg, (1, m))
    C_dyn_mat = np.tile(C_dyn_ctlg, (1, m))
    # endregion

    # region [2]: Calculation of bearing loads and shaft design
    # region [2.1]: Calculation of pressure angle and gearing forces
    # Calculation of the operating pressure angle in rad (Kirchner, p. 189)
    alpha_wt = math.acos((((z_3+z_4)*m_n_3)/(2*a_23))*(math.cos(alpha_t)/math.cos(beta_2)))

    # Calculation of occurring gearing forces in N
    F_u_2 = F_u_1
    F_ax_2 = F_ax_1
    F_rad_2 = F_rad_1
    F_u_3 = 2*(i_12*T_nom)/d_3
    F_ax_3 = F_u_3*math.tan(beta_2)
    F_rad_3 = F_u_3*math.tan(alpha_wt)
    # endregion

    # region [2.2]: Calculation of bearing distances a, b and c for bearing force calculation
    a = b_vert/2+b_gap+b_1/2
    if gearbox.Input.axles.lower() == 'parallel':
        b = b_1/2+b_gap+b_3/2
    else:   # gearbox.Input.axles.lower() == 'coaxial':
        b = b_1/2+b_gap+b_B+b_gap+35+b_gap+b_3/2       # distance is larger for coaxial gearboxes
    c = b_3/2+b_gap+b_hor/2
    # endregion

    # region [2.3]: Calculation of bearing forces
    # Bearing reaction forces in N in Y-direction
    F_Cy = 1./(a+b+c)*(F_rad_3*c-F_rad_2*(b+c)+F_ax_3*d_3/2+F_ax_2*d_2/2)
    F_Dy = F_rad_3-F_rad_2-F_Cy
    # Bearing reaction forces in N in Z-direction
    F_Cz = 1./(a+b+c)*(F_u_3*c-F_u_2*(b+c))
    F_Dz = F_u_3-F_u_2-F_Cz
    # Radial forces in N
    F_radC = np.sqrt(np.square(F_Cz)+np.square(F_Cy))
    F_radD = np.sqrt(np.square(F_Dz)+np.square(F_Dy))

    # Distribution of axial forces on bearing with lower radial load (Zaehringer, p. 28/29)
    F_axC = (F_radC <= F_radD)*(F_ax_3-F_ax_2)
    F_axD = (F_radC > F_radD)*(F_ax_3-F_ax_2)
    # endregion

    # region [2.4]: Calculation of bearing loads (Stahl, starting p. 82)
    # region Bearing C
    # Definition of axial to radial load ratio e (Stahl, p.84)
    val = f0_ctlg*F_axC/C_stat_ctlg
    e = (val < 0.5)*0.22+((val >= 0.5) & (val < 0.9))*0.24+((val >= 0.9) & (val < 1.6))*0.28\
        + ((val >= 1.6) & (val < 3))*0.32+((val >= 3) & (val < 6))*0.36+(val >= 6)*0.43

    # Determination of radial and axial factors (X and Y) of bearing (Stahl, p.84)
    par = F_axC/F_radC
    X = (par <= e)+(par > e)*0.56
    Y = ((par > e) & (e == 0.22) * 2) + ((par > e) & (e == 0.24)) * 1.8 + ((par > e) & (e == 0.28)) * 1.6 \
        + ((par > e) & (e == 0.32)) * 1.4 + ((par > e) & (e == 0.36)) * 1.2 + ((par > e) & (e == 0.43))

    # Static load ratings (Stahl, p. 82/83)
    P_stat_C = (0.6*F_radC+0.5*F_axC)*overload_factor   # Equivalent static load rating in N (in relation to T_max)
    C_stat_req_C = 2.1*P_stat_C                         # Required static load rating in N, Safety factor according to Stahl, p. 83 and Zaehringer, p. 29

    # Dynamic load ratings (Stahl, p. 84)
    P_next_C = (X*F_radC)+(Y*F_axC)                     # Equivalent dynamic load rating in N (in relation to T-nom)
    C_dyn_req_C = math.pow(L_10, (1/3))*P_next_C         # Required equivalent dynamic load rating in N

    # Check for static (cond_C1) and dynamic (cond_C2) load for bearing C
    cond_C1 = (C_stat_mat >= C_stat_req_C)
    cond_C2 = (C_dyn_mat >= C_dyn_req_C)
    # endregion

    # region Bearing D:
    # Definition of axial to radial load ratio e (Stahl, p.84)
    val = f0_ctlg.T*F_axD/C_stat_ctlg.T
    e = (val < 0.5) * 0.22 + ((val >= 0.5) & (val < 0.9)) * 0.24 + ((val >= 0.9) & (val < 1.6)) * 0.28 \
        + ((val >= 1.6) & (val < 3)) * 0.32 + ((val >= 3) & (val < 6)) * 0.36 + (val >= 6) * 0.43

    # Determination of radial and axial factors (X and Y) of bearing (Stahl, p.84)
    par = F_axD/F_radD
    X = (par <= e)+(par > e)*0.56
    Y = ((par > e) & (e == 0.22)) * 2 + ((par > e) & (e == 0.24)) * 1.8 + ((par > e) & (e == 0.28)) * 1.6 \
        + ((par > e) & (e == 0.32)) * 1.4 + ((par > e) & (e == 0.36)) * 1.2 + ((par > e) & (e == 0.43))

    # Static load ratings (Stahl, p. 82/83)
    P_stat_D = (0.6*F_radD+0.5*F_axD)*overload_factor   # Equivalent static load rating in N (in relation to T_max)
    C_stat_req_D = 2.1*P_stat_D                         # Required static load rating in N, Safety factor according to Stahl, p. 83 and Zaehringer, p. 29

    # Dynamic load ratings (Stahl, p. 84)
    P_next_D = (X*F_radD)+(Y*F_axD)                     # Equivalent dynamic load rating in N (in relation to T_nom)
    C_dyn_req_D = math.pow(L_10, (1/3))*P_next_D         # Required equivalent dynamic load rating in N

    # Check for static (cond_D1) and dynamic (cond_D2) load for bearing D
    cond_D1 = (C_stat_mat.T >= C_stat_req_D)
    cond_D2 = (C_dyn_mat.T >= C_dyn_req_D)
    # endregion
    # endregion

    # region [2.5]: Calculation of shaft
    # Calculation of shaft safety and inner diameter of hollow shaft
    gearbox = calc_d_sh(gearbox, parameters, shaft, d_ctlg)
    sh_mat = gearbox.shafts.shaft_2

    # Check if shaft endures torsional load
    S_sh_min = np.fmin(np.tile(sh_mat[:, 1].reshape(m, 1), (1, m)), np.tile(sh_mat[:, 1].reshape(1, m), (m, 1)))
    cond_s = (S_sh_min > S_Dt_min)
    # endregion

    #  region [2.6]: Check if all conditions are met for bearing combinations and select optimum
    # Bearing and shaft conditions are combined
    all_cond = cond_C1*cond_C2*cond_D1*cond_D2*cond_s

    # Find the best bearings combination
    poss_all = np.asarray(np.where(all_cond == True))
    poss = sum(poss_all)

    # endregion

    # region [2.7]: Calculation of the bearing distances for calc_factors
    if np.size(poss) == 0:
        setattr(gearbox.error, 'ratio_C_dyn_C', C_dyn_mat / C_dyn_req_C)
        setattr(gearbox.error, 'ratio_C_dyn_D', C_dyn_mat.T/C_dyn_req_D)
        raise ValueError('Error! No bearing combination was found for shaft 2!')

    idx = np.argmin(poss)

    # Distances a and c on shaft 2 for chosen bearing combination in mm
    a = a[poss_all[0, idx], 0]
    c = c[0, poss_all[1, idx]]
    # Distance of the bearing points on shaft 2 in mm
    l_2 = a+b+c
    # Distances of the force application points and the middle of the bearings for wheel 2 and 3 in mm
    s_2 = (-a+b+c)/2
    s_3 = (a+b-c)/2
    # endregion
    # endregion

    # region [3]: Output assignment
    setattr(gearbox.gears_34, 'alpha_wt_2', alpha_wt)       # working transverse pressure angle in rad

    setattr(gearbox.results, 'a_23', a_23)                  # distance between shafts 3&4 in mm

    setattr(gearbox.bearings_2, 's_2', s_2)                 # distance between middle of the shaft and wheel 2
    setattr(gearbox.bearings_2, 's_3', s_3)                 # distance between middle of the shaft and wheel 3
    setattr(gearbox.bearings_2, 'l_2', l_2)                 # bearing distance on shaft 2 in mm
    setattr(gearbox.bearings_2, 'a', a)                     # distance between bearing point C and wheel 2 in mm
    setattr(gearbox.bearings_2, 'b', b)                     # distance between wheel 2 and 3 in mm
    setattr(gearbox.bearings_2, 'c', c)                     # distance between wheel 3 and bearing point D in mm
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
    setattr(gearbox.bearings_2, 'ID_C', name_ctlg[poss_all[0, idx]])        # Name of bearing C from bearing catalog
    setattr(gearbox.bearings_2, 'ID_D', name_ctlg[poss_all[1, idx]])        # Name of bearing D from bearing catalog

    setattr(gearbox.forces, 'F_u_2', F_u_2)                 # Circumferential force of gear 2 in N
    setattr(gearbox.forces, 'F_ax_2', F_ax_2)               # Axial force of shaft 2 in N
    setattr(gearbox.forces, 'F_rad_2', F_rad_2)             # Radial force of shaft 2 in N
    setattr(gearbox.forces, 'F_u_3', F_u_3)                 # Circumferential force of gear 3 in N
    setattr(gearbox.forces, 'F_ax_3', F_ax_3)               # Axial force of shaft 3 in N
    setattr(gearbox.forces, 'F_rad_3', F_rad_3)             # Radial force of shaft 3 in N

    setattr(gearbox.shafts, 'd_sh_2', sh_mat[min(poss_all[0, idx], poss_all[1, idx]), 0])   # Critical diameter of shaft 2 in mm
    setattr(gearbox.shafts, 'S_dt_2', sh_mat[min(poss_all[0, idx], poss_all[1, idx]), 1])   # Safety factor against torsional fatigue of shaft 2
    setattr(gearbox.shafts, 'd_inn_2', sh_mat[min(poss_all[0, idx], poss_all[1, idx]), 2])  # Inner diameter of shaft 2 in mm
    # endregion

    return gearbox
