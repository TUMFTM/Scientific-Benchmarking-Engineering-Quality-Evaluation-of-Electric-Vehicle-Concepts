"""
Description:    This function calculates gearbox data for a non-shiftable two-stage
                helical-gear electric transmission in lay-shaft design
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
            (2) Niemann and Winter, "Maschinenelemente - Band 2: Getriebe allgemein, Zahnradgetriebe", Springer Verlag, 2003, ISBN: 978-3-662-11874-0
            (3) Parlow, "Entwicklung einer Methode zum anforderungsgerechten Entwurf von Stirnradgetrieben", Ph.D Thesis, TUM, 2016
            (4) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  Gearbox housing dimensions, bearings dimensions, gears dimensions, shafts dimensions, transmission ratio etc.
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of gearbox data
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
import numpy as np
import copy
# Import classes
# Import methods
from .set_lay_shaft import set_lay_shaft
# endregion


def set_layshaft_transmission(gearbox, parameters):
    # region [1]: Initialization of required values
    # Gearbox Values
    i_tot = gearbox.Input.i_tot             # Total transmission ratio[-]
    manTR = gearbox.Input.manTR             # For manual number of teeth as input

    # Parameters
    S_H_min = parameters.gearbox.MinSafety.S_H_min  # Minimum safety factor against flank break (Niemann and Winter, p. 344)[-]
    S_F_min = parameters.gearbox.MinSafety.S_F_min  # Minimum safety factor against root break (Niemann and Winter, p. 344)[-]

    # Number of iterations for selection of transmission ratios of both stages
    n = 1   # MUST BE odd!
    step = 0.2
    # endregion

    # region [2]: Calculation of gearbox
    if manTR == 0:  # The user did not give a desired number of teeth, this has to be derived!
        # Calculation and storage of initial transmission ratio of both stages(Parlow pp.6)
        i_12 = 1.1260 * math.pow(i_tot, 0.5103)  # formula for minimum gear mass
        i_12_res = i_12 + step * np.floor(n/2)
        setattr(gearbox.results, 'i_12', i_12_res)
        setattr(gearbox.results, 'i_34', i_tot/i_12_res)

        # Optimization of the transmission ratios in relation to tooth safety factors (Zaehringer, p.92)
        i_12_new = gearbox.results.i_12
        err_S_H_12 = np.zeros((1, n))
        err_S_H_34 = np.zeros((1, n))
        err_S_F_12 = np.zeros((1, n))
        err_S_F_34 = np.zeros((1, n))
        gearbox_list = []

        for i in range(n):
            gearbox = set_lay_shaft(gearbox, parameters)
            gearbox_list.append(copy.deepcopy(gearbox))

            # Absolute errors in the safety factors of both stages
            err_S_H_12[:, i] = gearbox.results.S_H_12-S_H_min
            err_S_H_34[:, i] = gearbox.results.S_H_34-S_H_min
            err_S_F_12[:, i] = gearbox.results.S_F_12-S_F_min
            err_S_F_34[:, i] = gearbox.results.S_F_34-S_F_min

            setattr(gearbox.results, 'i_12', i_12_new-(step*(i+1)))
            setattr(gearbox.results, 'i_34', i_tot/gearbox.results.i_12)

        # Calculation   of dataset with minimum delta of the safety factors
        err_sum = err_S_H_12 + err_S_H_34 + err_S_F_12 + err_S_F_34
        min_idx = np.argmin(err_sum)

        gearbox = gearbox_list[min_idx]

    else:  # The user has manually given the desired number of teeth
        z_1 = gearbox.Input.z_1             # Number of teeth of first wheel
        z_2 = gearbox.Input.z_2             # Number of teeth of second wheel
        z_3 = gearbox.Input.z_3             # Number of teeth of third wheel
        z_4 = gearbox.Input.z_4             # Number of teeth of forth wheel

        # Definition of transmission ratios and number of teeth for manual selection
        setattr(gearbox.results, 'i_12',  z_2/z_1)
        setattr(gearbox.results, 'i_34',  z_4/z_3)

        setattr(gearbox.gears_12, 'z_1', z_1)
        setattr(gearbox.gears_12, 'z_2', z_2)

        setattr(gearbox.gears_34, 'z_3', z_3)
        setattr(gearbox.gears_34, 'z_4', z_4)

        gearbox = set_lay_shaft(gearbox, parameters)
    # endregion
    return gearbox
