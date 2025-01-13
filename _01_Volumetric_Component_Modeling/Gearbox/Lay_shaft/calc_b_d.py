"""
Description:    This function computes initial gear dimensions for the given transmission
                ratio according to empirical axle distance and gear width factors.
------------
Sources:    (1) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
            (2) Naunheimer, "Fahrzeuggetriebe", Springer Vieweg, 2019, ISBN: 978-3-662-58883-3
            (3) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  First rough dimensioning of the gearbox gears
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Calculation of initial wheel dimensions
[3] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
# Import classes
# Import methods
# endregion


def calc_b_d(gearbox, parameters):
    # region [1]: Initialization of required values
    # Gearbox Values
    i_12 = gearbox.results.i_12         # Transmission ratio of first stage
    i_34 = gearbox.results.i_34         # Transmission ratio of second stage

    T_max = gearbox.Input.T_max * 1000  # Maximum Input torque[Nmm]
    m_n_1_max = gearbox.gears_12.m_n_1  # Maximum normal module of first stage(Zaehringer p. 105) [mm]

    # Empirical axle distance and gear width calculation factors for each stage(Koehler, p. 42)
    K_a_1 = parameters.gearbox.CalcFactors.K_a_1    # Axle distance factor for first stage
    K_a_2 = parameters.gearbox.CalcFactors.K_a_2    # Axle distance factor for second stage
    K_b_1 = parameters.gearbox.CalcFactors.K_b_1    # Gear width factor for first stage
    K_b_2 = parameters.gearbox.CalcFactors.K_b_2    # Gear width factor for second stage
    # endregion

    # region [2]: Calculation of initial wheel dimensions
    # Calculation of initial distance between first and second shaft with
    # approximation of pitting load capacity (Naunheimer, p.288)
    a_12 = K_a_1 * ((T_max * (i_12+1) ** 4) / i_12) ** (1 / 3)

    # Calculation of pitch diameter gear 1 in mm (Naunheimer, p.286)
    d_1 = (2 * a_12) / (1+i_12)

    # Calculation of distance between second and third shaft in mm as for first stage
    a_23 = K_a_2 * ((T_max * i_12 * (i_34+1) ** 4) / i_34) ** (1 / 3)

    # Switch for parallel or coaxial in- and output shafts
    if gearbox.Input.axles != 'coaxial':
        # Calculation of pitch diameter gear 2 in mm (Zaehringer, p. 25)
        d_2 = i_12 * d_1

        # Calculation of gear 3 & 4 pitch diameters with different axle distance as first stage
        d_3 = (2 * a_23) / (1 + i_34)
        d_4 = i_34 * d_3

    else:

        d_sh_3 = gearbox.shafts.d_sh_3  # Diameter of output shaft for coaxial gearbox configuration
        # Check if minimum pitch diameter of gear 1 fits around output shaft with 2 mm of circumferential clearance
        # and 2.6 mm of maximum normal module of stage 1
        if d_1 < d_sh_3 + 4 + 8 + 2 * 4.25 * m_n_1_max:
            d_1 = d_sh_3 + 4 + 8 + 2 * 4.25 * m_n_1_max
            d_2 = i_12 * d_1
            a_12 = 0.5 * (d_1 + d_2)

        # Selection of the larger axle distance for initial calculations
        a_12 = max(a_12, a_23)
        d_1 = (2 * a_12) / (1 + i_12)
        d_2 = i_12 * d_1

        # Calculation of gear 3 & 4 pitch diameters with same axle distance as first stage
        d_3 = (2 * a_12) / (1 + i_34)
        d_4 = i_34 * d_3
        a_23 = a_12

    # Calculation of width of gears 1 / 2 and 3 / 4 in mm with approximation formula (Naunheimer, p.289)
    b_1 = K_b_1 * ((T_max * (i_12 + 1)) / ((d_1 ** 2) * i_12))
    b_3 = K_b_2 * ((T_max * i_12 * (i_34 + 1)) / ((d_3 ** 2) * i_34))
    # endregion

    # region [3]: Output Assignment
    setattr(gearbox.gears_12, 'd_1', d_1)   # Wheel 1 pitch diameter[mm]
    setattr(gearbox.gears_12, 'd_2', d_2)   # Wheel 2 pitch diameter[mm]
    setattr(gearbox.gears_12, 'b_1', b_1)   # First stage gears' width [mm]

    setattr(gearbox.gears_34, 'b_3', b_3)   # Second stage gears' width [mm]
    setattr(gearbox.gears_34, 'd_3', d_3)   # Wheel 3 pitch diameter[mm]
    setattr(gearbox.gears_34, 'd_4', d_4)   # Wheel 4 pitch diameter[mm]

    setattr(gearbox.results, 'a_12', a_12)  # Distance between shafts 1 & 2[mm]
    setattr(gearbox.results, 'a_23', a_23)  # Distance between shafts 2 & 3[mm]
    # endregion

    return gearbox
