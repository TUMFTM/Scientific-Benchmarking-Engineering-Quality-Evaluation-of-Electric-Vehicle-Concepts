"""
Description: This function calculates the weight of the main vehicle modules. The
             vehicle is divided in 7 main modules, and each one of them is modeled
             separately using empirical models.

             All the models were first created in the work of Romano (2),
             and then further detailed in another publication (3) and in
             the Ph.D. thesis (1). A complete overview of the models is available at the
             Appendix E and at the chapter 3.5 of the Ph. D thesis (1)
------------
Sources: (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", Technical University of Munich, Institute of Automotive Technology, 2022
         (2) A. Romano, „Data-based Analysis for Parametric Weight Estimation of new BEV Concepts,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
         (3) L. Nicoletti, A. Romano, A. König, P. Köhler, M. Heinrich and M. Lienkamp, „An Estimation of the Lightweight Potential of Battery Electric Vehicles,“ Energies, vol. 14, no. 15, p. 4655, 2021, DOI: 10.3390/en14154655.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The vehicle structure updated with the mass of all the modules
        and components of the vehicle as well as the vehicle empty and gross mass
------------

Implementation
[0] Import modules, classes and functions
[1] Calculate chassis weights
[2] Calculate powertrain weight
[3] Calculate exterior weight
[4] Calculate interior weight
[5] Calculate Electrical weight
[6] Calculate frame weight
[7] Calculate accessories weight
[8] Calculate the total vehicle weight
------------
"""

# region [0] Import modules, classes and functions
# Import functions
from .calc_chassis_weight import calc_chassis_weight
from .calc_powertrain_weight import calc_powertrain_weight
from .calc_exterior_weight import calc_exterior_weight
from .calc_interior_weight import calc_interior_weight
from .calc_EE_weight import calc_EE_weight
from .calc_frame_weight import calc_frame_weight
from .calc_accessories_weight import calc_accessories_weight
from .calc_vehicle_total_weight import calc_vehicle_total_weight
# Import modules
# endregion


def calc_vehicle_weight(vehicle, parameters):
    # region [1] Calculate chassis weights
    # Calculate weight of the chassis components (brakes, brake calipers, brake pads, rims, tires ...)
    vehicle, parameters = calc_chassis_weight(vehicle, parameters)
    # endregion

    # region [2] Calculate powertrain weight
    # Calculate weight of the powertrain components (battery, electric machines, gearboxes ...)
    vehicle, parameters = calc_powertrain_weight(vehicle, parameters)
    # endregion

    # region [3] Calculate exterior weight
    # Calculate weight of the exterior components (closures, bumpers, lights, windshield, windows ...)
    vehicle, parameters = calc_exterior_weight(vehicle, parameters)
    # endregion

    # region [4] Calculate interior weight
    # Calculate weight of the interior components (airbags, center console, door panels, HVAC, instrument panel,...)
    vehicle, parameters = calc_interior_weight(vehicle, parameters)
    # endregion

    # region [5] Calculate Electrical weight
    # Calculate weight of the EE components (LV and HV network)
    vehicle, parameters = calc_EE_weight(vehicle, parameters)
    # endregion

    # region [6] Calculate frame weight
    # Calculate weight of the frame components (BIW and further frame components)
    vehicle, parameters = calc_frame_weight(vehicle, parameters)
    # endregion

    # region [7] Calculate accessories weight
    # Calculate weight of the accessories (ADAS, emergency equipment ...)
    vehicle, parameters = calc_accessories_weight(vehicle, parameters)
    # endregion

    # region [8] Calculate the total vehicle weight
    vehicle, parameters = calc_vehicle_total_weight(vehicle, parameters)
    # endregion

    return vehicle, parameters
