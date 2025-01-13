"""
Description:    This function computes the transmission ratios between all gears in the planetary gearbox and
                calls the set_planetary-function.
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
            (2) Mueller, "Die Umlaufgetriebe", Springer Verlag, 1998, ISBN: 978-3-642-58725-2
            (3) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  Gearbox housing dimensions, bearings dimensions, gears dimensions, shafts dimensions, transmission ratio etc.
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of the transmission ratios according (Mueller, p.34)
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
import numpy as np
import copy
# Import classes
# Import methods
from .set_planetary import set_planetary
# endregion


def set_planetary_transmission(gearbox, parameters):
    # region [1]: Initialization of required values
    # Gearbox Values
    i_tot = gearbox.Input.i_tot         # Total transmission ratio [-]
    manTR = gearbox.Input.manTR         # For manual number of teeth as input

    # Constants
    # Number of iterations for selection of transmission ratios of both stages
    n = 5                 # has to be ODD!
    step = 0.1
    iteration = 0

    # Preallocation of error arrays
    err_S_H_12 = np.zeros((1, n))
    err_S_H_34 = np.zeros((1, n))
    err_S_F_12 = np.zeros((1, n))
    err_S_F_34 = np.zeros((1, n))
    err_i_tot = np.zeros((1, n))
    # endregion

    # region [2]: Calculation of the transmission ratios according (Mueller, p.34)
    if manTR == 0:
        # Total transmission ratio is between input (sun) shaft and planet carrier (index s)
        i_1s = i_tot
        # Stationary gear ratio (between sun shaft and ring gear)
        i_0 = 1-i_1s

        # Determination of the transmission ratio of the first stage from the total ratio (Koehler, p. 56):
        i_1p1 = math.pow(i_1s, (1/4))

        # Storage of initial transmission ratios for further calculation
        setattr(gearbox.results, 'i_1s',  i_1s)
        setattr(gearbox.results, 'i_0',  i_0)

        # Optimization of the transmission ratios in relation to tooth safety factors (Zaehringer, p. 92)
        i_1p1_max = i_1p1+step*math.floor(n/2)

        gearbox_selection = []
        for i in range(n, 0, -1):

            setattr(gearbox.results, 'i_1p1', i_1p1_max - (step * (n - i)))
            setattr(gearbox.results, 'i_p22', i_0 / gearbox.results.i_1p1)

            # Calculation of the gearbox with given stage transmission ratios
            gearbox = set_planetary(gearbox, parameters)

            # Store the gearbox class in a list
            gearbox_selection.append(copy.deepcopy(gearbox))

            # Determination of errors in safety factors and transmission ratio
            err_S_H_12[0, iteration] = abs(gearbox.results.S_H_1p1-gearbox.results.S_H_p22)
            err_S_H_34[0, iteration] = abs(gearbox.results.S_H_1p1-gearbox.results.S_H_p22)
            err_S_F_12[0, iteration] = abs(gearbox.results.S_F_1p1-gearbox.results.S_F_p22)
            err_S_F_34[0, iteration] = abs(gearbox.results.S_F_1p1-gearbox.results.S_F_p22)
            err_i_tot[0, iteration] = abs(gearbox.Input.i_tot-gearbox.results.i_1s)

            iteration += 1

        # Calculation of dataset with minimum delta of the safety factors
        err_sum = err_S_H_12+err_S_H_34+err_S_F_12+err_S_F_34+err_i_tot
        idx = np.nanargmin(err_sum)

        gearbox = gearbox_selection[idx]

    else:   # Storing of numbers of teeth and transmission ratios for manual selection
        # Assign teeth number
        z_1 = gearbox.Input.z_1  # Number of teeth of sun gear
        z_p1 = gearbox.Input.z_2  # Number of teeth of first planet
        z_p2 = gearbox.Input.z_3  # Number of teeth of second planet
        z_2 = gearbox.Input.z_4  # Number of teeth of ring gear

        # Assign Inputs
        setattr(gearbox.gears_12, 'z_1', z_1)
        setattr(gearbox.gears_12, 'z_p1', z_p1)
        setattr(gearbox.gears_12, 'z_p2', z_p2)
        setattr(gearbox.gears_12, 'z_2', z_2)

        setattr(gearbox.results, 'i_1p1', abs(z_2/z_1))
        setattr(gearbox.results, 'i_p22', z_2/z_p2)
        i_0 = gearbox.results.i_1p1 * gearbox.results.i_p22
        setattr(gearbox.results, 'i_0', i_0)
        setattr(gearbox.results, 'i_1s', 1-i_0)

        # Calculation of the gearbox with given transmission ratio
        gearbox = set_planetary(gearbox, parameters)
    # endregion

    return gearbox
