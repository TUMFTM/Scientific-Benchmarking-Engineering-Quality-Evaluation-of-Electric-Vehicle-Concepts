"""
Description:    This function computes the number of teeth according to the chosen transmission ratios and calculates the wheels' dimensions.
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
            (2) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
            (3) Decker and Kabus, "Maschinenelemente - Formeln", Carl Hanser Verlag, 2011, ISBN: 978-3-446-42990-1
            (4) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
            (5) Mueller, "Die Umlaufgetriebe", Springer Verlag, 1998, ISBN: 978-3-642-58725-2
            (6) K. Stahl, Documentation Lecture "Maschinenelemente", TUM, 2015/2016
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  Dimensions of the gearbox gears
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of Wheel dimensions
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
import numpy as np
# Import classes
# Import methods
# endregion


def calc_wheel_data_plan(gearbox, parameters):
    # region [1]: Initialization of required values
    # Gearbox Values
    i_tot = gearbox.Input.i_tot         # Desired total transmission ratio

    i_1p1 = gearbox.results.i_1p1       # Desired transmission ratio between sun shaft and first planet
    i_p22 = gearbox.results.i_p22       # Desired transmission ratio between second planet and ring gear

    m_n_1 = gearbox.gears_12.m_n_1      # Normal module of first stage (sun - planet 1) [mm]
    b_1 = gearbox.gears_12.b_1          # Width of first stage gears [mm]
    b_2 = gearbox.gears_12.b_2          # Width of second stage gears [mm]

    d_sh_3 = gearbox.shafts.d_sh_3      # Diameter of output shaft [mm]

    # Parameters
    epsilon_beta = parameters.gearbox.GearingConst.epsilon_beta   # Desired overlap ratio [-]
    alpha_n = parameters.gearbox.GearingConst.alpha_n             # Normal pressure angle [rad] --> 20deg
    # endregion

    # region [2]: Calculation of gearing data
    # Calculation of helix angles of first stage in rad (Decker, p. 136)
    beta_1 = math.asin((epsilon_beta*m_n_1*math.pi)/b_1)
    if beta_1 > math.pi/6:
        b_1 = epsilon_beta*m_n_1*math.pi/math.sin(math.pi/6)
        beta_1 = math.asin((epsilon_beta*m_n_1*math.pi)/b_1)
    elif beta_1 < math.pi/9:
        b_1 = epsilon_beta*m_n_1*math.pi/math.sin(math.pi/9)
        beta_1 = math.asin((epsilon_beta*m_n_1*math.pi)/b_1)

    # Calculation of pressure angle in transverse section of first stage in rad (Decker, p. 132)
    alpha_t_1 = math.atan(math.tan(alpha_n)/math.cos(beta_1))

    # Definition of root clearance (Decker, p. 133)
    c_1 = 0.25*m_n_1

    # Pitch diameter of sun gear with current normal module in mm (Koehler [2], p. 57)
    d_1 = d_sh_3+4+8+2*4.25*m_n_1    # 2 mm gap between output shaft and hollow sun shaft, 4 mm space for profile shaft

    if gearbox.Input.manTR == 0:
        # Definition of desired stationary gear ratio (Mueller, p. 35)
        i_0 = 1-i_tot

        # Calculation of the number of teeth for automatic selection (Decker, p.135)
        z_1 = d_1*math.cos(beta_1)/m_n_1
        z_1 = math.ceil(z_1)
        # Pressure angle in transverse section (Decker, p. 132) [rad]
        alpha_t_1 = math.atan(math.tan(alpha_n)/math.cos(beta_1))
        # Base helix angle (Decker, p. 133) [rad]
        beta_b_1 = math.acos(math.sin(alpha_n)/math.sin(alpha_t_1))

        # Substitute teeth number (Decker, p. 133)
        z_n = z_1/(math.pow(math.cos(beta_b_1), 2)*math.cos(beta_1))
        # Minimum number of teeth (Decker, p. 135)
        if z_n < 17:
            z_1 = math.ceil(17*math.pow(math.cos(beta_b_1), 2)*math.cos(beta_1))

        # Number of teeth of planet 1
        z_p1 = round(z_1*i_1p1)

        # Number of teeth of second stage with empirical module-stage-ratio
        # (m_n_2/m_n_1 --> 0.73) (Koehler [2], p. 57)
        z_p2 = math.floor(0.73*abs((z_1+z_p1)/(1+i_p22)))
        # Check if number of teeth is greater than minimum
        if z_p2 < 15:
            z_p2 = 15

        # Number of teeth of ring gear
        z_2 = round(z_p2*i_p22)

        # Confirmation that the normal module of the second stage is larger or
        # equal to the first stage
        while abs(z_p2+z_2) > z_1+z_p1:
            z_1 = z_1+1
            z_p1 = round(z_1*i_1p1)
            z_2 = round(z_p2*i_0/(z_p1/z_1))

        # Check for number of planet condition (Mueller, p. 239)
        z_stage2 = np.array([z_p2, z_2])
        n = np.outer(np.ones((9, 1)), z_stage2)
        if z_1 % 3 != 0 and z_p2 % 3 != 0:
            n[3, 0] += 1
            n[4, 0] -= 1
            n[5, 0] += 1
            n[6, 0] -= 1
            n[7, 0] += 1
            n[8, 0] -= 1
        if z_p1 % 3 != 0 and z_2 % 3 != 0:
            n[1, 1] -= 1
            n[2, 1] += 1
            n[5, 1] -= 1
            n[6, 1] += 1
            n[7, 1] += 1
            n[8, 1] -= 1

        N = np.mod(np.absolute(z_p1*n[:, 1])+np.absolute(z_1*n[:, 0]), 3)
        N_idx = np.asarray(np.where(N == 0))
        z_p2 = n[N_idx[0][0], 0]
        z_2 = n[N_idx[0][0], 1]

    else:
        z_1 = gearbox.gears_12.z_1
        z_p1 = gearbox.gears_12.z_p1
        z_p2 = gearbox.gears_12.z_p2
        z_2 = gearbox.gears_12.z_2

    # Updated transmission ratios according to number of teeth
    i_1p1 = z_p1/z_1
    i_p22 = z_2/z_p2
    i_0 = i_1p1*i_p22
    i_1s = 1-i_0
    i_p_rel = (math.pow(i_0, 2)-1)/(2*i_0)

    # Normal module of stage 2 according to stepped planet condition (Mueller, p. 232)
    m_n_2 = m_n_1*abs((z_1+z_p1)/(z_2+z_p2))
    c_2 = 0.25*m_n_2

    # Calculation of helix angles of second stage in rad (Decker, p. 136)
    beta_2 = math.asin((epsilon_beta*m_n_2*math.pi)/b_2)
    if beta_2 > math.pi/6:
        b_2 = epsilon_beta*m_n_2*math.pi/math.sin(math.pi/6)
        beta_2 = math.asin((epsilon_beta*m_n_2*math.pi)/b_2)
    elif beta_1 < math.pi/9:
        b_2 = epsilon_beta*m_n_2*math.pi/math.sin(math.pi/9)
        beta_2 = math.asin((epsilon_beta*m_n_2*math.pi)/b_2)

    # Calculation of pressure angle in transverse section of second stage in rad (Decker, p. 132)
    alpha_t_2 = math.atan(math.tan(alpha_n)/math.cos(beta_2))

    # Pitch diameters of all wheels in mm (Decker, p.132)
    d_1 = z_1*m_n_1/math.cos(beta_1)
    d_p1 = z_p1*m_n_1/math.cos(beta_1)
    d_p2 = z_p2*m_n_2/math.cos(beta_2)
    d_2 = -z_2*m_n_2/math.cos(beta_2)

    # Calculation of outside, root and base diameters of all gears (Stahl, p. 106)
    d_a1 = d_1+(2*m_n_1)
    d_ap1 = d_p1+(2*m_n_1)
    d_ap2 = d_p2+(2*m_n_2)
    d_a2 = d_2-(2*m_n_2)

    d_f1 = d_1-(2*(m_n_1+c_1))
    d_fp1 = d_p1-(2*(m_n_1+c_1))
    d_fp2 = d_p2-(2*(m_n_2+c_2))
    d_f2 = d_2+(2*(m_n_2+c_2))

    d_b1 = d_1*math.cos(alpha_t_1)
    d_bp1 = d_p1*math.cos(alpha_t_1)
    d_bp2 = d_p2*math.cos(alpha_t_2)
    d_b2 = d_2*math.cos(alpha_t_2)

    # Diameter of planet circle in mm
    d_s = d_1+d_p1
    # endregion

    # region [3]: Output Assignment
    setattr(gearbox.gears_12, 'beta_1', beta_1)          # Helix angle of first stage gears in rad
    setattr(gearbox.gears_12, 'alpha_t_1', alpha_t_1)    # Pressure angle in transverse section of first stage in rad
    setattr(gearbox.gears_12, 'd_1', d_1)                # Pitch diameter of sun gear in mm
    setattr(gearbox.gears_12, 'd_a1', d_a1)              # Outside diameter of sun gear in mm
    setattr(gearbox.gears_12, 'd_f1', d_f1)              # Root diameter of sun gear in mm
    setattr(gearbox.gears_12, 'd_b1', d_b1)              # Base diameter of sun gear in mm
    setattr(gearbox.gears_12, 'z_1', z_1)                # Number of teeth of sun gear
    setattr(gearbox.gears_12, 'd_p1', d_p1)              # Pitch diameter of planet 1 in mm
    setattr(gearbox.gears_12, 'd_ap1', d_ap1)            # Outside diameter of planet 1 in mm
    setattr(gearbox.gears_12, 'd_fp1', d_fp1)            # Root diameter of planet 1 in mm
    setattr(gearbox.gears_12, 'd_bp1', d_bp1)            # Base diameter of planet 1 in mm
    setattr(gearbox.gears_12, 'z_p1', z_p1)              # Number of teeth of planet 1
    setattr(gearbox.gears_12, 'beta_2', beta_2)          # Helix angle of second stage gears in rad
    setattr(gearbox.gears_12, 'alpha_t_2', alpha_t_2)    # Pressure angle in transverse section of second stage in rad
    setattr(gearbox.gears_12, 'm_n_2', m_n_2)            # Normal module of stage 2 in mm
    setattr(gearbox.gears_12, 'd_p2', d_p2)              # Pitch diameter of planet 2 in mm
    setattr(gearbox.gears_12, 'd_ap2', d_ap2)            # Outside diameter of planet 2 in mm
    setattr(gearbox.gears_12, 'd_fp2', d_fp2)            # Root diameter of planet 2 in mm
    setattr(gearbox.gears_12, 'd_bp2', d_bp2)            # Base diameter of planet 2 in mm
    setattr(gearbox.gears_12, 'z_p2', z_p2)              # Number of teeth of planet 2
    setattr(gearbox.gears_12, 'd_2', d_2)                # Pitch diameter of ring gear in mm
    setattr(gearbox.gears_12, 'd_a2', d_a2)              # Inside diameter of ring gear in mm
    setattr(gearbox.gears_12, 'd_f2', d_f2)              # Root diameter of ring gear in mm
    setattr(gearbox.gears_12, 'd_b2', d_b2)              # Base diameter of ring gear in mm
    setattr(gearbox.gears_12, 'z_2', z_2)                # Number of teeth of ring gear (negative)
    setattr(gearbox.gears_12, 'd_s', d_s)               # Diameter of planet circle in mm

    setattr(gearbox.results, 'i_1p1', i_1p1)            # Transmission ratio between sun shaft and first planet
    setattr(gearbox.results, 'i_p22', i_p22)            # Transmission ratio between second planet and ring gear
    setattr(gearbox.results, 'i_0', i_0)                # Stationary transmission ratio
    setattr(gearbox.results, 'i_1s', i_1s)              # Total transmission ratio between input and output shafts
    setattr(gearbox.results, 'i_p_rel', i_p_rel)        # Relative transmission ratio of the planets (for bearing rotational speed)
    # endregion

    return gearbox
