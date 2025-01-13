"""
Description: The basis is a basic machine from a white paper. This basic machine is adapted to the torque of
             the real machine using a scaling factor. The scaling factor can then be used to calculate the
             basic dimensions of the simulated machine.

------------
Sources: (1) P. Köhler, „Semi-physikalische Modellierung von Antriebsstrangkomponenten für Elektrofahrzeuge,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021
         (2) MDL, "Performance Analysis of Electric Motor Technologies for an Electric Vehicle Powertrain", White Paper, 2019
         (3) Pries and Hofmann, "Magnetic and thermal scaling of electric machines", 2013
         (4) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", P. D. Thesis, Technical University of Munich, Institute of Automotive Technology, 2022
         (5) Rosenberger et al., "Scientific benchmarking: Engineering quality evaluation of electric vehicle concepts", e-Prime - Advances in Electrical Engineering, Electronics and Energy 9, 2024
         (6) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
------------
Input: vehicle: Stores the calculated component volumes and masses
       Parameters: Stores the constant values and regressions for volume and mass models
       key: Key describing the concerned axles (front or rear)
------------
Output: Diameter and length of stator and machine (in mm)
------------
Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Calculate machine dimensions
[3] Output Assignment
------------
"""

# region [0] Import modules, classes and functions
# import modules
import math
# import functions
# endregion


def calc_EM_dimension(vehicle, parameters, key):
    # region [1] Assign Inputs
    # Define e-machine class
    e_machine = vehicle.e_machine[key]

    # Load empirical parameters for the dimension
    CX_house_thick = parameters.e_machine.CX.housing_thickness          # Machine housing thickness in mm[1, p.46]
    CX_house_rib_thick = parameters.e_machine.CX.housing_rib_thickness  # Thickness of machine housing ribs in mm[1, p. 46]
    EY_stat_to_mach = parameters.e_machine.EY.stator_to_machine_length  # Difference between stator length and total motor length in mm[1, p.46]

    e_machine_type = e_machine.type                                     # Type of the E-machine (PSM, ASM, FSM)

    # Empirical length- diameter- ratio of the stator (dimensionless) depending on machine type [1, p.46]
    ratios = parameters.e_machine.stator_ratio
    match e_machine_type:
        case 'PSM':
            stator_ratio = ratios.PMSM
        case 'ASM':
            stator_ratio = ratios.IM
        case 'FSM':
            stator_ratio = ratios.SSM
        case _:
            stator_ratio = ratios.PMSM

    # Load the reference diameter, and the scaling factor
    reference_diameter = parameters.e_machine.EY.diameter_reference  # Stator diameter of the referenced e-machine [2]
    k_length = e_machine.k_length                                    # Previously calculated scaling factor [6, p. 46-48]
    # endregion

    # region [2] Calculate machine dimensions
    # A visualization of the dimensional chain is documented in the Appendix of [4, p. xlii-xliv]

    # Compute the stator diameter of the e-machine in mm [3, 5]
    CX_stator_diameter = k_length * reference_diameter

    # Length of the stator in mm [1, p. 43]
    CY_stator_length = stator_ratio * CX_stator_diameter

    # Volume of the stator in L [1, p.43]
    volume_stator = (math.pi/4) * CY_stator_length * math.pow(CX_stator_diameter, 2) * math.pow(10, -6)

    # Include the dimensions of the housing to estimate the total machine dimensions [1, p.43]
    # Total e machine diameter in mm
    e_machine_diameter = CX_stator_diameter + 2 * CX_house_thick + 2 * CX_house_rib_thick
    #  Total e machine length in mm
    e_machine_length = CY_stator_length + EY_stat_to_mach
    # endregion

    # region [3] Assign Outputs
    # Length of the entire machine(includes housings and covers) in mm
    setattr(e_machine, 'CY_e_machine_length', e_machine_length)
    # Diameter of the entire machine(includes housings ribs and thickness) in mm
    setattr(e_machine, 'CX_e_machine_diameter', e_machine_diameter)

    setattr(e_machine, 'CX_stator_diameter', CX_stator_diameter)     # Diameter of the stator in mm
    setattr(e_machine, 'CY_stator_length', CY_stator_length)         # Length of the stator in mm
    setattr(e_machine, 'volume_stator', volume_stator)               # Volume of the stator in L
    # endregion

    return e_machine
