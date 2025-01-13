"""
Description: This function conducts a Longitudinal dynamic simulation, which is
              used for the sizing of the powertrain components (battery,
              electric machines, gearbox). The simulation was created in
              different theses, which are listed in the Sources section.
              A simplified overview of the simulation and how it is integrated in the mass of the vehicle, and the position of the components
              the tool can be found at Chapter 3.3 of (1).
------------
Sources: (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", Technical University of Munich, Institute of Automotive Technology, 2022
          The following theses developed and improved the longitudinal simulation
         (2) K. Moller, „Validierung einer MATLAB Längsdynamiksimulation für die Auslegung von Elektrofahrzeugen,“ Bachelor thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2020.
         (3) K. Moller, „Antriebsstrangmodellierung zur Optimierung autonomer Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
         (4) R. Hefele, „Implementierung einer MATLAB Längsdynamiksimulation für Elektrofahrzeuge,“Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2019.
         The simulation presented here is based on the following open-source repository
         (5) A. König, L. Nicoletti and K. Moller. „Modular Quasi Static Longitudinal Simulation for BEV,“ 2020. [Online]. Available: https://github.com/TUMFTM/Modular-Quasi-Static- Longitudinal-Simulation-for-BEV [visited on 01/07/2020].
         More information regarding the open-source repository is given at:
         (6) A. König, L. Nicoletti, S. Kalt, K. Moller, A. Koch and M. Lienkamp, „An Open-Source Modular Quasi-Static Longitudinal Simulation for Full Electric Vehicles,“ in 15th International Conference on Ecological Vehicles and Renewable Energies, Monte-Carlo, Monaco, 2020, pp. 1–9, DOI: 10.1109/EVER48776.2020.9242981.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output:  The vehicle structure updated with:
        -the vehicle consumption
        -the resistance forces
        -the achievable range
        -the results of acceleration and max speed simulation
------------

Implementation
[0] Import modules, classes and functions
[1] Acceleration simulation
[2] Top speed simulation
[3] Calculate the energy consumption
"""

# region [0] Import modules, classes and functions
# Import modules
# Import functions
from _02_LDS.Functions.calc_functions import calc_e_i
from _02_LDS.Functions.calc_functions import calc_max_speed
from _02_LDS.Functions.calc_functions import calc_acceleration
from _02_LDS.Functions.calc_functions import calc_consumption

# endregion


def calc_longitudinal_simulation(vehicle, parameters):

    # region [1] Acceleration simulation
    # This function calculates the moment of inertia for the rotating components of the vehicle
    vehicle = calc_e_i(vehicle, parameters)

    # This function calculates the achievable acceleration time for the given vehicle
    vehicle = calc_acceleration(vehicle, parameters)
    # endregion

    # region [2] Top speed simulation
    vehicle = calc_max_speed(vehicle, parameters)
    # endregion

    direction = ['sim_cons', 'sim_range']

    for directory in direction:
        # region [3] Calculate the energy consumption
        vehicle = calc_consumption(vehicle, parameters, directory)
        # endregion

    return vehicle, parameters
