"""
Description:    This function computes data for two-stage transmissions in lay-shaft design
                for given transmission ratios
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
            (2) Kirchner, "Leistungsuebertragung in Fahrzeuggetrieben", Springer Verlag, 2007, ISBN: 978-3-540-35288-4
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  Bearings dimensions, gears dimensions, shafts dimensions, transmission ratio etc.
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of gearbox data
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
# Import classes
# Import methods
from .calc_b_d import calc_b_d
from .set_shaft_1 import set_shaft_1
from .set_shaft_2 import set_shaft_2
from .set_diff import set_diff
# endregion


def set_lay_shaft(gearbox, parameters):
    # region [1]: Initialization of required values
    # Gearbox Values
    i_tot = gearbox.Input.i_tot                 # Total transmission ratio[-]
    T_max = gearbox.Input.T_max                 # Maximum torque of el.motor[Nm]

    # Parameters
    tau_tw = parameters.gearbox.MatProp.tau_tw  # Torsional fatigue strength 16MnCr5(Kirchner, p.158) [N / mm ^ 2]

    # Initialization of normal modules as maximum values depending on the maximum torque(Koehler, pp. 54) [mm]
    if T_max < 200:
        setattr(gearbox.gears_12, 'm_n_1', 1.8)    # Reduced maximum normal module of stage 1 for low input torque[mm]
        setattr(gearbox.gears_34, 'm_n_3', 2.4)    # Reduced maximum normal module of stage 2 for low input torque[mm]
    elif T_max < 400:
        setattr(gearbox.gears_12, 'm_n_1', 2.2)        # Reduced maximum normal module of stage 1 for low input torque[mm]
        setattr(gearbox.gears_34, 'm_n_3', parameters.gearbox.GearingConst.m_n_3_max)  # Maximum normal module of stage 2[mm]
    else:
        setattr(gearbox.gears_12, 'm_n_1', parameters.gearbox.GearingConst.m_n_1_max)  # Maximum normal module of stage 1[mm]
        setattr(gearbox.gears_34, 'm_n_3', parameters.gearbox.GearingConst.m_n_3_max)  # Maximum normal module of stage 2[mm]
    setattr(gearbox.results, 'i_tot', i_tot)
    # endregion

    # region [2]: Calculation of gearbox data
    # Maximum torque at output shaft in Nmm
    T_out = T_max * 1000 * i_tot / 2

    # Approximation of output shaft diameter(Kirchner, p .159)
    d_sh_3 = math.pow((16 * T_out) / (math.pi * tau_tw), 1/3)
    setattr(gearbox.shafts, 'd_sh_3', d_sh_3)

    # Calculation main dimensions of the gears
    gearbox = calc_b_d(gearbox, parameters)

    # Dimensioning of the first shaft
    gearbox = set_shaft_1(gearbox, parameters)

    # Dimensioning of the second shaft
    gearbox = set_shaft_2(gearbox, parameters)

    # Dimensioning of the differential
    gearbox = set_diff(gearbox, parameters)
    # endregion

    # region [3]: Assign the Outputs
    # Calculation of final total transmission ratio
    setattr(gearbox.results, 'i_tot', gearbox.results.i_12*gearbox.results.i_34)
    # endregion

    return gearbox
