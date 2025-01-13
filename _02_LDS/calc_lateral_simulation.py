"""
Description: This function conducts a lateral dynamics simulation in the form of calculating the slalom
             speed as a cumulative evaluation variable for assessing lateral dynamics.
------------
Sources: (1) S. Bogdan, "Weiterentwicklung eines Simulationsmodells zur Bewertung von Elektrofahrzeugkonzepten im Bereich Querdynamik", Semester thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2024.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
       benchmarking: Stores the Benchmarking values of the corresponding vehicle
------------
Output:  The vehicle structure updated with the simulated slalom velocity
------------

Implementation
[0] Import modules, classes and functions
[1] Slalom velocity simulation
"""

# region [0] Import modules, classes and functions
# Import modules
# Import functions
from _02_LDS.Functions.calc_functions import calc_slalom
# endregion


def calc_lateral_simulation(vehicle, parameters, benchmarking):

    # region [1] Evaluation of regression formulas
    # This function calculates the slalom velocity for the given vehicle based on the regression formula
    vehicle = calc_slalom(vehicle, parameters, benchmarking)

    return vehicle
