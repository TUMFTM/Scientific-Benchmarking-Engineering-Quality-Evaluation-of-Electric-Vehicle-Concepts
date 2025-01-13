"""
Description:    This function computes the inclination between the shafts of a parallel lay-shaft gearbox
                according to the optimization goal (Height/Length/Mass/Manual)
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  Inclination of the gearbox shafts (required for the gearbox dimension estimation)
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of auxiliary parameters
[3] Switch for selected optimization
[4] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
import numpy as np
# Import classes
# Import methods
from .calc_mass_laysh import calc_mass_laysh
# endregion


def calc_inc(gearbox, parameters):
    # region [1]: Initialization of required values
    # Gearbox Values
    d_mot = gearbox.Input.d_mot  # Diameter of el. motor [mm]
    inc_init = gearbox.Input.inc_init  # Angle between shafts with manual selection [deg]
    opt_gears = gearbox.Input.opt_gears  # Optimization goal

    d_1 = gearbox.gears_12.d_1  # Pitch diameter of wheel 1 [mm]
    d_2 = gearbox.gears_12.d_2  # Pitch diameter of wheel 2 [mm]

    d_4 = gearbox.gears_34.d_4                  # Pitch diameter of wheel 4 [mm]

    a_12 = gearbox.results.a_12                 # Distance between shafts 1&2 [mm]
    a_23 = gearbox.results.a_23                 # Distance between shafts 2&3 [mm]

    d_sh_3 = gearbox.shafts.d_sh_3              # Outer diameter of output shaft [mm]

    # Constants
    inc = 0                                     # Initialization of inclination parameter
    angle = np.arange(0, 61, 1).reshape(61, 1)  # Initialization of possible angles as
    # endregion

    # region [2]: Calculation of auxiliary parameters
    # Definition of characteristic dimensions
    theta = angle*math.pi/180                       # Possible angles between the connecting lines of axles 1-2 and 1-3 [rad]
    zeta = np.arcsin((a_12/a_23)*np.sin(theta))     # Possible angles between the connecting lines of axles 3-1 and 3-2 [rad]
    z_1 = (a_12*np.cos(theta))+(a_23*np.cos(zeta))  # Distance between shafts 1&3 in mm
    z = z_1-(d_sh_3/2)                              # Distance between shaft 1 and outer limit of output shaft in mm
    val = (a_12*np.cos(theta))+(d_1/2)              # Distance between outer limit of wheel 1 and shaft 2 in x/y-plane

    # Definition of general geometric criteria: output shaft fits next to el. motor, wheel 1 is outer limit, wheel 1&4 do not cross
    test_matrix = np.concatenate((z > (d_mot/2+5), val > (d_2/2), z_1 > ((d_4/2)+(d_2/2))), axis=1)
    test_cond = np.nansum(test_matrix, axis=1).reshape(test_matrix.shape[0], 1)
    poss_angle = np.asarray(np.where(test_cond == 3))
    # endregion

    # region [3]: Switch for selected optimization
    if np.size(poss_angle) == 0:
        print('The drive unit cannot be mounted on the axle, since the machine on the Input shaft has such a big diameter, that it collides with the output shaft!!')
        print('The drive unit will be assembled anyway although this will lead to collisions!!!')
        inc = 0

        # Check if the actual number of Error stored in Errorlog
        # id=numel(gearbox.ErrorLog);
        # gearbox.Errorlog{id+1}='Drive unit unfeasible due to collision';

    else:
        if opt_gears.lower() == 'length':
            # Determine the lengths that fit geometric criteria
            z_poss = z_1[poss_angle[0, :]]
            inc_idx = np.argmin(z_poss)
            inc = angle[inc_idx][0]
        elif opt_gears.lower() == 'manual':
            # Angle is set to desired value
            inc = inc_init
        elif opt_gears.lower() == 'height':
            # Determines minimum length for minimum height = d_4
            if d_2 > d_4 or np.size(poss_angle) == 0:
                inc = 0
            else:
                h = d_2/2+a_12*np.sin(theta)
                h_poss = h[poss_angle[0, :]]
                inc_idx = np.asarray(np.where(h_poss < d_4/2))[0, -1]
                inc = angle[inc_idx][0]
        elif opt_gears.lower() == 'Mass':
            # Determines angle for minimum housing mass
            angle = angle[poss_angle[0, :]]
            m_er = np.zeros(1, len(angle))
            for t in range(0,  len(angle)):         # Calculate mass for all angles that fit geometric criteria
                setattr(gearbox.results, 'theta', theta[t][0])
                setattr(gearbox.results, 'zeta', zeta[t][0])
                if gearbox.Input.axles.lower() == 'parallel':
                    gearbox = calc_mass_laysh(gearbox, parameters)
                else:
                    # gearbox = calc_mass_2sp(gearbox)
                    raise Exception("THIS FUNCTION IS NOT IMPLEMENTED IN THIS VERSION")

                m_er[t] = gearbox.results.m_gearbox        # Array with possible masses in kg
            inc_idx = np.argmin(m_er)
            inc = angle[inc_idx][0]                        # Choose angle with minimum mass in kg
    # endregion

    # region [4]: Output Assignment
    setattr(gearbox.results, 'inc', inc)          # Inclination of the gearbox on y-axis in deg
    # endregion

    return gearbox
