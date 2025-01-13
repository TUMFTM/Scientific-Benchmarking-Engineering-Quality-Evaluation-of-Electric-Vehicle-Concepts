"""
Description:    This function computes a bevel gear differential for gearbox with angular ball bearings.
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
            (2) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
            (3) Schaeffler, "Waelzlager", Bearing Catalogue, 2019
            (4) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Master Thesis, TUM, 2020
            (5) K. Stahl, Documentation Lecture "Maschinenelemente", TUM, 2015/2016

------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  Dimensioning of all elements on the differential (gears, shaft, bearings)
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of differential dimensions and gear data
[3] Selection of bearings according to input load and desired lifetime
[3.1] Bearing E: Static load ratings in N (Stahl, pp. 82)
[3.2] Bearing F: Static load ratings in N (Stahl, pp. 82)
[3.3] Check if all conditions are met for bearing combinations and selection of optimum
[3.4] Calculation of the bearing distances for calc_factors
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
import numpy as np
# Import classes
# Import methods
# endregion


def set_diff_plan(gearbox, parameters):
    # region[1]: Initialization of required values
    # Gearbox Values
    T_max = gearbox.Input.T_max                             # Maximum torque of el. motor [Nm]
    overload_factor = gearbox.Input.overload_factor         # Overload factor of el. motor [-]

    i_1s = gearbox.results.i_1s                             # Total transmission ratio of planetary gearbox [-]
    b_1 = gearbox.gears_12.b_1                              # Width of first stage gears [mm]
    b_2 = gearbox.gears_12.b_2                              # Width of second stage gears [mm]
    d_s = gearbox.gears_12.d_s                              # Diameter of the planet circle [mm]
    d_ap2 = gearbox.gears_12.d_ap2                          # Outer diameter of planet 2 [mm]

    b_C = gearbox.bearings_2.b_C                            # Width of bearing C [mm]
    b_D = gearbox.bearings_2.b_D                            # Width of bearing D [mm]
    d_A_B = gearbox.bearings_1.d_A_B                        # Outer diameter of bearing A [mm]

    d_sh_3 = gearbox.shafts.d_sh_3                          # Outer diameter of output shaft [mm]
    F_ax_p = gearbox.forces.F_ax_p                          # Resulting axial force on each planet [N]

    # Parameters
    b_d_bevel = parameters.gearbox.GearingConst.b_d_bevel   # Empirical ratio of bevel gear width and outer diameter (Koehler [1], p.41) [-]
    d_bevel = parameters.gearbox.GearingConst.d_bevel       # Ratio between smaller and larger bevel gears of the diffferential (Koehler [1], p.47) [-]
    t_diffcage = parameters.gearbox.ConstDim.t_diffcage     # Thickness of differential housing [mm]
    b_gap = parameters.gearbox.ConstDim.b_gap               # Gap between components on the shafts [mm]
    regr_d_bevel = parameters.regr.gearbox.d_bevel           # Regression formula for the diameter of the larger differential gears in mm ([1], p. 46)
    L_10 = parameters.gearbox.CalcFactors.L_10/gearbox.results.i_1s  # Lifetime factor regarding differential shaft speed [10^6 revolutions]

    # Loading of the bearing catalogue
    ab = parameters.gearbox.BearCtlg.ang_ball                       # Loading of Schaeffler angular ball bearing catalogue (starting on p. 272)
    length_ctlg = len(ab)
    d_ctlg = np.array(ab.d.values).reshape(length_ctlg, 1)            # List of inner bearing diameters [mm]
    d_A_ctlg = np.array(ab.d_A.values).reshape(length_ctlg, 1)        # List of outer bearing diameters [mm]
    b_ctlg = np.array(ab.b.values).reshape(length_ctlg, 1)            # List of bearing widths [mm]
    a_ctlg = np.array(ab.a.values).reshape(length_ctlg, 1)            # List of bearing point distances [mm]
    C_dyn_ctlg = np.array(ab.C_dyn.values).reshape(length_ctlg, 1)    # List of dynamic load ratings [N]
    m_ctlg = np.array(ab.m.values).reshape(length_ctlg, 1)            # List of bearing masses [kg]
    d_1_ctlg = np.array(ab.d_1.values).reshape(length_ctlg, 1)        # List of diameters of inner bearing ring [mm]
    C_stat_ctlg = np.array(ab.C_stat.values).reshape(length_ctlg, 1)  # List of static load ratings [N]
    name_ctlg = ab.Name                                               # List of bearing codes

    # Initialization of bearing matrices for vectorial calculations
    # Variation over the rows means variation of bearing E, variation over the columns varies bearing F
    d_vert = np.tile(d_ctlg, (1, length_ctlg))       # m x m matrix where the inner diameter of bearing E is varied over the rows
    d_hor = d_vert.T                                # m x m matrix where the inner diameter of bearing F is varied over the columns
    # m x m matrices where the static and dynamic load ratings of the bearings are varied in over the rows
    C_stat_mat = np.tile(C_stat_ctlg, (1, length_ctlg))
    C_dyn_mat = np.tile(C_dyn_ctlg, (1, length_ctlg))
    # endregion

    # region [2]: Calculation of differential dimensions and gear data
    # Calculation of differential data for one EM on the axle
    if gearbox.Input.num_EM == 1:
        # Empirical diameters of differential bevel gears in mm (Koehler [1], pp .46)
        # Empirical diameter of larger bevel gears in mm
        d_bev_l = regr_d_bevel.coefficients[0] + regr_d_bevel.coefficients[1]*(T_max*i_1s)
        d_bev_s = d_bevel*d_bev_l                  # Empirical diameter of smaller bevel gears in mm

        # Diameter of differential cage in mm (Koehler [4], p.59)
        d_diffcage = d_bev_l+10+2*t_diffcage

        # Determination of the empirical width of bevel gearing in mm (Koehler [1], p.47)
        b_bev = b_d_bevel*d_bev_l

        # Determination of the differential cage width in mm
        b_diffcage = d_bev_s+2*t_diffcage
    else:  # substitute values for plotting of planetary gearboxes without differential
        b_diffcage = parameters.gearbox.ConstDim.b_gap
    # endregion

    # region [3]: Selection of bearings according to input load and desired lifetime
    # Definition of initial inner bearing diameters in mm
    if gearbox.Input.num_EM == 1:
        d_sh_E_min = d_sh_3+4+10
    else:   # gearbox.Input.num_EM == 2:
        d_sh_E_min = d_sh_3

    d_sh_F_min = d_A_B+10

    # Bearings nominally experience no radial load (central shafts in planetary gears)!
    # Definition of axial Forces on planet carrier
    F_ax_s = 3*F_ax_p
    F_axF = F_ax_s

    # region [3.1]: Bearing E: Static load ratings in N (Stahl, pp. 82)
    P_stat_E = 0                               # Equivalent static load rating in N (in relation to T_max; only axial Forces)
    C_stat_req_E = 2.1*P_stat_E                # Required static load rating in N, Safety factor according to Stahl, p. 83

    # Determination of equivalent dynamic load ratings in N (Stahl, p. 84) (in relation to T_nom)
    P_dyn_E = 0
    C_dyn_req_E = math.pow(L_10, (1/3))*P_dyn_E         # Required equivalent dynamic load rating in N

    # Check for static (cond_E1) and dynamic (cond_E2) load for bearing E
    cond_E1 = (C_stat_mat >= C_stat_req_E)
    cond_E2 = (C_dyn_mat >= C_dyn_req_E)

    # Check for minimum bearing E diameter
    cond_s1 = (d_vert >= d_sh_E_min)
    # endregion

    # region [3.2]: Bearing F: Static load ratings in N (Stahl, pp. 82)
    P_stat_F = 0.26*F_axF*overload_factor      # No nominal radial or axial forces on bearing F
    C_stat_req_F = 2.1*P_stat_F                # Required static load rating in N, Safety factor according to Stahl, p. 83

    # Determination of equivalent dynamic load ratings in N (Stahl, p. 84) (in relation to T_nom)
    P_dyn_F = 0.57*F_axF                       # No nominal radial forces on bearing F
    C_dyn_req_F = math.pow(L_10, (1/3))*P_dyn_F         # Required equivalent dynamic load rating in N

    # Check for static (cond_F1) and dynamic (cond_F2) load for bearing F
    cond_F1 = (C_stat_mat >= C_stat_req_F)
    cond_F2 = (C_dyn_mat >= C_dyn_req_F)

    # Check for minimum bearing F diameter
    cond_s2 = (d_hor >= d_sh_F_min)
    # endregion

    # region [3.3]: Check if all conditions are met for bearing combinations and selection of optimum
    # Bearing and shaft conditions are combined
    all_cond = cond_E1 * cond_E2 * cond_F1 * cond_F2 * cond_s1 * cond_s2

    # Find best bearing combination
    poss_all = np.asarray(np.where(all_cond == True))
    poss = sum(poss_all)

    if np.size(poss) == 0:
        # Print error message if no bearings are found
        gearbox.error.ratio_C_dyn_E = C_dyn_mat / C_dyn_req_E
        gearbox.error.ratio_C_dyn_F = C_dyn_mat.T / C_dyn_req_F
        raise ValueError('Error! No bearing combination was found for planet carrier!')

    idx = np.argmin(poss)
    # endregion

    # region [3.4]: Calculation of the bearing distances for calc_factors
    # Distances a and b on shaft 1 for chosen bearing combination in mm
    if gearbox.Input.num_EM == 1:
        # Integration of differential in planet carrier if planet circle is large enough
        # noinspection PyUnboundLocalVariable
        if d_s > d_diffcage+4+d_ap2:
            a = (b_ctlg[poss_all[0, idx], 0] - a_ctlg[poss_all[0, idx], 0]) + b_diffcage+b_gap/2
        else:
            a = (b_ctlg[poss_all[0, idx], 0] - a_ctlg[poss_all[0, idx], 0])+b_diffcage+5+b_D+b_gap+b_2+b_gap/2
    else:   # gearbox.Input.num_EM == 2:
        a = (b_ctlg[poss_all[0, idx], 0] - a_ctlg[poss_all[0, idx], 0]) + 5+b_D+b_gap+b_2+b_gap/2

    b = (b_ctlg[poss_all[1, idx], 0] - a_ctlg[poss_all[1, idx], 0]) + 5+b_C+b_gap+b_1+b_gap/2
    # endregion
    # endregion

    # region [4]: Output Assignment
    setattr(gearbox.differential, 'b_diffcage', b_diffcage)               # Width of the differential cage in mm

    setattr(gearbox.bearings_3, 'a', a)         # distance between bearing point E and the middle of the planets in mm
    setattr(gearbox.bearings_3, 'b', b)         # distance between the middle of the planets and bearing point F in mm
    setattr(gearbox.bearings_3, 'd_sh_E', d_ctlg[poss_all[0, idx], 0])    # inner diameter of bearing E in mm
    setattr(gearbox.bearings_3, 'd_sh_F', d_ctlg[poss_all[1, idx], 0])    # inner diametet of bearing F in mm
    setattr(gearbox.bearings_3, 'm_E', m_ctlg[poss_all[0, idx], 0])       # mass of bearing E in kg
    setattr(gearbox.bearings_3, 'm_F', m_ctlg[poss_all[1, idx], 0])       # mass of bearing F in kg
    setattr(gearbox.bearings_3, 'd_A_E', d_A_ctlg[poss_all[0, idx], 0])   # outer diameter of bearing E in mm
    setattr(gearbox.bearings_3, 'd_A_F', d_A_ctlg[poss_all[1, idx], 0])   # outer diameter of bearing F in mm
    setattr(gearbox.bearings_3, 'b_E', b_ctlg[poss_all[0, idx], 0])       # width of bearing E in mm
    setattr(gearbox.bearings_3, 'b_F', b_ctlg[poss_all[1, idx], 0])       # width of bearing F in mm
    setattr(gearbox.bearings_3, 'd_1_E', d_1_ctlg[poss_all[0, idx], 0])   # outer diameter of inner bearing ring of bearing E in mm
    setattr(gearbox.bearings_3, 'd_1_F', d_1_ctlg[poss_all[1, idx], 0])   # outer diameter of inner bearing ring of bearing F in mm
    setattr(gearbox.bearings_3, 'ID_E', name_ctlg[poss_all[0, idx]])      # name of bearing E from bearing catalog
    setattr(gearbox.bearings_3, 'ID_F', name_ctlg[poss_all[1, idx]])      # name of bearing F from bearing catalog

    if gearbox.Input.num_EM == 1:
        setattr(gearbox.differential, 'd_diffcage', d_diffcage)         # Diameter of differential cage in mm
        # noinspection PyUnboundLocalVariable
        setattr(gearbox.differential, 'd_bev_l', d_bev_l)               # Diameter of larger bevel gears in mm
        # noinspection PyUnboundLocalVariable
        setattr(gearbox.differential, 'd_bev_s', d_bev_s)                # Diameter of smaller bevel gears in mm
        # noinspection PyUnboundLocalVariable
        setattr(gearbox.differential, 'b_bev', b_bev)                   # Width of bevel gearing in mm
    else:
        setattr(gearbox.differential, 'd_diffcage', gearbox.bearings_3.d_1_E)   # Substitute diameter for plotfunction in mm
    # endregion

    return gearbox
