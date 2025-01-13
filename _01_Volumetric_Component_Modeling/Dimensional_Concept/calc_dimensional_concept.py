"""
Description:    This function calculates the dimensions of the interior design of a battery electric vehicle
                Therefore it is important to have a common knowledge about the in the SAE norms described
                dimensions and angles of the passenger department
------------
Sources:    (1) SAE J1100 - https://www.sae.org/standards/content/j1100_200911/
            (2) SAE J4004 - Positioning the H-Point Design Tool - Seating Reference Point and Seat Track Length, 2008.
            (3) SAE J1052 - Motor Vehicle Driver and Passenger Head Position, 2010.
            (4) SAE J941 - Motor Vehicle Drivers’ Eye Locations, 2010.
            (5) UN/ECE regulation number 125 (ECE R125)
            Further information can be found at the Chapter 3.4.3 of the Ph.D thesis:
            (6) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Design", FTM, 2022
------------
Input:   vehicle: Class element, which stores all the vehicle information
         parameters: Class element, which stores all necessary computation parameters
------------
Output:  Updated classes vehicle and parameters with the dimensions of the passenger compartment
------------
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import numpy as np
# Import classes
# Import methods
from .calc_ground_clearance import calc_ground_clearance
from .calc_passenger_compartment_z import calc_passenger_compartment_z
from .calc_passenger_compartment_x_first_seatrow import calc_passenger_compartment_x_first_seatrow
from .calc_passenger_compartment_x_second_seatrow import calc_passenger_compartment_x_second_seatrow
from .calc_passenger_compartment_y import calc_passenger_compartment_y
# endregion


def calc_dimensional_concept(vehicle, parameters):
    # Check if the H156 measure is given
    H156 = vehicle.dimensions.GZ.H156
    if np.isnan(H156):
        vehicle, parameters = calc_ground_clearance(vehicle, parameters)

    # Calc the dimensions in z-direction of the passenger compartment
    vehicle, parameters = calc_passenger_compartment_z(vehicle, parameters)

    # Calc the dimensions in x-direction of the first seatrow
    vehicle, parameters = calc_passenger_compartment_x_first_seatrow(vehicle, parameters)

    # Calc the dimensions in x-direction of the second seatrow
    vehicle, parameters = calc_passenger_compartment_x_second_seatrow(vehicle, parameters)

    # Calc the dimensions in y-direction of the passenger compartment
    vehicle, parameters = calc_passenger_compartment_y(vehicle, parameters)
    return vehicle, parameters
