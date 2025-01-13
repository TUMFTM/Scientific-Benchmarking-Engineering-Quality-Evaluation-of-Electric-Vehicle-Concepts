"""
Description:    This function computes calculation factors for the determination of the
                gears' safety coefficients for planetary gearboxes according to Decker, from p. 148
------------
Sources:    (1) DIN 3990-1, "Tragfaehigkeitsberechnung von Stirnraedern", 1987
            (2) Decker and Kabus, "Maschinenelemente - Formeln", Carl Hanser Verlag, 2011, ISBN: 978-3-446-42990-1
            (3) Niemann and Winter, "Maschinenelemente - Band 2: Getriebe allgemein, Zahnradgetriebe", Springer Verlag, 2003, ISBN: 978-3-662-11874-0
            (4) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
         shaft: denotes which shaft is being considered
------------
Output:  A series of calculation factors required for the sizing of the gears and shafts
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


def calc_factors_plan(gearbox, parameters, shaft):
    # region [1]: Initialization of required values
    # Gearbox Values
    T_max = 1/3*gearbox.Input.T_max*1000                # Maximum torque of el. motor [Nmm]
    n_nom = gearbox.Input.n_nom                         # Nominal engine speed [rpm]

    if shaft == 1:
        alpha_t = gearbox.gears_12.alpha_t_1            # Pressure angle in transverse section of first stage [rad]
        beta = gearbox.gears_12.beta_1                  # Helix angle of first stage [rad]
        m_n = gearbox.gears_12.m_n_1                    # Normal module of first stage [mm]
        b = gearbox.gears_12.b_1                        # Width of wheel 1&2 [mm]
        z_1 = gearbox.gears_12.z_1                      # Number of teeth of wheel 1 [-]
        d_1 = gearbox.gears_12.d_1                      # Pitch diameter of wheel 1 [mm]
        d_a1 = gearbox.gears_12.d_a1                    # Outside diameter of wheel 1 [mm]
        d_a2 = gearbox.gears_12.d_ap1                   # Outside diameter of first planet [mm]
        d_b1 = gearbox.gears_12.d_b1                    # Base diameter of wheel 1 [mm]
        d_b2 = gearbox.gears_12.d_bp1                   # Base diameter of first planet [mm]
        alpha_wt = gearbox.gears_12.alpha_wt_1          # Working transverse pressure angle of first stage[rad]

        i_12 = gearbox.results.i_1p1                    # Transmission ratio between sun shaft and first planet [-]
    else:
        alpha_t = gearbox.gears_12.alpha_t_2            # Pressure angle in transverse section of second stage [rad]
        beta = gearbox.gears_12.beta_2                  # Helix angle of second stage [rad]
        m_n = gearbox.gears_12.m_n_2                    # Normal module of stage 2 [mm]
        b = gearbox.gears_12.b_2                        # Width of planet 2 [mm]
        z_1 = gearbox.gears_12.z_p2                     # Number of teeth of planet 2 [-]
        d_1 = gearbox.gears_12.d_p2                     # Pitch diameter of planet 2 [mm]
        d_a1 = gearbox.gears_12.d_ap2                   # Outside diameter of planet 2 [mm]
        d_a2 = gearbox.gears_12.d_a2                    # Inside diameter of ring gear [mm]
        d_b1 = gearbox.gears_12.d_bp2                   # Base diameter of planet 2 [mm]
        d_b2 = gearbox.gears_12.d_b2                    # Base diameter of ring gear [mm]
        alpha_wt = gearbox.gears_12.alpha_wt_2          # Working transverse pressure angle of second stage [rad]

        i_1p1 = gearbox.results.i_1p1                   # Stationary gear ratio of the planetary transmission [-]
        i_1s = gearbox.results.i_1s                     # Total transmission of the gearbox [-]
        i_12 = gearbox.results.i_p22                    # Transmission ratio between sun and first planet [-]

        n_nom = n_nom/i_1p1*(1-1/i_1s)                  # Nominal speed of the planets [rpm]
        T_max = T_max*i_1p1                             # Maximum torque of the planets [Nmm]

    # Parameters
    alpha_n = parameters.gearbox.GearingConst.alpha_n   # Normal pressure angle [rad] --> 20deg
    K_app = parameters.gearbox.CalcFactors.K_app        # Application factor for static strength verification (DIN 3990-1, p.55) [-]
    K_1 = parameters.gearbox.CalcFactors.K_1            # Factor for calculation of dynamic factor K_v (DIN 3990-1, p. 18) [-]
    K_2 = parameters.gearbox.CalcFactors.K_2            # Factor for calculation of dynamic factor K_v (DIN 3990-1, p. 18) [-]
    c_gamma = parameters.gearbox.MatProp.c_gamma        # Mesh stiffness steel/steel (Decker, p. 148) [N/mm*mym]
    # endregion

    # region [2]: Calculation of calculation factors for safety coefficients
    # Calculation of base helix angle in rad (Decker, p. 133)
    beta_b = math.acos(math.sin(alpha_n)/math.sin(alpha_t))

    # Definition of root clearance in mm (Decker, p. 133)
    c = 0.25*m_n

    # Distance between planetary axle and main gearbox axle
    a = (gearbox.gears_12.d_1+gearbox.gears_12.d_p1)/2

    # Determination of dynamic factor K_v according to Decker, p. 148
    v = ((d_1/1000)*math.pi)*(n_nom/60)                 # circumferential speed in tooth contact point [m/s]
    F_n_t = 2*T_max/d_1                                 # circumferential tooth force [N]
    K_v = 1+((K_1/(K_app*F_n_t/b))+K_2)*((z_1*v/100)*math.sqrt(math.pow(i_12, 2)/(1+math.pow(i_12, 2))))

    # Determination of width factors K_h_beta (flank) und K_f_beta (root) (Decker, pp. 149)
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

    # Approximated flank line deviation in mym (Niemann and Winter, p. 324)
    if F_n_t/b < 200:
        if b < 20:
            f_sh = 5
        elif b < 40:
            f_sh = 6.5
        else:            # Width always smaller than 100 mm!
            f_sh = 7
    elif F_n_t/b < 1000:
        if b < 20:
            f_sh = 6
        elif b < 40:
            f_sh = 7
        else:
            f_sh = 8
    else:
        if b < 20:
            f_sh = 10
        elif b < 40:
            f_sh = 13
        else:
            f_sh = 18

    # Effective flank line deviation before running-in in mym (Decker, p. 149)
    F_beta_x = (1.33*f_sh)+f_h_beta
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
    N_f = math.pow((b/h), 2)/(1+(b/h)+(math.pow((b/h), 2)))
    K_f_beta = math.pow(K_h_beta, N_f)

    # Definition of transverse factors K_f_alpha and K_h_alpha (Decker, pp. 149)
    # Decisive transverse circumferential force in N
    F_t_h = F_n_t*K_v*K_app*K_h_beta
    # Permitted base-pitch deviation from table (Zaehringer, p. xii)
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

    # Running-in value y_alpha (Zaehringer, p. 45)
    y_alpha = 0.075*f_pe

    # Calculation of Total overlap
    p_et = m_n*math.pi*math.cos(alpha_t)/math.cos(beta)           # transverse normal base pitch (Decker, p. 135)
    # Transverse contact ratio (Decker, p. 136)
    if shaft == 1:
        epsilon_alpha = (math.sqrt(math.pow(d_a1, 2)-math.pow(d_b1, 2)) +
                         math.sqrt(math.pow(d_a2, 2)-math.pow(d_b2, 2))-(2*a*math.sin(alpha_wt)))/(2*p_et)
    else:
        epsilon_alpha = (math.sqrt(math.pow(d_a1, 2)-math.pow(d_b1, 2)) -
                         math.sqrt(math.pow(d_a2, 2)-math.pow(d_b2, 2))-(2*(-a)*math.sin(alpha_wt)))/(2*p_et)

    epsilon_beta = b*math.sin(beta)/(m_n*math.pi)       # overlap ratio (Decker, p. 136)
    epsilon_gamma = epsilon_beta+epsilon_alpha          # total overlap (Decker, p. 136)

    # Boundary condition for tooth root and pitting load capacity K_f_alpha and K_h_alpha (Decker, p.150)
    if epsilon_gamma > 2:
        K_f_alpha = 0.9+(0.4*(math.sqrt((2*(epsilon_gamma-1))/epsilon_gamma)*(c_gamma*(f_pe-y_alpha)/(F_t_h/b))))
        K_h_alpha = K_f_alpha
    else:
        K_f_alpha = (epsilon_gamma/2)*(0.9+(0.4*(c_gamma*(f_pe-y_alpha)/(F_t_h/b))))
        K_h_alpha = K_f_alpha

    # Overlap factor for tooth root load capacity (Decker, p. 150)
    Y_epsilon = 0.25+(0.75/(epsilon_alpha/math.pow(math.cos(beta_b), 2)))

    # Overlap factor for calculation of Z_epsilon (Decker, p. 150)
    # (epsilon_beta is set to one for the calculation, if > 1)
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
    else:
        setattr(gearbox.gears_12, 'beta_b_2', beta_b)               # Base helix angle of second stage in rad

        setattr(gearbox.factors, 'K_v_2', K_v)                       # Dynamic factor for second stage
        setattr(gearbox.factors, 'K_h_beta_2', K_h_beta)             # Flank width factor for second stage
        setattr(gearbox.factors, 'K_h_alpha_2', K_h_alpha)           # Boundary condition for pitting load capacity for second stage
        setattr(gearbox.factors, 'K_f_beta_2', K_f_beta)             # Width factor for root load capacity for second stage
        setattr(gearbox.factors, 'K_f_alpha_2', K_f_alpha)           # Boundary condition for tooth root load capacity for second stage
        setattr(gearbox.factors, 'Y_epsilon_2', Y_epsilon)           # Overlap factor for tooth root load capacity for second stage
        setattr(gearbox.factors, 'Z_epsilon_2', Z_epsilon)           # Overlap factor for pitting load capacity for second stage
        setattr(gearbox.factors, 'epsilon_beta_2', epsilon_beta)     # Overlap factor for second stage
        setattr(gearbox.factors, 'epsilon_alpha_2', epsilon_alpha)   # Transverse contact ratio of second stage
        setattr(gearbox.factors, 'F_n_t_2', F_n_t)                   # Circumferential tooth force of second stage [N]
    # endregion

    return gearbox
