"""
Description: This function calculates the dimensions of the electric machines, of the
             gearbox and of the battery.
             More information to this regard can be found in (1) and Chapters 4.3, 4.4, 4.5, 4.6 of (2)
             Many implementations are derived from the work of Nicoletti and can be found in the
             Chapters 3.4.4, 3.4.5, 3.4.6, and 3.5.5 of (3)
------------
Sources: (1) Rosenberger et al., "Scientific benchmarking: Engineering quality evaluation of electric vehicle concepts", e-Prime - Advances in Electrical Engineering, Electronics and Energy 9, 2024
         (2) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
         (3) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", P. D. Thesis, Technical University of Munich, Institute of Automotive Technology, 2022
------------
Input:  vehicle: Class element, which stores all values of the vehicle
        parameters: Class element, which stores all necessary computation parameters
------------
Output: The Main output of this function (and its sub-functions are):
          -The size of the battery and its components as well as the simulated battery capacity
          -The size of the gearbox and its components
          -The size of the electric machine(s) and its components
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Scale the initialized e-machine based on the desired outputs
[2] Compute the dimension of the e-machine
[3] Compute the dimension of the gearbox
[4] Compute the position of the gearbox
[5] Compute the position of the driveshaft
[6] Compute the position of the E-Machine
[7] Calc the available space of the battery in the underfloor
[8] Calculate the available space under the front seat row
[9] Calc the available space of the battery in the second row
[10] Calc the available space of the battery in the tunnel
[11] Compute the dimensions and fillings of the battery
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
# Import classes
# Import methods
from _01_Volumetric_Component_Modeling.E_Machine import scale_e_machine
from _01_Volumetric_Component_Modeling.E_Machine import calc_EM_dimension
from _01_Volumetric_Component_Modeling.E_Machine import calc_EM_position
from _01_Volumetric_Component_Modeling.Gearbox import calc_gearbox_dimension
from _01_Volumetric_Component_Modeling.Gearbox import calc_gearbox_position
from _01_Volumetric_Component_Modeling.E_Machine import calc_driveshaft_position
from _01_Volumetric_Component_Modeling.Battery import calc_battery_space_dimensions_underfloor
from _01_Volumetric_Component_Modeling.Battery import calc_battery_space_dimensions_underfloor_lowfloor
from _01_Volumetric_Component_Modeling.Battery import calc_battery_space_dimensions_secondrow
from _01_Volumetric_Component_Modeling.Battery import calc_battery_space_dimensions_tunnel
from _01_Volumetric_Component_Modeling.Battery import calc_battery_electric_scheme
# endregion


def calc_powertrain_dimensions(vehicle, parameters):
    for key, value in vehicle.topology.filled_axles.items():
        if value is True:
            # region [1] Scale the initialized e-machine based on the desired outputs
            vehicle.e_machine[key] = scale_e_machine(vehicle, key)
            # endregion

            # region [2] Compute the dimension of the e-machine
            vehicle.e_machine[key] = calc_EM_dimension(vehicle, parameters, key)
            # endregion

            # region [3] Compute the dimension of the gearbox
            vehicle.gearbox[key] = calc_gearbox_dimension(vehicle, parameters, key)
            # endregion

            # region [4] Compute the position of the gearbox
            vehicle.gearbox[key] = calc_gearbox_position(vehicle, parameters, key)
            # endregion

            # region [5] Compute the position of the driveshaft
            vehicle.gearbox[key] = calc_driveshaft_position(vehicle, key)
            # endregion

            # region [6] Compute the position of the E-Machine
            vehicle.e_machine[key] = calc_EM_position(vehicle.e_machine[key], vehicle.gearbox[key])
            # endregion

    # region [7] Calc the available space of the battery in the underfloor
    vehicle = calc_battery_space_dimensions_underfloor(vehicle, parameters)
    # endregion

    # region [8] Calculate the available space under the front seat row
    if vehicle.topology.battery_topology.lower() == 'lowfloor':
        vehicle = calc_battery_space_dimensions_underfloor_lowfloor(vehicle, parameters)
    # endregion

    # region [9] Calc the available space of the battery in the second row
    vehicle = calc_battery_space_dimensions_secondrow(vehicle, parameters)
    # endregion

    # region [10] Calc the available space of the battery in the tunnel
    vehicle = calc_battery_space_dimensions_tunnel(vehicle, parameters)
    # endregion

    # region [11] Compute the dimensions and fillings of the battery
    vehicle = calc_battery_electric_scheme(vehicle, parameters)
    # endregion

    return vehicle, parameters
