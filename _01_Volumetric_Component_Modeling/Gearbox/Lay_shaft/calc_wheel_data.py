"""
Description:    This function computes the number of teeth according to the chosen
                transmission ratios and calculates the wheels' dimensions
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
            (2) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
            (3) Decker and Kabus, "Maschinenelemente - Formeln", Carl Hanser Verlag, 2011, ISBN: 978-3-446-42990-1
            (4) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
            (5) K. Stahl, Documentation Lecture "Maschinenelemente", TUM, 2015/2016
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
         shaft: denotes which reduction stage is being considered (1 or 2; for the differential shaft a different calculation is used)
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


def calc_wheel_data(gearbox, parameters, shaft):
    # region [1]: Initialization of required variables
    # Parameters
    epsilon_beta = parameters.gearbox.GearingConst.epsilon_beta     # Desired overlap ratio [-]
    alpha_n = parameters.gearbox.GearingConst.alpha_n               # Normal pressure angle [rad] --> 20deg

    # Gearbox Values
    if shaft == 1:
        d_1 = gearbox.gears_12.d_1      # Initial pitch diameter of wheel 1[mm]
        m_n = gearbox.gears_12.m_n_1    # Normal module of first stage[mm]
        b = gearbox.gears_12.b_1        # Width of first stage[mm]

        i_12 = gearbox.results.i_12  # Initial transmission ratio of first stage[-]
    else:
        d_1 = gearbox.gears_34.d_3      # Initial pitch diameter of wheel 3[mm]
        m_n = gearbox.gears_34.m_n_3    # Normal module of second stage[mm]
        b = gearbox.gears_34.b_3        # Width of second stage[mm]

        i_12 = gearbox.results.i_34  # Initial transmission ratio of second stage[-]
    # endregion

    # region [2]: Calculation Wheel dimensions
    # Calculation of helix angle of the stage in rad (Decker, p. 136)
    beta = math.asin((epsilon_beta*m_n*math.pi)/b)
    if beta > math.pi/6:
        b = 2*epsilon_beta*m_n*math.pi
        beta = math.asin((epsilon_beta*m_n*math.pi)/b)

    # Calculation of pressure angle in transverse section in rad (Decker, p. 132)
    alpha_t = math.atan(math.tan(alpha_n)/math.cos(beta))

    # Definition of root clearance (Decker, p. 133)
    c = 0.25*m_n

    # Calculation of the number of teeth for automatic selection (Decker, p.135)
    if gearbox.Input.manTR == 0:
        z_1 = d_1*math.cos(beta)/m_n
        if shaft == 1:
            z_1 = round(z_1)
        else:
            z_1 = np.ceil(z_1)

        # Minimum number of teeth (Decker, p. 135)
        if z_1 < 15:
            z_1 = 15

        # Calculation of pitch diameters with integer tooth number in mm (Decker, p. 132 and Zaehringer, p. 25)
        d_1 = z_1*m_n/math.cos(beta)
        d_2 = i_12*d_1
        # Calculation of number of teeth of second wheel as for wheel 1
        z_2 = d_2*math.cos(beta)/m_n

        if shaft == 1:
            z_2 = round(z_2)
        else:
            z_2 = np.ceil(z_2)

        # Check if number of teeth corresponds to transmission ratio, 3
        # alternative transmission variants are created
        i_12_1 = z_2/z_1
        i_12_2 = (z_2+1)/z_1
        i_12_3 = z_2/(z_1+1)

        # Calculation of errors between desired transmission ratio and
        # transmission ratios generated from number of teeth
        err_1 = abs(i_12-i_12_1)
        err_2 = abs(i_12-i_12_2)
        err_3 = abs(i_12-i_12_3)

        # Check that the number of teeth is not an integral multiple: if the number
        # of teeth of the wheels of a stage are integral multiples, a penalty
        # is added so that another pair of number of teeth is chosen
        if math.fmod(z_2, z_1) == 0:
            err_1 = err_1+1
        elif math.fmod(z_2+1, z_1) == 0:
            err_2 = err_2+1
        elif math.fmod(z_2, z_1+1) == 0:
            err_3 = err_3+1

        # Search for minimum error of desired to calculated transmission ratio
        err_arr = np.array([[err_1], [err_2], [err_3]])
        opt = min(err_arr)

        # Definition of number of teeth and transmission ratio according to criteria
        if opt == err_1:
            i_12 = i_12_1
        elif opt == err_2:
            i_12 = i_12_2
            z_2 = z_2+1
        else:
            i_12 = i_12_3
            z_1 = z_1+1
    else:               # Switch for manual transmission ratios
        if shaft == 1:
            z_1 = gearbox.gears_12.z_1
            z_2 = gearbox.gears_12.z_2
        else:
            z_1 = gearbox.gears_34.z_3
            z_2 = gearbox.gears_34.z_4

    # Calculation of new gear dimensions with updated transmission ratios
    if gearbox.Input.axles == 'coaxial' and shaft == 2:
        d_1 = (2*gearbox.results.a_12)/(1+i_12)     # New pitch diameter of wheel 3 according to updated transmission ratio in mm
        d_2 = (2*gearbox.results.a_12)-d_1          # New pitch diameter of wheel 4 with fixed axle distance in mm
        a_12 = gearbox.results.a_12                 # Distance between shafts 2&3 stays the same
        z_1 = round(d_1*math.cos(beta)/m_n)         # New number of teeth of wheel 3
        z_2 = round(d_2*math.cos(beta)/m_n)         # New number of teeth of wheel 4
        i_12 = z_2/z_1                              # New transmission ratio of second stage
    else:
        d_1 = z_1*m_n/math.cos(beta)                     # New pitch diameter of pinion in mm (Decker, p. 132)
        d_2 = i_12*d_1                              # New pitch diameter of wheel in mm (Zaehringer, p. 25)
        a_12 = (d_1+d_2)/2

    # Calculation of outside, root and base diameters of pinion and wheel (Stahl, p. 106)
    d_a1 = d_1+(2*m_n)
    d_a2 = d_2+(2*m_n)

    d_f1 = d_1-(2*(m_n+c))
    d_f2 = d_2-(2*(m_n+c))

    d_b1 = d_1*math.cos(alpha_t)
    d_b2 = d_2*math.cos(alpha_t)
    # endregion

    # region [3]: Output Assignment
    if shaft == 1:
        setattr(gearbox.gears_12, 'beta_1', beta)         # Helix angle of first stage in rad
        setattr(gearbox.gears_12, 'alpha_t_1', alpha_t)   # Pressure angle in transverse section of first stage in rad
        setattr(gearbox.gears_12, 'd_1', d_1)             # Pitch diameter of wheel 1 in mm
        setattr(gearbox.gears_12, 'd_a1', d_a1)           # Outside diameter of wheel 1 in mm
        setattr(gearbox.gears_12, 'd_f1', d_f1)           # Root diameter of wheel 1 in mm
        setattr(gearbox.gears_12, 'd_b1', d_b1)           # Base diameter of wheel 1 in mm
        setattr(gearbox.gears_12, 'z_1', z_1)             # Number of teeth of wheel 1
        setattr(gearbox.gears_12, 'd_2', d_2)             # Pitch diameter of wheel 2 in mm
        setattr(gearbox.gears_12, 'd_a2', d_a2)           # Outside diameter of wheel 2 in mm
        setattr(gearbox.gears_12, 'd_f2', d_f2)           # Root diameter of wheel 2 in mm
        setattr(gearbox.gears_12, 'd_b2', d_b2)           # Base diameter of wheel 2 in mm
        setattr(gearbox.gears_12, 'z_2', z_2)             # Number of teeth of wheel 2
        setattr(gearbox.gears_12, 'b_1', b)               # Width of first stage gears in mm

        setattr(gearbox.results, 'a_12', a_12)            # Updated distance between shafts 1&2 in mm
        setattr(gearbox.results, 'i_12', i_12)            # updated transmission ratio of first stage
    else:
        setattr(gearbox.gears_34, 'beta_2', beta)         # Helix angle of second stage in rad
        setattr(gearbox.gears_34, 'alpha_t_2', alpha_t)   # Pressure angle in transverse section of second stage in rad
        setattr(gearbox.gears_34, 'd_3', d_1)             # Pitch diameter of wheel 3 in mm
        setattr(gearbox.gears_34, 'd_a3', d_a1)           # Outside diameter of wheel 3 in mm
        setattr(gearbox.gears_34, 'd_f3', d_f1)           # Root diameter of wheel 3 in mm
        setattr(gearbox.gears_34, 'd_b3', d_b1)           # Base diameter of wheel 3 in mm
        setattr(gearbox.gears_34, 'z_3', z_1)             # Number of teeth of wheel 3
        setattr(gearbox.gears_34, 'd_4', d_2)             # Pitch diameter of wheel 4 in mm
        setattr(gearbox.gears_34, 'd_a4', d_a2)           # Outside diameter of wheel 4 in mm
        setattr(gearbox.gears_34, 'd_f4', d_f2)           # Root diameter of wheel 4 in mm
        setattr(gearbox.gears_34, 'd_b4', d_b2)           # Base diameter of wheel 4 in mm
        setattr(gearbox.gears_34, 'z_4', z_2)             # Number of teeth of wheel 4
        setattr(gearbox.gears_34, 'b_3', b)               # Width of second stage gears in mm

        setattr(gearbox.results, 'a_23', a_12)            # Updated distance between shafts 2&3 in mm
        setattr(gearbox.results, 'i_34', i_12)            # Updated transmission ratio of second stage
    # endregion

    return gearbox
