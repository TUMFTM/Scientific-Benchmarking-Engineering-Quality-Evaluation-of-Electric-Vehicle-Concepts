"""
Description:    This function computes the housing dimensions of the planetary gearbox.
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
            (2) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Master Thesis, TUM, 2020
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
         shaft: denotes which reduction stage is being considered (1 or 2; for the differential shaft a different calculation is used)
         d_ctlg: List of inner bearing diameters [mm]
------------
Output:  Gearbox housing dimensions
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of the gearbox' dimensions:
[2.1] Calculation of gearbox width in mm ((2), pp. 56)
[2.2] Determination of gearbox diameter in mm ((2), pp. 56)
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
# Import classes
# Import methods
# endregion


def calc_dimensions_plan(gearbox, parameters):
    # region [1]: Initialization of required values
    # Parameters
    b_gap = parameters.gearbox.ConstDim.b_gap           # Gap between components on the shafts [mm]
    t_housing = parameters.gearbox.ConstDim.t_housing   # Housing thickness as mean of database ([1], p. 60) [mm]
    d_housing = parameters.gearbox.ConstDim.d_housing   # Distance between gears and housing as mean of database (Koehler, p. 60) [mm]
    b_seal = parameters.gearbox.ConstDim.b_seal         # Width of seals on output shafts as mean of database (Koehler, p. 60) [mm]
    d_flange = parameters.gearbox.ConstDim.d_flange     # Additional space for screws on housing flange as average of database (Koehler, p. 60) [mm]

    # Gearbox Values
    m_n_1 = gearbox.gears_12.m_n_1                      # Normal module of the first stage [mm]
    m_n_2 = gearbox.gears_12.m_n_2                      # Normal module of the second stage [mm]
    d_1 = gearbox.gears_12.d_1                          # Pitch diameter of sun gear [mm]
    d_p1 = gearbox.gears_12.d_p1                        # Pitch diameter of the planet 1 [mm]
    d_ap2 = gearbox.gears_12.d_ap2                      # Outside diameter of planet 2 [mm]
    d_f2 = gearbox.gears_12.d_f2                        # Root diameter of ring gear [mm]
    b_1 = gearbox.gears_12.b_1                          # Width of first stage gears [mm]
    b_2 = gearbox.gears_12.b_2                          # Width of second stage gears [mm]
    d_s = gearbox.gears_12.d_s                          # Diameter of planet circle [mm]

    b_C = gearbox.bearings_2.b_C                        # Width of bearing C [mm]
    b_D = gearbox.bearings_2.b_D                        # Width of bearing D [mm]
    b_E = gearbox.bearings_3.b_E                        # Width of bearing E [mm]
    b_F = gearbox.bearings_3.b_F                        # Width of bearing F [mm]

    if gearbox.Input.num_EM == 1:
        d_diffcage = gearbox.differential.d_diffcage    # Diameter of differential cage [mm]
        b_diffcage = gearbox.differential.b_diffcage    # Width of differential cage [mm]
    else:   # gearbox.Input.num_EM == 2:
        d_diffcage = gearbox.bearings_3.d_1_E
        b_diffcage = b_gap
    # endregion

    # region [2]: Calculation of the gearbox' dimensions
    # region [2.1]: Calculation of gearbox width in mm ([2], pp. 56)
    t_plancarrier = b_F+5+b_C+b_gap+b_1+b_gap+b_2+b_gap+b_D+5
    t_diff = b_diffcage+b_E

    if gearbox.Input.num_EM == 1:
        # Integration of differential in planet carrier if planet circle is large enough
        if d_s > d_diffcage+4+d_ap2:
            t_gearing = t_plancarrier+t_diff-(5+b_D+b_gap+b_2)
        else:
            t_gearing = t_plancarrier+t_diff
    else:   # gearbox.Input.num_EM == 2:
        t_gearing = t_plancarrier+t_diff

    # Width of housing for mass calculations in mm ((1), p. 61)
    t_gearbox = b_seal+t_gearing+b_seal
    # endregion

    # region [2.2]: Determination of gearbox diameter in mm ((2), pp. 56)
    # Maximum outer diameter of gears of the first stage in mm
    d_1_max = d_1+2*d_p1+2*m_n_1+2*d_housing
    # Maximum diameter of the ring gear (second stage) in mm
    d_2_max = d_f2+2*6*m_n_2
    # Critical diameter for outer gearbox dimensions in mm
    d_gearing = max(d_1_max, d_2_max)

    # Calculation of gearbox length and height in mm  ((1), p. 61)
    d_gearbox = d_gearing+2*t_housing+2*d_flange
    # endregion
    # endregion

    # region [3]: Output Assignment
    setattr(gearbox.dimension_house, 'd_gearbox', d_gearbox)    # Diameter of the gearbox housing according to dimensional chains in mm
    setattr(gearbox.dimension_house, 't_gearbox', t_gearbox)    # Width of the gearbox housing according to dimensional chains in mm
    setattr(gearbox.dimension_house, 'd_gearing', d_gearing)    # Largest diameter of all gears in mm
    setattr(gearbox.dimension_house, 't_gearing', t_gearing)    # Width of all components inside the gearbox housing in mm

    setattr(gearbox.differential, 't_diff', t_diff)             # Width of differential in mm

    setattr(gearbox.shafts, 'd_1_max', d_1_max)                 # Maximum outer diameter of gears of the first stage [mm]
    setattr(gearbox.shafts, 'd_2_max', d_2_max)                 # Maximum diameter of the ring gear (second stage) [mm]
    # endregion

    return gearbox
