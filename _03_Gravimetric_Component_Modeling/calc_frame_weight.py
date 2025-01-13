"""
Description: This function calculates the BIW weight. Toggle alu_perc in initialize_weight_options
             ALL THE GIVEN MASSES ARE CALCULATED IN KG

             All the models were first created in the work of Romano (2),
             and then further detailed in another publication (3) and in
             the Ph.D. thesis (1). A complete overview of the models is available at the
             Appendix E and at the chapter 3.5 of the Ph. D thesis (1)
------------
Sources: (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", Technical University of Munich, Institute of Automotive Technology, 2022
         (2) A. Romano, „Data-based Analysis for Parametric Weight Estimation of new BEV Concepts,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
         (3) L. Nicoletti, A. Romano, A. König, P. Köhler, M. Heinrich and M. Lienkamp, „An Estimation of the Lightweight Potential of Battery Electric Vehicles,“ Energies, vol. 14, no. 15, p. 4655, 2021, DOI: 10.3390/en14154655.
         (4) S. Fuchs, Verfahren zur parameterbasierten Gewichtsabschätzung neuer Fahrzeugkonzepte, Ph.D. Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2014.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output:  The vehicle structure updated with the mass of the frame components
------------

Implementation
[0] Import modules, classes and functions
[1] Initialize variables
[2] BIW weight
[3] Weight of other frame components
[4] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
import math
# endregion


def calc_frame_weight(vehicle, parameters):
    # region [1] Initialize variables
    # Vehicle measurements
    gross_weight = vehicle.masses.vehicle_max_weight            # Maximum allowable mass in kg
    overhang_f = vehicle.dimensions.GX.vehicle_overhang_f       # in mm
    overhang_r = vehicle.dimensions.GX.vehicle_overhang_r       # in mm
    width = vehicle.dimensions.GY.vehicle_width                 # in mm
    height = vehicle.dimensions.GZ.vehicle_height               # in mm
    wheelbase = vehicle.dimensions.GX.wheelbase                 # in mm

    # Further vehicle data
    perc_alu = vehicle.masses.optional_extras.alu_perc_BIW      # in %
    frameform = vehicle.topology.frameform                      # SUV, Hatchback or Sedan

    # Regressions for the mass calculation of frame components
    regr_BIW_coeff = parameters.regr.mass.BIW.coefficients
    regr_other_frame_components_coeff = parameters.regr.mass.frame_elements.coefficients
    # endregion

    # region [2] BIW weight
    # Calculate substitute volume according to (4, p.39)
    if frameform.lower == 'sedan':
        subs_volume = ((0.5 * overhang_f + wheelbase + 2 * overhang_r/3) * width * height)/math.pow(10, 9)  # [m^3]
    else:
        subs_volume = ((0.5 * overhang_f + wheelbase + 3 * overhang_r/4) * width * height)/math.pow(10, 9)  # [m^3]

    # Calculate frame mass and assign outputs
    var1 = subs_volume * perc_alu/100
    var2 = subs_volume * (1 - perc_alu/100)

    # Calculate the weight of the Body in white
    BIW_weight = regr_BIW_coeff[0] + regr_BIW_coeff[1] * var1 + \
                 regr_BIW_coeff[2] * var2 + regr_BIW_coeff[3] * gross_weight

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if BIW_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The BIW mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)
    # endregion

    # region [3] Weight of other frame components
    # Calculate mass of other frame components besides BIW. This includes:
    # Front cross members, body reinforcements, sound insulation on body, aerodynamic screens, water draining system,
    # rocker panels, exterior pillar trims, roof trim and roof rack, running boards, seals, jack pads
    # for servicing, underbody protections.
    other_frame_components_weight = regr_other_frame_components_coeff[0] + \
                                    regr_other_frame_components_coeff[1] * subs_volume

    # Check that the resulting masses are not negative (this may happen if the inputs are outside of the regression confidence interval)
    if other_frame_components_weight < 0:
        # Define errorlog
        errorlog_list = vehicle.errorlog
        text_errorlog = 'The other frame components mass is negative. Please check for errors in the inputs or in the mass calculation'
        print(text_errorlog)
        errorlog_list.append(text_errorlog)
        setattr(vehicle, 'errorlog', errorlog_list)
    # endregion

    #  region [4] Assign outputs
    # All outputs in kg
    setattr(vehicle.masses.frame, 'BIW_weight', BIW_weight)
    setattr(vehicle.masses.frame, 'other_frame_components_weight', other_frame_components_weight)
    # endregion

    return vehicle, parameters
