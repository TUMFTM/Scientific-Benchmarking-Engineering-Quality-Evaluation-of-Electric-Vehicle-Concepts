"""
Description:    This function calculates dimensions and gear data
                of the differtial gear according to Zaehringer, starting p. 53
------------
Sources:    (1) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
            (2) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  Dimensions of the differential
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of differential data
[3] Assign Outputs
"""


# region [0] Import all necessary modules, classes and methods
# Import modules
# Import classes
# Import methods
# endregion


def calc_diff_data(gearbox, parameters):
    # region [1]: Initialization of required values
    # Gearbox Values
    b_3 = gearbox.gears_34.b_3                              # Width of wheels 3&4 [mm]

    d_bev_l = gearbox.differential.d_bev_l                  # Diameter of larger bevel gears [mm]
    b_d_bevel = parameters.gearbox.GearingConst.b_d_bevel  # Empirical ratio of bevel gear width and outer diameter (Koehler, p.41) [-]
    t_diffcage = parameters.gearbox.ConstDim.t_diffcage     # Minimum thickness of differential housing [mm]
    # endregion

    # region [2]: Calculation of differential data
    # Determination of the differential cage width in mm
    if gearbox.Input.axles.lower() == 'coaxial':
        b_diffcage = d_bev_l+2*t_diffcage-0.3*b_3
    else:
        b_diffcage = d_bev_l+2*t_diffcage

    # Determination of the empirical width of bevel gearing in mm
    b_bev = b_d_bevel*d_bev_l
    # endregion

    # region [3]: Output Assignment
    setattr(gearbox.differential, 'b_diffcage', b_diffcage)     # width of the differential cage in mm
    setattr(gearbox.differential, 'b_bev', b_bev)               # width of bevel gearing in mm
    # endregion

    return gearbox
