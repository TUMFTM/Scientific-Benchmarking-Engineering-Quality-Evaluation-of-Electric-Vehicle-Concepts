"""
Description:    This function computes a bevel gear differential for gearbox with taper roller bearings
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
            (2) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
            (3) Schaeffler, "Waelzlager", Bearing Catalogue, 2019
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  Dimensioning of all elements on the third/differential shaft (gears, shaft, bearings)
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of output shaft data
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import numpy as np
# Import classes
# Import methods
from .calc_diff_data import calc_diff_data
from .set_bearings_diff import set_bearings_diff
# endregion


def set_diff(gearbox, parameters):
    # region [1]: Initialization of required values
    # Gearbox Values
    b_1 = gearbox.gears_12.b_1             # Width of wheels 1&2 [mm]

    b_3 = gearbox.gears_34.b_3             # Width of wheels 3&4 [mm]

    diff_orientation = gearbox.differential.diff_orientation  # Orientation of the differential

    # Parameters
    b_gap = parameters.gearbox.ConstDim.b_gap         # Gap between components on the shafts (Zaehringer, p. 64) [mm]

    # Loading of the bearing catalogue
    tr = parameters.gearbox.BearCtlg.roller     # Loading of Schaeffler taper roller bearing catalogue (starting on p. 590)
    length_tr = len(tr)
    d_ctlg = np.array(tr.d.values).reshape(length_tr, 1)             # List of inner bearing diameters [mm]
    d_A_ctlg = np.array(tr.d_A.values).reshape(length_tr, 1)         # List of outer bearing diameters [mm]
    b_ctlg = np.array(tr.b.values).reshape(length_tr, 1)             # List of bearing widths [mm]
    C_dyn_ctlg = np.array(tr.C_dyn.values).reshape(length_tr, 1)     # List of dynamic load ratings [N]
    m_ctlg = np.array(tr.m.values).reshape(length_tr, 1)             # List of bearing masses [kg]
    a_ctlg = np.array(tr.a.values).reshape(length_tr, 1)             # List of bearing distances [mm]
    e_ctlg = np.array(tr.e.values).reshape(length_tr, 1)             # List of bearing factors e [-]
    Y_ctlg = np.array(tr.Y.values).reshape(length_tr, 1)             # List of bearing factors Y [-]
    d_1_ctlg = np.array(tr.d_1.values).reshape(length_tr, 1)         # List of diameters of inner bearing ring [mm]
    C_stat_ctlg = np.array(tr.C_stat.values).reshape(length_tr, 1)   # List of static load ratings [N]
    Y_0_ctlg = np.array(tr.Y_0.values).reshape(length_tr, 1)         # List of bearing factors Y_0 [-]
    name_ctlg = tr.Name                                              # List of bearing codes

    # endregion

    # region [2]: Calculation of output shaft data
    # Switch for number of EMs on vehicle axle (differential only for one EM)
    if gearbox.Input.num_EM == 1:
        # Calculation of differential dimensions and gear data
        gearbox = calc_diff_data(gearbox, parameters)

        # Selection of bearings according to input load and desired lifetime
        gearbox = set_bearings_diff(gearbox, parameters, d_ctlg, d_A_ctlg, b_ctlg, C_dyn_ctlg, m_ctlg, a_ctlg, e_ctlg,
                                    Y_ctlg, d_1_ctlg, C_stat_ctlg, Y_0_ctlg, name_ctlg)

        # Calculation of the width of the differential with bearings in mm
        if gearbox.Input.axles.lower() != 'parallel':
            b_diff = gearbox.bearings_3.b_E+gearbox.differential.b_diffcage+b_3+b_gap+gearbox.bearings_3.b_F
        elif diff_orientation.lower() == 'out':
            b_diff = gearbox.bearings_3.b_E+gearbox.differential.b_diffcage+b_3+b_gap+b_1+b_gap+gearbox.bearings_3.b_F
        else:
            b_diff = gearbox.bearings_3.b_E+gearbox.differential.b_diffcage+b_3+b_gap+gearbox.bearings_3.b_F

    elif gearbox.Input.num_EM == 2:
        # Selection of bearings according to input load and desired lifetime
        gearbox = set_bearings_diff(gearbox, parameters, d_ctlg, d_A_ctlg, b_ctlg, C_dyn_ctlg, m_ctlg, a_ctlg, e_ctlg,
                                    Y_ctlg, d_1_ctlg, C_stat_ctlg, Y_0_ctlg, name_ctlg)

        # Calculation of the width of the third shaft in mm
        b_sh_3 = gearbox.bearings_3.b_E+b_gap+b_3+b_gap+gearbox.bearings_3.b_F
    # endregion

    # region [3]: Output Assignment
    if gearbox.Input.num_EM == 1:
        # noinspection PyUnboundLocalVariable
        setattr(gearbox.differential, 'b_diff',  b_diff)           # Width of the differential in mm
    elif gearbox.Input.num_EM == 2:
        # noinspection PyUnboundLocalVariable
        setattr(gearbox.shafts, 'b_sh_3',  b_sh_3)         # Width of the third shaft in mm

        setattr(gearbox.differential, 'd_diffcage', gearbox.bearings_3.d_1_E)
        setattr(gearbox.differential, 'b_diffcage', b_gap)
    # endregion

    return gearbox
