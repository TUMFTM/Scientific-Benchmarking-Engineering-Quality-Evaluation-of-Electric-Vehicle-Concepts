"""
Description:    This Function computes a planetary gearbox for given input data
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
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
# Import classes
# Import methods
from .calc_b_d_plan import calc_b_d_plan
from .set_sun_shaft import set_sun_shaft
from .set_planets import set_planets
from .set_diff_plan import set_diff_plan
# endregion


def set_planetary(gearbox, parameters):
    # region [1]: Initialization of required values
    # Gearbox Values
    i_tot = gearbox.results.i_1s                    # Total transmission ratio [-]
    T_max = gearbox.Input.T_max                     # Maximum torque of el. motor [Nm]
    tau_tw = parameters.gearbox.MatProp.tau_tw      # Torsional fatigue strength 16MnCr5 (Kirchner, p. 158) [N/mm^2]

    # Initialization of normal modules as maximum values depending on the maximum torque (Koehler, pp. 54) [mm]
    if T_max < 200:
        setattr(gearbox.gears_12, 'm_n_1', 1.6)      # Reduced maximum normal module of stage 1 for low input torque [mm]
    elif T_max < 400:
        setattr(gearbox.gears_12, 'm_n_1', 1.8)     # Reduced maximum normal module of stage 1 for low input torque [mm]
    else:
        setattr(gearbox.gears_12, 'm_n_1', 2.0)     # Maximum normal module of stage 1 [mm]
    # endregion

    # region [2]: Calculation of gearbox data
    # Maximum torque at output shaft in Nmm
    T_out = T_max * 1000 * i_tot/2
    # Approximation of output shaft diameter in mm (Kirchner, p.159)
    d_sh_3 = math.pow((16*T_out)/(math.pi*tau_tw), (1/3))
    # Save output shaft diameter in gearbox struct
    setattr(gearbox.shafts, 'd_sh_3', d_sh_3)

    # Calculation main dimensions of the gears
    gearbox = calc_b_d_plan(gearbox, parameters)

    # Calculation of the sun shaft
    gearbox = set_sun_shaft(gearbox, parameters)

    # Calculation of the planets
    gearbox = set_planets(gearbox, parameters)

    # Calculation of the differential gear
    gearbox = set_diff_plan(gearbox, parameters)

    # Final total transmission ratio
    i_tot_new = 1 - (gearbox.results.i_1p1 * gearbox.results.i_p22)
    setattr(gearbox.results, 'i_tot', i_tot_new)
    # endregion

    return gearbox
