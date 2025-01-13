"""
Description:    This function computes the safety factor against root break for planetary gearboxes according to Decker, p. 150
------------
Sources:    (1) Decker and Kabus, "Maschinenelemente - Formeln", Carl Hanser Verlag, 2011, ISBN: 978-3-446-42990-1
            (2) DIN 3990-1, "Tragfaehigkeitsberechnung von Stirnraedern", 1987
            (3) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
            (4) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
         shaft: denotes which reduction stage is being considered (1 or 2; for the differential shaft a different calculation is used)
------------
Output:  Safety factor against root break for first and second stage
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of safety factors against root break
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
# Import classes
# Import methods
# endregion


def calc_S_F_plan(gearbox, parameters, shaft):
    # region [1]: Initialization of required values
    # Parameters
    K_app = parameters.gearbox.CalcFactors.K_app        # Application factor for static strength verification (DIN 3990-1, p.55) [-]
    sigma_fe = parameters.gearbox.MatProp.sigma_fe      # Fatigue strength of 16MnCr5 (Zaehringer, p. xiv) [N/mm^2]

    # Gearbox Values
    if shaft == 1:
        beta = gearbox.gears_12.beta_1                  # Helix angle of first stage [rad]
        beta_b = gearbox.gears_12.beta_b_1              # Base helix angle of first stage [rad]
        z_1 = gearbox.gears_12.z_1                      # Number of teeth of sun gear [-]
        b = gearbox.gears_12.b_1                        # Width of sun gear [mm]
        m_n = gearbox.gears_12.m_n_1                    # Normal module of first stage [mm]

        epsilon_beta = gearbox.factors.epsilon_beta_1   # Overlap ratio of first stage [-]
        F_n_t = gearbox.factors.F_n_t_1                 # Circumferential tooth force of first stage [N]
        Y_epsilon = gearbox.factors.Y_epsilon_1         # Overlap factor for tooth root load capacity for first stage [-]
        K_v = gearbox.factors.K_v_1                     # Dynamic factor for first stage [-]
        K_f_beta = gearbox.factors.K_f_beta_1           # Width factor for root load capacity for first stage [-]
        K_f_alpha = gearbox.factors.K_f_alpha_1         # Boundary condition for tooth root load capacity for first stage [-]

    else:  # if shaft == 2
        beta = gearbox.gears_12.beta_2                  # Helix angle of second stage [rad]
        beta_b = gearbox.gears_12.beta_b_2              # Base helix angle of second stage [rad]
        z_1 = gearbox.gears_12.z_p2                     # Number of teeth of planet 2 [-]
        b = gearbox.gears_12.b_2                        # Width of planet 2 [mm]
        m_n = gearbox.gears_12.m_n_2                    # Normal module of second stage [mm]

        epsilon_beta = gearbox.factors.epsilon_beta_2   # Overlap ratio of second stage [-]
        F_n_t = gearbox.factors.F_n_t_2                 # Circumferential tooth force of second stage [N]
        Y_epsilon = gearbox.factors.Y_epsilon_2         # Overlap factor for tooth root load capacity for second stage [-]
        K_v = gearbox.factors.K_v_2                     # Dynamic factor for second stage [-]
        K_f_beta = gearbox.factors.K_f_beta_2           # Width factor for root load capacity for second stage [-]
        K_f_alpha = gearbox.factors.K_f_alpha_2         # Boundary condition for tooth root load capacity for second stage [-]
    # endregion

    # region [2]: Calculation of safety factors against root break
    # Substitute number of teeth (Decker, p. 133)
    z_n = z_1/(math.pow(math.cos(beta_b), 2)*math.cos(beta))
    # Determination of helix angle factor (Decker, p. 150)
    # (overlap ratio set to 1 for the calculation if >1)
    if epsilon_beta > 1:
        epsilon_beta = 1

    Y_beta = 1-(epsilon_beta*((beta*180/math.pi)/120))

    # Form factor depending on substitute number of teeth for a profile modification of 0 (Zaehringer, p. xiii)
    if z_n < 15:
        Y_Fa = 3.36
    elif 15 <= z_n < 16:
        Y_Fa = 3.25
    elif 16 <= z_n < 17:
        Y_Fa = 3.16
    elif 17 <= z_n < 18:
        Y_Fa = 3.09
    elif 18 <= z_n < 19:
        Y_Fa = 3.02
    elif 19 <= z_n < 20:
        Y_Fa = 2.96
    elif 20 <= z_n < 21:
        Y_Fa = 2.91
    elif 21 <= z_n < 22:
        Y_Fa = 2.87
    elif 22 <= z_n < 23:
        Y_Fa = 2.83
    elif 23 <= z_n < 24:
        Y_Fa = 2.80
    elif 24 <= z_n < 25:
        Y_Fa = 2.75
    elif 25 <= z_n < 30:
        Y_Fa = 2.72
    elif 30 <= z_n < 40:
        Y_Fa = 2.60
    elif 40 <= z_n < 50:
        Y_Fa = 2.45
    elif 50 <= z_n < 60:
        Y_Fa = 2.36
    elif 60 <= z_n < 100:
        Y_Fa = 2.32
    elif 100 <= z_n < 200:
        Y_Fa = 2.21
    elif 200 <= z_n < 400:
        Y_Fa = 2.14
    else:
        Y_Fa = 2.10

    # Stress coefficient (Zaehringer, p. xiv)
    if z_n < 18:
        Y_Sa = 1.57
    elif 18 <= z_n < 19:
        Y_Sa = 1.58
    elif 19 <= z_n < 20:
        Y_Sa = 1.59
    elif 20 <= z_n < 22:
        Y_Sa = 1.60
    elif 22 <= z_n < 24:
        Y_Sa = 1.63
    elif 24 <= z_n < 26:
        Y_Sa = 1.64
    elif 26 <= z_n < 28:
        Y_Sa = 1.66
    elif 28 <= z_n < 30:
        Y_Sa = 1.68
    elif 30 <= z_n < 35:
        Y_Sa = 1.69
    elif 35 <= z_n < 40:
        Y_Sa = 1.73
    elif 40 <= z_n < 45:
        Y_Sa = 1.75
    elif 45 <= z_n < 50:
        Y_Sa = 1.78
    elif 50 <= z_n < 60:
        Y_Sa = 1.80
    elif 60 <= z_n < 70:
        Y_Sa = 1.84
    elif 70 <= z_n < 80:
        Y_Sa = 1.87
    elif 80 <= z_n < 100:
        Y_Sa = 1.90
    elif 100 <= z_n < 150:
        Y_Sa = 1.94
    elif 150 <= z_n < 200:
        Y_Sa = 2.02
    elif 200 <= z_n < 400:
        Y_Sa = 2.06
    else:
        Y_Sa = 2.17

    # Calculation of the root stresses and safety factor (Decker, p. 150)
    # Root nominal stress in N/mm^2
    sigma_f_0 = (F_n_t/(b*m_n))*Y_Fa*Y_Sa*Y_beta*Y_epsilon
    # Root stress in N/mm^2
    sigma_f = (((sigma_f_0*K_app)*K_v)*K_f_beta)*K_f_alpha
    # Safety factor against against root break with Y_NT = 1.8 (Zaehringer, p. xv)
    S_F = sigma_fe*1.8/sigma_f
    # endregion

    # region [3]: Output Assignment
    if shaft == 1:
        setattr(gearbox.results, 'S_F_1p1', S_F)       # Safety factor against root break for first stage
    else:  # if shaft == 2
        setattr(gearbox.results, 'S_F_p22', S_F)       # Safety factor against root break for second stage
    # endregion

    return gearbox
