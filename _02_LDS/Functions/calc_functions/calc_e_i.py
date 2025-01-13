"""
Description:  If the e_i is a User-Input, then the Input will be assigned for further
              calculations, if not the Input will be calculated by using the reduced inertia
              from motor and inertia of wheels
------------
Sources: More information regarding the implementation of the LDS functions is available at:
         (1) K. Moller, „Validierung einer MATLAB Längsdynamiksimulation für die Auslegung von Elektrofahrzeugen,“ Bachelor thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2020.
         (2) K. Moller, „Antriebsstrangmodellierung zur Optimierung autonomer Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The mass inertia factor reduced at the wheel center, e_i
------------

Implementation
[0] Import modules, classes and functions
[1] Inertia factor for given Input
[2] Calculate moment of inertia
[2.1] Calculate the moments of inertia for the e-machine(s)
[2.2] Calculate moments of inertia for the gearbox(es)
[2.3] Calculate the moment of inertia for the remaining rotational components
[2.4] Calculate the mass inertia factor
[2.5] Assign Calculated Outputs
[3] Assign mass inertia factor
"""

# region [0] Import modules, classes and functions
# Import modules
import numpy as np
import math
# Import functions
from _01_Volumetric_Component_Modeling.Gearbox.Lay_shaft.calc_J_laysh import calc_J_laysh
from _01_Volumetric_Component_Modeling.Gearbox.Planetary.calc_J_planetary import calc_J_planetary
# endregion


def calc_e_i(vehicle, parameters):
    # region [1] Inertia factor for given Input
    if hasattr(vehicle.Input, 'e_i') and not np.isnan(vehicle.Input.e_i):   # The User has assigned an e_i which should be used

        # repeat given e_i value - needed for multispeed transmission
        e_i = vehicle.Input.e_i
    # endregion

    # region [2] Calculate moment of inertia
    else:    # The User did not assign an Input e_i
        # To exactly calculate the e_i, all the masses of the rotating
        # components need to be known. Therefore all masses must be known

        # region [2.1] Calculate the moments of inertia for the e-machine(s)
        J_red = {'front': 0, 'rear': 0}
        # Reduced inertia front motors in kg m^2
        for key, value in vehicle.topology.filled_axles.items():
            if value is True:
                J_M = vehicle.e_machine[key].J_M
                quantity = vehicle.e_machine[key].quantity
                i_gearbox = vehicle.gearbox[key].results.i_tot
                J_red[key] = J_M * quantity * math.pow(i_gearbox, 2)

        J_gearbox = {'front': 0, 'rear': 0}
        # endregion

        # region [2.2] Calculate moments of inertia for the gearbox(es)
        for key, value in vehicle.topology.filled_axles.items():
            if value is True:
                gearbox = vehicle.gearbox[key]

                if gearbox.Input.type.lower() == 'lay-shaft':
                    # Calculation of moment of inertia in kg*mm^2
                    gearbox = calc_J_laysh(gearbox, parameters)

                else:       # It is a planetary gearbox
                    # Calculation of moment of inertia in kg*mm^2
                    gearbox = calc_J_planetary(gearbox, parameters)

                J_gearbox[key] = gearbox.results.J_tot_out * math.pow(10, -6)

                if J_gearbox[key] < 0:
                    # Define errorlog
                    errorlog_list = vehicle.errorlog
                    text_errorlog = 'Error in the calculation of the gearbox inertia. The values are not realistic and will be overwritten with typical values!'
                    print(text_errorlog)
                    errorlog_list.append(text_errorlog)
                    setattr(vehicle, 'errorlog', errorlog_list)

                    # Define Gearbox inertia
                    J_gearbox[key] = 0.168  # Typical value for a gearbox (calculated from reference vehicle BMW i3)

        # endregion

        # region [2.3] Calculate the moment of inertia for the remaining rotational components
        # mass of 4 wheels (calculated from the wheel modeling)
        m_wheels = vehicle.masses.chassis.tires_weight                  # All four tires in kg
        m_rims = vehicle.masses.chassis.rims_weight                     # All four rims kg
        m_brakes = vehicle.masses.chassis.wheel_brakes_weight           # All four brakes in kg

        # Check which of the wheels is wider
        r_wheels = np.array([vehicle.dimensions.CX.wheel_f_diameter/2000, vehicle.dimensions.CX.wheel_r_diameter/2000])
        idx_wheels = np.argmax(r_wheels)

        # Radius of wheel, brake and rim
        r_wheel = r_wheels[idx_wheels]                                  # in mm
        if idx_wheels == 0:
            r_rim = vehicle.dimensions.CX.rim_diameter_f_inch * 25.4/2000   # in m
            r_brake = vehicle.dimensions.CX.brake_disc_f_diameter/2000      # in m
        else:
            r_rim = vehicle.dimensions.CX.rim_diameter_r_inch * 25.4 / 2000  # in m
            r_brake = vehicle.dimensions.CX.brake_disc_r_diameter / 2000  # in m

        # inertia of 4 tires and 4 rims in kg m^2
        J_tires = 0.5 * m_wheels * (math.pow(r_wheel, 2) + math.pow(r_rim, 2))  # Simplified as hollow cylinder with Ri=r_rim and Ro=R_tire
        J_rims = 0.5 * m_rims * math.pow(r_rim, 2)                              # Simplified as filled cylinder with R=Rrim
        J_brakes = 0.5 * m_brakes * math.pow(r_brake, 2)                        # Simplified as filled cylinder with R=rRbrake
        # endregion

        # region [2.4] Calculate the mass inertia factor
        # addition of inertia wheels + front motor + rear motor to get total reduced inertia in kg m^2
        J_red = J_red['front'] + J_red['rear'] + J_tires + J_rims + J_brakes + J_gearbox['front'] + J_gearbox['rear']

        # rotating mass factor [-]
        eps = J_red/(vehicle.masses.vehicle_empty_weight_EU_sim * math.pow(vehicle.wheels.r_dyn/1000, 2))

        # e_i value [-]
        e_i = eps + 1
        # endregion

        # region [2.5] Assign Calculated Outputs
        setattr(vehicle.wheels, 'J_tires', J_tires)
        setattr(vehicle.wheels, 'J_rims', J_rims)
        setattr(vehicle.wheels, 'J_brakes', J_brakes)
        setattr(vehicle.wheels, 'm_wheels', m_wheels)
        # endregion
    # endregion

    # region [3] Assign mass inertia factor
    setattr(vehicle.LDS.parameters, 'e_i', e_i)
    # endregion
    return vehicle
