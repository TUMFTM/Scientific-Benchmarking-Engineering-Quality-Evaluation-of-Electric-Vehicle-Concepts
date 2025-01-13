"""
Description:    This function computes the safety factor against flank break for planetary gearboxes, according to Decker, starting p. 151
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
Output:  Safety factor against flank break for first and second stage
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of safety factors against flank break
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
# Import classes
# Import methods
# endregion


def calc_S_H_plan(gearbox, parameters, shaft):
    # region [1]: Initialization of required values
    # Parameters
    K_app = parameters.gearbox.CalcFactors.K_app        # Application factor for static strength verification (DIN 3990-1, p.55) [-]
    Z_E = parameters.gearbox.CalcFactors.Z_E            # Elasticity factor for material combination steel/steel (Decker, p. 151) [(N/mm^2)^1/2]
    sigma_Hlim = parameters.gearbox.MatProp.sigma_Hlim  # Fatigue strength against gear flank pressure 16MnCr5 (Zaehringer, p. xiv) [N/mm^2]

    # Gearbox Values
    if shaft == 1:
        i_12 = gearbox.results.i_1p1                    # Transmission ratio of first stage [-]

        beta = gearbox.gears_12.beta_1                  # Helix angle of first stage [rad]
        beta_b = gearbox.gears_12.beta_b_1              # Base helix angle of first stage [rad]
        alpha_t = gearbox.gears_12.alpha_t_1            # Pressure angle in transverse section of first stage [rad]
        alpha_wt = gearbox.gears_12.alpha_wt_1          # Working transverse pressure angle of first stage [rad]
        b = gearbox.gears_12.b_1                        # Width of first wheel [mm]
        d_1 = gearbox.gears_12.d_1                      # Pitch diameter of sun gear [mm]

        Z_epsilon = gearbox.factors.Z_epsilon_1         # Overlap factor for pitting load capacity for first stage [-]
        K_v = gearbox.factors.K_v_1                     # Dynamic factor for first stage [-]
        F_n_t = gearbox.factors.F_n_t_1                 # Circumferential tooth force of first stage [N]
        K_h_beta = gearbox.factors.K_h_beta_1           # Flank width factor for first stage [-]
        K_h_alpha = gearbox.factors.K_h_alpha_1         # Boundary condition for pitting load capacity for first stage [-]
    else:
        i_12 = abs(gearbox.results.i_p22)               # Transmission ratio of second stage [-]

        beta = gearbox.gears_12.beta_2                  # Helix angle of second stage [rad]
        beta_b = gearbox.gears_12.beta_b_2              # Base helix angle of second stage [rad]
        alpha_t = gearbox.gears_12.alpha_t_2            # Pressure angle in transverse section of second stage [rad]
        alpha_wt = gearbox.gears_12.alpha_wt_2          # Working transverse pressure angle of second stage [rad]
        b = gearbox.gears_12.b_2                        # Width of planet 2 [mm]
        d_1 = gearbox.gears_12.d_p2                     # Pitch diameter of planet 2 [mm]

        Z_epsilon = gearbox.factors.Z_epsilon_2         # Overlap factor for pitting load capacity for second stage [-]
        K_v = gearbox.factors.K_v_2                     # Dynamic factor for second stage [-]
        F_n_t = gearbox.factors.F_n_t_2                 # Circumferential tooth force of second stage [N]
        K_h_beta = gearbox.factors.K_h_beta_2           # Flank width factor for second stage [-]
        K_h_alpha = gearbox.factors.K_h_alpha_2         # Boundary condition for pitting load capacity for second stage [-]
    # endregion

    # region [2]: Calculation of safety factors against flank break
    # Zone coefficient (Decker, p. 151)
    Z_h = math.sqrt((2*math.cos(beta_b))/(math.pow(math.cos(alpha_t), 2)*math.tan(alpha_wt)))

    # Helix angle factor (Decker, p. 151)
    Z_beta = math.sqrt(math.cos(beta))

    # Nominal tooth pressure (Decker, p.151)
    sigma_h0 = math.sqrt(((i_12+1)/i_12)*(F_n_t/(d_1*b)))*Z_h*Z_E*Z_epsilon*Z_beta

    # Decisive tooth pressure (Decker, p.152) (Z_B = 1)
    sigma_h = sigma_h0*math.sqrt(K_app*K_v*K_h_beta*K_h_alpha)

    # Safety factor against flank break with Z_NT = 1.6 (Zaehringer, p. xv)
    S_H = sigma_Hlim*1.6/sigma_h
    # endregion

    # region [3]:  Output Assignment
    if shaft == 1:
        setattr(gearbox.results, 'S_H_1p1', S_H)      # Safety factor against flank break for first stage
    else:
        setattr(gearbox.results, 'S_H_p22', S_H)      # Safety factor against flank break for second stage
    # endregion

    return gearbox
