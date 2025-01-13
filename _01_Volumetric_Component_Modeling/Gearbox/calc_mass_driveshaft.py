"""
Description:    This function computes the mass of both drive shafts of one propelled axle according to data
                from the Gearbox function.
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
            (2) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
------------
Input:   gearbox: Class element which stores all the gearbox information
         parameters: Class element which stores all necessary computation parameters
         e_machine_length
------------
Output:  Mass and dimensions of the driveshafts
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of drive shaft mass
[3] Output assignment
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
# Import classes
# Import methods
# endregion


def calc_mass_driveshaft(gearbox, parameters, e_machine_length):
    # region [1]: Initialization of required values
    # Assign gearbox parameters
    T_max = gearbox.Input.T_max                     # Maximum torque of electric machine [Nm]
    i_tot = gearbox.results.i_tot                   # Total transmission ratio of the gearbox [-]
    d_sh_3 = gearbox.shafts.d_sh_3                  # Diameter of output shafts [mm]
    t_gearbox = gearbox.dimension_house.t_gearbox   # Width of the gearbox housing according to dimensional chains in mm

    # Assign constant parameters and regressions from the parameters class
    rho_gear = parameters.gearbox.MatProp.rho_gear/math.pow(10, 9)      # Density 16MnCr5 (2, p. 67) [kg/mm^3]
    regr_m_out = parameters.regr.gearbox.m_out        # Regression formula for the mass of the output shafts (2, p. 67) [kg]
    # endregion

    # region [2]: Calculation of drive shaft mass
    # Resulting maximum torque on each drive shaft in Nm
    T_out = T_max * i_tot/2

    # Total mass of both drive shafts of one propelled axle calculated by a
    # linear regression of gearbox database in kg (2, p. 67)
    coeff = regr_m_out.coefficients
    m_driveshaft = coeff[0] + coeff[1] * T_out

    # If the number of EM on the axle is 2, the mass of the output shaft is
    # reduced by the length of the EMs and gearboxes
    if gearbox.Input.num_EM == 2:
        m_driveshaft = m_driveshaft - 2 * (math.pow(0.5 * d_sh_3, 2) * math.pi * (e_machine_length + t_gearbox) * rho_gear)

    # endregion

    # region [3]: Output assignment
    setattr(gearbox.masses, 'm_driveshaft',  m_driveshaft)
    # endregion

    return gearbox
