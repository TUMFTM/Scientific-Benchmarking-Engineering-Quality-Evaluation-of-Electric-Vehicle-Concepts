"""
Description:    This function computes calculation factors for the determination of the
                gears' safety coefficients according to Decker, starting p. 148
------------
Sources:    (1) DIN 3990-1, "Tragfaehigkeitsberechnung von Stirnraedern", 1987
            (2) Decker and Kabus, "Maschinenelemente - Formeln", Carl Hanser Verlag, 2011, ISBN: 978-3-446-42990-1
            (3) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
            (4) Wittel et al., "Roloff/Matek Maschinenelemente", Springer Vieweg, 2013, ISBN: 978-3-658-02327-0
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
         shaft: denotes which reduction stage is being considered (1 or 2; for the differential shaft a different calculation is used)
------------
Output:  Dimensioning of all elements on the first shaft (gears, shaft, bearings)
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of calculation factors for safety coefficients
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
# Import classes
# Import methods
# endregion


def calc_factors(gearbox, parameters, shaft):
    # region [1]: Initialization of required values
    # Parameters
    K_app = parameters.gearbox.CalcFactors.K_app        # Application factor for static strength verification (DIN 3990-1, p.55) [-]
    K_1 = parameters.gearbox.CalcFactors.K_1            # Factor for calculation of dynamic factor K_v (DIN 3990-1, p. 18) [-]
    K_2 = parameters.gearbox.CalcFactors.K_2            # Factor for calculation of dynamic factor K_v (DIN 3990-1, p. 18) [-]
    alpha_n = parameters.gearbox.GearingConst.alpha_n   # Normal pressure angle [rad] --> 20deg
    c_gamma = parameters.gearbox.MatProp.c_gamma        # Mesh stiffness steel/steel (Decker, p. 148) [N/mm*mym]

    # Gearbox Values
    if shaft == 1:
        n_nom = gearbox.Input.n_nom                    # Nominal engine speed [rpm]
        T_max = gearbox.Input.T_max*1000               # Maximum torque of el. motor [Nmm]

        m_n = gearbox.gears_12.m_n_1                   # Normal module of first stage [mm]
        b = gearbox.gears_12.b_1                       # Width of wheel 1&2 [mm]
        beta = gearbox.gears_12.beta_1                 # Helix angle of gearing of first stage [rad]
        alpha_t = gearbox.gears_12.alpha_t_1           # Pressure angle in transverse section of first stage [rad]
        alpha_wt = gearbox.gears_12.alpha_wt_1         # Working transverse pressure angle of first stage [rad]
        z_1 = gearbox.gears_12.z_1                     # Number of teeth of wheel 1 [-]
        d_1 = gearbox.gears_12.d_1                     # Pitch diameter of wheel 1 [mm]
        d_a1 = gearbox.gears_12.d_a1                   # Outside diameter of wheel 1 [mm]
        d_a2 = gearbox.gears_12.d_a2                   # Outside diameter of wheel 2 [mm]
        d_b1 = gearbox.gears_12.d_b1                   # Base diameter of wheel 1 [mm]
        d_b2 = gearbox.gears_12.d_b2                   # Base diameter of wheel 2 [mm]
        # Selection of the shaft diameter at pinion in mm, assumption: pinion is part of the shaft (Zaehringer, p 43)
        d_sh_r = gearbox.gears_12.d_f1

        a = gearbox.results.a_12                       # Distance between shafts 1&2 [mm]
        i_12 = gearbox.results.i_12                    # Transmission ratio of first stage [-]

        length = gearbox.bearings_1.l_1                # Distance between bearings on shaft 1 [mm]
        s = gearbox.bearings_1.s_1                     # Distance between force application point and middle of bearings on shaft 1 [mm]

        K_prime = 0.48                                 # Factor for consideration of bearings on shaft 1 (Zaehringer, p. xi) [-]

    else:  # shaft == 2:
        T_max = gearbox.Input.T_max*1000*gearbox.results.i_12      # Maximum torque of shaft 2 [Nmm]
        n_nom = gearbox.Input.n_nom/gearbox.results.i_12           # Nominal speed of shaft 2 [rpm]

        m_n = gearbox.gears_34.m_n_3                   # Normal module of second stage [mm]
        b = gearbox.gears_34.b_3                       # Width of wheel 3&4 [mm]
        beta = gearbox.gears_34.beta_2                 # Helix angle of gearing of second stage [rad]
        alpha_t = gearbox.gears_34.alpha_t_2           # Pressure angle in transverse section of second stage [rad]
        alpha_wt = gearbox.gears_34.alpha_wt_2         # Working transverse pressure angle of second stage [rad]
        z_1 = gearbox.gears_34.z_3                     # Number of teeth of wheel 3 [-]
        d_1 = gearbox.gears_34.d_3                     # Pitch diameter of wheel 3 [mm]
        d_a1 = gearbox.gears_34.d_a3                   # Outside diameter of wheel 3 [mm]
        d_a2 = gearbox.gears_34.d_a4                   # Outside diameter of wheel 4 [mm]
        d_b1 = gearbox.gears_34.d_b3                   # Base diameter of wheel 3 [mm]
        d_b2 = gearbox.gears_34.d_b4                   # Base diameter of wheel 4 [mm]
        # Selection of the shaft diameter at pinion in mm, assumption: pinion is part of the shaft (Zaehringer, p. 43)
        d_sh_r = gearbox.gears_34.d_f3

        a = gearbox.results.a_23  # Distance between shafts 2&3 [mm]
        i_12 = gearbox.results.i_34                    # Transmission ratio of first stage [-]

        length = gearbox.bearings_2.l_2                     # Distance between bearings on shaft 2 [mm]
        s = gearbox.bearings_2.s_3                     # Distance between force application point of wheel 3 and middle of bearings [mm]

        if gearbox.Input.axles.lower() != 'coaxial':
            K_prime = -0.6                             # Factor for consideration of bearings on shaft 2 (Zaehringer, p. xi) [-]
        else:
            K_prime = -0.36                            # Factor for consideration of bearings on shaft 2 (Zaehringer, p. xi) [-]
    # endregion

    # region [2]: Calculation of calculation factors for safety coefficients
    # Calculation of base helix angle in rad (Decker, p. 133)
    beta_b = math.acos(math.sin(alpha_n)/math.sin(alpha_t))

    # Definition of root clearance in mm (Decker, p. 133)
    c = 0.25*m_n

    # Determination of dynamic factor K_v (Decker, p. 148)
    v = ((d_1/1000)*math.pi)*(n_nom/60)                    # circumferential speed in tooth contact point [m/s]
    F_n_t = 2*T_max/d_1                                     # circumferential tooth force [N]
    K_v = 1+((K_1/(K_app*F_n_t/b))+K_2)*((z_1*v/100)*math.sqrt((math.pow(i_12, 2))/(1+(math.pow(i_12, 2)))))

    # Determination of width factors K_h_beta (flank) und K_f_beta (root) (Decker, p. 149/149)
    if b <= 20:
        f_h_beta = 8
    elif 20 < b <= 40:
        f_h_beta = 9
    elif 40 < b <= 100:
        f_h_beta = 10
    else:
        f_h_beta = 11

    # Average circumferential force at the pitch circle in N (Decker, p. 148)
    F_m = F_n_t*K_v*K_app

    # Flank line deviation in mym (Decker, p. 149)
    f_sh = (F_m/b)*0.023*(abs(0.7+(K_prime*length*s/(math.pow(d_1, 2)))*(math.pow((d_1/d_sh_r), 4)))+0.3) * (math.pow((b/d_1), 2))
    # Limit of flank line deviation set to 18 mym, (Roloff/Matek, p. 225 (Table 21/16))
    if f_sh > 18:
        f_sh = 18

    # Effective flank line deviation before running-in in mym (Decker, p. 149)
    F_beta_x = (1.33*f_sh) + f_h_beta
    # Running-in value in mym (with maximum of 6 mym) (Zaehringer, p. xii)
    y_beta = 0.15*F_beta_x
    if y_beta > 6:
        y_beta = 6

    # Effective flank line deviation after running-in in mym (Decker, p. 149)
    F_beta_y = F_beta_x-y_beta

    # Calculation of flank width factor K_h_beta (Decker, p. 148)
    par = (F_beta_y*c_gamma)/(2*F_m/b)     # auxiliary parameter for determination of K_h_beta
    if par >= 1:
        K_h_beta = math.sqrt((2*F_beta_y*c_gamma)/(F_m/b))
    else:
        K_h_beta = 1+(F_beta_y*c_gamma)/(2*F_m/b)

    # Calculation of width factor for root load capacity K_f_beta (Decker, p. 149)
    h = (2*m_n)+c                          # tooth height in mm (Decker, p.149)
    N_f = (math.pow((b/h), 2))/(1+(b/h)+(math.pow((b/h), 2)))
    K_f_beta = math.pow(K_h_beta, N_f)

    # Definition of transverse factors K_f_alpha and K_h_alpha (Decker, starting p. 149)
    # Decisive transverse circumferential force in N
    F_t_h = F_n_t*K_v*K_app*K_h_beta

    if d_1 <= 50:
        if m_n <= 3.55:
            f_pe = 7
        elif 3.55 < m_n <= 6:
            f_pe = 8
        else:
            f_pe = 10
    elif 50 < d_1 <= 125:
        if m_n <= 3.55:
            f_pe = 7
        elif 3.55 < m_n <= 6:
            f_pe = 9
        elif 6 < m_n <= 10:
            f_pe = 10
        else:
            f_pe = 12
    else:
        if m_n <= 3.55:
            f_pe = 8
        elif 3.55 < m_n <= 6:
            f_pe = 9
        elif 6 < m_n <= 10:
            f_pe = 11
        else:
            f_pe = 16
    # Running - in value y_alpha(Zaehringer, p.45)
    y_alpha = 0.075 * f_pe

    # Calculation of Total overlap
    p_et = m_n*math.pi*math.cos(alpha_t)/math.cos(beta)             # transverse normal base pitch (Decker, p. 135)
    # transverse contact ratio (Decker, p. 136)
    epsilon_alpha = (math.sqrt(math.pow(d_a1, 2)-(math.pow(d_b1, 2))) +
                     math.sqrt((math.pow(d_a2, 2))-(math.pow(d_b2, 2)))-(2*a*math.sin(alpha_wt)))/(2*p_et)
    epsilon_beta = b*math.sin(beta)/(m_n*math.pi)                   # overlap ratio (Decker, p. 136)
    epsilon_gamma = epsilon_beta+epsilon_alpha                      # total overlap (Decker, p. 136)

    # Boundary condition for tooth root and pitting load capacity K_f_alpha and K_h_alpha (Decker, p.150)
    if epsilon_gamma > 2:
        K_f_alpha = 0.9+(0.4*(math.sqrt((2*(epsilon_gamma-1))/epsilon_gamma)*(c_gamma*(f_pe-y_alpha)/(F_t_h/b))))
        K_h_alpha = K_f_alpha
    else:
        K_f_alpha = (epsilon_gamma/2)*(0.9+(0.4*(c_gamma*(f_pe-y_alpha)/(F_t_h/b))))
        K_h_alpha = K_f_alpha

    # Overlap factor for tooth root load capacity (Decker, p. 150)
    Y_epsilon = 0.25+(0.75/(epsilon_alpha/math.pow(math.cos(beta_b), 2)))

    # Overlap factor for calculation of Z_epsilon (Decker, p. 150) (epsilon_beta is set to one if >1)
    epsilon_beta_new = epsilon_beta
    if epsilon_beta_new > 1:
        epsilon_beta_new = 1

    # Overlap factor for pitting load capacity (Decker, p. 150)
    Z_epsilon = math.sqrt((((4-epsilon_alpha)/3)*(1-epsilon_beta_new))+(epsilon_beta_new/epsilon_alpha))
    # endregion

    # region [3]: Output Assignment
    if shaft == 1:
        setattr(gearbox.gears_12, 'beta_b_1', beta_b)               # Base helix angle of first stage in rad

        setattr(gearbox.factors, 'K_v_1', K_v)                      # Dynamic factor for first stage
        setattr(gearbox.factors, 'K_h_beta_1', K_h_beta)            # Flank width factor for first stage
        setattr(gearbox.factors, 'K_h_alpha_1', K_h_alpha)          # Boundary condition for pitting load capacity for first stage
        setattr(gearbox.factors, 'K_f_beta_1', K_f_beta)            # Width factor for root load capacity for first stage
        setattr(gearbox.factors, 'K_f_alpha_1', K_f_alpha)          # Boundary condition for tooth root load capacity for first stage
        setattr(gearbox.factors, 'Y_epsilon_1', Y_epsilon)          # Overlap factor for tooth root load capacity for first stage
        setattr(gearbox.factors, 'Z_epsilon_1', Z_epsilon)          # Overlap factor for pitting load capacity for first stage
        setattr(gearbox.factors, 'epsilon_beta_1', epsilon_beta)    # Overlap factor for first stage
        setattr(gearbox.factors, 'epsilon_alpha_1', epsilon_alpha)  # Transverse contact ratio of first stage
        setattr(gearbox.factors, 'F_n_t_1', F_n_t)                  # Circumferential tooth force of first stage [N]
    elif shaft == 2:
        setattr(gearbox.gears_34, 'beta_b_2', beta_b)               # Base helix angle of second stage in rad

        setattr(gearbox.factors, 'K_v_2', K_v)                      # Dynamic factor for second stage
        setattr(gearbox.factors, 'K_h_beta_2', K_h_beta)            # Flank width factor for second stage
        setattr(gearbox.factors, 'K_h_alpha_2', K_h_alpha)          # Boundary condition for pitting load capacity for second stage
        setattr(gearbox.factors, 'K_f_beta_2', K_f_beta)            # Width factor for root load capacity for second stage
        setattr(gearbox.factors, 'K_f_alpha_2', K_f_alpha)          # Boundary condition for tooth root load capacity for second stage
        setattr(gearbox.factors, 'Y_epsilon_2', Y_epsilon)          # Overlap factor for tooth root load capacity for second stage
        setattr(gearbox.factors, 'Z_epsilon_2', Z_epsilon)          # Overlap factor for pitting load capacity for second stage
        setattr(gearbox.factors, 'epsilon_beta_2', epsilon_beta)    # Overlap factor for second stage
        setattr(gearbox.factors, 'epsilon_alpha_2', epsilon_alpha)  # Transverse contact ratio of second stage
        setattr(gearbox.factors, 'F_n_t_2', F_n_t)                  # Circumferential tooth force of second stage [N]
    # endregion

    return gearbox
