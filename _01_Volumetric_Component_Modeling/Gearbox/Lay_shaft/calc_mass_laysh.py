"""
Description:    This function computes the mass of the gearbox and its components in kg according to Zaehringer, starting p. 67
------------
Sources:    (1) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
            (2) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
            (3) Naunheimer, "Fahrzeuggetriebe", Springer Vieweg, 2019, ISBN: 978-3-662-58883-3
            (4) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Master Thesis, TUM, 2020
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  Mass of the gearbox and all its subcomponents
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Masses of shafts, bearings and gears
[2.1] Shaft 1
[2.2] Shaft 2
[2.3] Differential shaft (shaft 3)
[3] Mass of gearbox housing (1, pp. 74)
[4] Total mass of gearbox in kg
[5] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
# Import classes
# Import methods
# endregion


def calc_mass_laysh(gearbox, parameters):
    # region [1]: Initialization of required values
    # Assign the result class from the gearbox class
    T_max = gearbox.Input.T_max                     # Maximum torque of el. motor [Nm]
    i_tot = gearbox.results.i_tot                   # Total transmission ratio [-]
    a_12 = gearbox.results.a_12                     # Distance between shafts 1&2 [mm]
    a_23 = gearbox.results.a_23                     # Distance between shafts 2&3 [mm]
    t_gearbox = gearbox.dimension_house.t_gearbox   # Thickness of the gearbox housing in vehicles y-direction

    # Assign necessary parameter values
    rho_alu = parameters.gearbox.MatProp.rho_alu/math.pow(10, 9)    # Density of housing material AlSi9Cu3 (3, p. 517) [kg/m^3]
    rho_gear = parameters.gearbox.MatProp.rho_gear/math.pow(10, 9)  # Density 16MnCr5 (1, p. 67) [kg/m^3]
    t_housing = parameters.gearbox.ConstDim.t_housing               # Housing thickness (1, p. 64) [mm]
    d_housing = parameters.gearbox.ConstDim.d_housing               # Distance between gears and housing (1, p. 64) [mm]
    b_seal = parameters.gearbox.ConstDim.b_seal                     # Width of seals on output shafts (mean of database) (4, p. 61) [mm]
    d_diffbolt = parameters.gearbox.ConstDim.d_diffbolt             # Diameter of differential bolt (1, p. 55) [mm]
    b_gap = parameters.gearbox.ConstDim.b_gap                       # Gap between components on the shafts (1, p. 64) [mm]
    b_park = parameters.gearbox.ConstDim.b_park                     # Width of parking gear (1, p. 64) [mm]

    # Assign values of the first transmission gears (gears 1 and 2)
    m_n_1 = gearbox.gears_12.m_n_1                  # Normal module of first stage [mm]
    b_1 = gearbox.gears_12.b_1                      # Width of wheels 1&2 [mm]
    d_1 = gearbox.gears_12.d_1                      # Pitch diameter of wheel 1 [mm]
    d_2 = gearbox.gears_12.d_2                      # Pitch diameter of wheel 2 [mm]
    d_f2 = gearbox.gears_12.d_f2                    # Root diameter of wheel 2 [mm]
    d_a1 = gearbox.gears_12.d_a1                    # Outer diameter of wheel 1 [mm]
    d_a2 = gearbox.gears_12.d_a2                    # Outer diameter of wheel 2 [mm]

    # Assign values of the second transmission gears
    m_n_3 = gearbox.gears_34.m_n_3                  # Normal module of second stage [mm]
    b_3 = gearbox.gears_34.b_3                      # Width of wheels 3&4 [mm]
    d_3 = gearbox.gears_34.d_3                      # Pitch diameter of wheel 3 [mm]
    d_4 = gearbox.gears_34.d_4                      # Pitch diameter of wheel 4 [mm]
    d_f4 = gearbox.gears_34.d_f4                    # Root diameter of wheel 4 [mm]
    d_a4 = gearbox.gears_34.d_a4                    # Outer diameter of wheel 4 [mm]

    # Assign values of the shafts
    d_inn_1 = gearbox.shafts.d_inn_1                # Inner diameter of hollow shaft 1 [mm]
    d_inn_2 = gearbox.shafts.d_inn_2                # Inner diameter of hollow shaft 2 [mm]
    d_sh_3 = gearbox.shafts.d_sh_3                  # Outer diameter of output shaft [mm]
    d_1_max = gearbox.shafts.d_1_max                # Maximum diameter of components on shaft 1 [mm]

    # Assign values of the first shaft bearings (bearing A and B)
    b_A = gearbox.bearings_1.b_A                    # Width of bearing A [mm]
    b_B = gearbox.bearings_1.b_B                    # Width of bearing B [mm]
    d_sh_A = gearbox.bearings_1.d_sh_A              # Inner diameter of bearing A [mm]
    d_sh_B = gearbox.bearings_1.d_sh_B              # Inner diameter of bearing B [mm]
    d_A_A = gearbox.bearings_1.d_A_A                # Outer diameter of bearing A [mm]
    d_A_B = gearbox.bearings_1.d_A_B                # Outer diameter of bearing B [mm]
    m_A = gearbox.bearings_1.m_A                    # Mass of bearing A [kg]
    m_B = gearbox.bearings_1.m_B                    # Mass of bearing B [kg]

    # Assign values of the second shaft bearings (bearing C and D)
    b_C = gearbox.bearings_2.b_C                    # Width of bearing C [mm]
    b_D = gearbox.bearings_2.b_D                    # Width of bearing D [mm]
    d_sh_C = gearbox.bearings_2.d_sh_C              # Inner diameter of bearing C [mm]
    d_sh_D = gearbox.bearings_2.d_sh_D              # Inner diameter of bearing D [mm]
    d_1_C = gearbox.bearings_2.d_1_C                # Outer diameter of Cs inner bearing ring [mm]
    d_A_C = gearbox.bearings_2.d_A_C                # Outer diameter of bearing C [mm]
    d_A_D = gearbox.bearings_2.d_A_D                # Outer diameter of bearing D [mm]
    m_C = gearbox.bearings_2.m_C                    # Mass of bearing C [kg]
    m_D = gearbox.bearings_2.m_D                    # Mass of bearing D [kg]

    # Assign values of the third shaft bearings (bearing E and F)
    b_E = gearbox.bearings_3.b_E                    # Width of bearing E [mm]
    b_F = gearbox.bearings_3.b_F                    # Width of bearing F [mm]
    d_sh_E = gearbox.bearings_3.d_sh_E              # Inner diameter of bearing E [mm]
    d_sh_F = gearbox.bearings_3.d_sh_F              # Inner diameter of bearing F [mm]
    d_1_E = gearbox.bearings_3.d_1_E                # Outer diameter of Es inner bearing ring [mm]
    d_1_F = gearbox.bearings_3.d_1_F                # Outer diameter of Fs inner bearing ring [mm]
    d_A_E = gearbox.bearings_3.d_A_E                # Outer diameter of bearing E [mm]
    d_A_F = gearbox.bearings_3.d_A_F                # Outer diameter of bearing F [mm]
    m_E = gearbox.bearings_3.m_E                    # Mass of bearing E [kg]
    m_F = gearbox.bearings_3.m_F                    # Mass of bearing F [kg]

    # Assign necessary parameters for the calculations
    opt_gears = gearbox.Input.opt_gears                             # Optimization goal (Height/Length/Mass/Manual)
    diff_orientation = gearbox.differential.diff_orientation        # Orientation of the differential

    # Assign the regression
    regr_m_diff_coeff = parameters.regr.gearbox.m_diff.coefficients  # Regression formula for the differential mass in kg ([1], p. 47)

    # Assign differential values
    if gearbox.Input.num_EM == 1:
        b_diffcage = gearbox.differential.b_diffcage        # Width of differential cage [mm]
        d_diffcage = gearbox.differential.d_diffcage        # Diameter of differential cage [mm]
        b_bev = gearbox.differential.b_bev                  # Width of bevel gears in differential [mm]
        d_bev_l = gearbox.differential.d_bev_l              # Diameter of larger bevel gears in differential [mm]
        d_bev_s = gearbox.differential.d_bev_s              # Diameter of smaller bevel gears in differential [mm]

    else:   # Assign Variables as empty to avoid Pycharm warnings, because for two E-Machine no differentials are used
        b_diffcage = 0
        d_diffcage = 0
        b_bev = 0
        d_bev_l = 0
        d_bev_s = 0

    # Set general attributes to zero to avoid Pycharm warnings
    D_tot = 0
    D_4 = 0
    m_diff_emp = 0
    m_diffcage = 0
    m_diffbolt = 0
    m_bevels = 0
    m_s3 = 0
    # endregion

    # region [2]: Masses of shafts, bearings and gears
    # region [2.1]: Shaft 1
    # Volumes of first wheel and shaft in mm^3
    V_gear_1 = (math.pow(d_1/2, 2) - math.pow(d_inn_1/2, 2)) * math.pi * b_1
    V_shaft_1 = ((b_seal + b_A + b_gap + b_park + b_gap) * (math.pow(d_sh_A/2, 2) - math.pow(d_inn_1/2, 2)) *
                        math.pi) + ((b_B + b_gap) * (math.pow(d_sh_B/2, 2) - math.pow(d_inn_1/2, 2)) * math.pi)

    # Masses of first wheel and shaft in kg
    m_g1 = V_gear_1 * rho_gear
    m_s1 = V_shaft_1 * rho_gear

    # Total mass of shaft 1 with components in kg
    m_1 = m_g1 + m_s1 + m_A + m_B
    # endregion

    # region [2.2]: Shaft 2
    # Volumes of wheels 2&3 in mm^3 (gear web thickness of wheel 2 is decreased if diameter is large enough) (2, p. 69)
    if d_f2 - 6 * m_n_1 - d_1_C > 40:

        V_gear_23 = ((math.pow(0.5 * d_2, 2) - math.pow(0.5 * d_inn_2, 2)) * math.pi * b_1) + \
                    ((math.pow(0.5 * d_3, 2) - math.pow(0.5 * d_inn_2, 2)) * math.pi * b_3) - \
                    (b_1 * 0.6 * math.pi * (math.pow(0.5*(d_f2 - 6*m_n_1), 2) - math.pow(d_1_C/2, 2)))
    else:

        V_gear_23 = ((math.pow(0.5 * d_2, 2) - math.pow(0.5 * d_inn_2, 2)) * math.pi * b_1) + \
                    ((math.pow(0.5 * d_3, 2) - math.pow(0.5 * d_inn_2, 2)) * math.pi * b_3)

    # Volume of shaft 2 in mm^3 (longer shaft for coaxial lay-shaft design)
    if gearbox.Input.axles.lower() == 'parallel':   # parallel shaft configuration

        V_shaft_2 = ((b_C + b_gap) * (math.pow(d_sh_C/2, 2) - math.pow(d_inn_2/2, 2)) * math.pi) + \
                    ((b_gap + b_D) * (math.pow(d_sh_D/2, 2) - math.pow(d_inn_2/2, 2)) * math.pi) + \
                    b_gap * (math.pow(min(d_sh_C, d_sh_D), 2) - math.pow(d_inn_2/2, 2)) * math.pi

    else:                                           # coaxial configuration
        V_shaft_2 = ((b_C+b_gap) * (math.pow(d_sh_C/2, 2) - math.pow(d_inn_2/2, 2)) * math.pi) + \
                    ((b_gap+b_D) * (math.pow(d_sh_D/2, 2) - math.pow(d_inn_2/2, 2)) * math.pi) + \
                    ((b_gap + b_B + b_gap + b_E + b_gap) * (math.pow(min(d_sh_C, d_sh_D)/2, 2) - math.pow(d_inn_2/2, 2)) * math.pi)

    # Masses of wheels 2&3 and shaft 2 in kg
    m_g23 = V_gear_23 * rho_gear
    m_s2 = V_shaft_2 * rho_gear

    # Total mass of shaft 2 with components in kg
    m_2 = m_g23 + m_s2 + m_C + m_D
    # endregion

    # region [2.3]: Differential shaft (shaft 3)
    # Switch for calculation of third shaft with or without differential
    if gearbox.Input.num_EM == 1:
        # Volumes of wheel 4 in mm^3 (gear web thickness is decreased if diameter is large enough, Zaehringer, p. 69)
        if d_f4 - 6 * m_n_3 - d_diffcage > 40:

            V_gear_4 = (math.pow(0.5 * d_4, 2) * math.pi * b_3) -\
                       (math.pow(0.5 * d_sh_3 + 2, 2) * math.pi * (b_3 - (25 - b_bev))) - \
                       (math.pow(0.5 * d_sh_3 + 5, 2) * math.pi * (25 - b_bev)) - \
                       ((0.6 * b_3 * math.pi * math.pow(0.5 * d_f4 - 3 * m_n_3, 2)) -
                        (0.3 * b_3 * math.pi * (math.pow(0.5 * d_diffcage, 2) + math.pow(0.5 * d_1_F, 2))))
        else:

            V_gear_4 = (math.pow(0.5*d_4, 2) * math.pi * b_3) - \
                       (math.pow(0.5 * d_sh_3 + 2, 2) * math.pi * (b_3 - (25 - b_bev))) - \
                       (0.3 * b_3 * math.pi * (math.pow(0.5 * d_f4 - 3 * m_n_3, 2) - math.pow(0.5*d_1_F, 2)))

        # Mass of wheel 4 in kg
        m_g4 = V_gear_4 * rho_gear

        # Volumes of differential bolt in mm^3
        V_diffbolt = math.pow(0.5 * d_diffbolt, 2) * math.pi * d_diffcage

        # Larger bevel with flange for output shaft
        r = 0.5 * d_bev_l - b_bev                           # smaller radius of bevel gears in mm
        R = 0.5 * d_bev_l                                   # bigger radius of bevel gears in mm

        V_bev_l = math.pi/3 * b_bev * (math.pow(R, 2) + (R * r) + math.pow(r, 2)) + \
                  math.pow(d_sh_3/2 + 5, 2) * math.pi * (25 - b_bev) - math.pow(d_sh_3/2, 2) * math.pi * 25

        # Smaller bevel with addition of ball segments to bevel gears and subtraction of bores for diffbolt and output shaft
        r = 0.5 * (d_bev_s - b_bev)
        R = 0.5 * d_bev_l
        h = (math.sqrt(2) - 1)/2 * d_bev_s
        r1 = math.sqrt(2)/2 * d_bev_s

        V_bev_s = math.pi/3 * b_bev * (math.pow(R, 2) + (R * r) + math.pow(r, 2)) + \
                  (math.pi/3 * math.pow(h, 2) * (3 * r1 - h) - math.pow(0.5 * d_diffbolt, 2) * math.pi * (b_bev + h))

        # Total volume of bevel gears in mm^3
        V_bevels = 2 * V_bev_l + 2 * V_bev_s

        # Volumes of differential cage in mm^3, calculated with auxiliary volumes V1-V5 (r and R change!)
        # Cylinder with diameter d_diffcage and width of smaller bevels
        V1 = math.pow(d_diffcage/2, 2) * math.pi * d_bev_s

        # Truncated cone with diameter d_diffcage on one side and d_1_E on the other and length of 10 mm
        R = d_diffcage/2
        r = d_1_E/2
        length = 10
        V2 = math.pi/3 * length * (math.pow(R, 2) + (R * r) + math.pow(r, 2))

        # Cylinder with diameter of larger bevels plus ball segments on smaller bevels
        r = math.sqrt(2)/2 * d_bev_s
        R = 0.5 * d_bev_l
        V3 = math.pow(R, 2) * math.pi * d_bev_s + 2 * (math.pi/3 * math.pow(h, 2) * (3 * r - h))

        # Opening for montage of bevel gears (2*120 deg)
        V4 = 2/3 * ((math.pow(0.5 * d_diffcage, 2) - math.pow(R, 2)) * math.pi * d_bev_s)

        # Bore for fitting section for profile shaft on output bevels with length of (25-b_bev mm)
        # (fitting of bevel wheel on output shaft is set to 25 mm)
        r = d_sh_3/2 + 5
        V5 = math.pow(r, 2) * math.pi * (25 - b_bev)

        # Total volume of the diffcage as sum of subvolumes in mm^3
        V_diffcage = V1 + V2 - V3 - V4 - V5

        # Volumes of shaft bearing carriers in mm^3
        V_sh_carr = ((math.pow(0.5 * d_sh_E, 2) - math.pow(0.5 * d_sh_3 + 2, 2)) * math.pi * b_E) + \
                    ((math.pow(0.5 * d_sh_F, 2) - math.pow(0.5 * d_sh_3 + 2, 2)) * math.pi * b_F) + \
                    ((math.pow(0.5 * d_1_F, 2) - math.pow(0.5 * d_sh_3 + 2, 2)) * math.pi * b_gap)

        # Masses of differential cage, bearing carriers, differential bolt and bevel gears in kg
        m_diffcage = V_diffcage * rho_gear
        m_carrier = V_sh_carr * rho_gear
        m_diffbolt = V_diffbolt * rho_gear
        m_bevels = V_bevels * rho_gear

        # Total mass of differential with components in kg
        m_3 = m_g4 + m_diffcage + m_carrier + m_diffbolt + m_bevels + m_E + m_F

        # Empirical mass with linear regression in kg
        m_diff_emp = regr_m_diff_coeff[0] + regr_m_diff_coeff[1] * (T_max * i_tot)

        # Addition of shaft if differential is facing out
        if gearbox.Input.axles.lower() == 'parallel' and diff_orientation.lower() == 'out':

            V_s3 = ((math.pow(0.5 * d_1_F, 2) - math.pow(0.5 * d_sh_F - 5, 2)) * math.pi * (b_gap + b_1 + b_gap))
            m_s3 = V_s3 * rho_gear
            m_diff_emp = m_diff_emp + m_s3

    else:   # 2 E-Machines at the corresponding axle

        # Volume of wheel 4 in mm^3
        V_gear_4 = ((math.pow(0.5 * d_4, 2) - math.pow(0.5 * d_sh_3, 2)) * math.pi * b_3) - \
                   ((0.6 * b_3 * math.pi * math.pow(0.5 * d_f4 - (3 * m_n_3), 2)) -
                    (0.3 * b_3 * math.pi * (math.pow(0.5 * d_1_E, 2) + math.pow(0.5 * d_1_F, 2))))

        # Volume of shaft 3 in mm^3
        V_shaft_3 = (math.pow(0.5 * d_1_E, 2) * math.pi * b_gap) + \
                    (math.pow(0.5 * d_sh_E, 2) * math.pi * b_E) - \
                    (math.pow(0.5 * d_sh_3, 2) * math.pi * (b_gap + b_E)) + \
                    (math.pow(0.5 * d_1_F, 2) * math.pi * b_gap) + \
                    (math.pow(0.5 * d_sh_F, 2) * math.pi * b_F) - \
                    (math.pow(0.5 * d_sh_3, 2) * math.pi * (b_gap + b_F))

        # Mass of wheel 4 in kg
        m_g4 = V_gear_4 * rho_gear

        # Mass of shaft 3 in kg
        m_s3 = V_shaft_3 * rho_gear

        # Total mass of shaft 3 with components in kg
        m_3 = m_g4 + m_s3 + m_E + m_F
    # endregion
    # endregion

    # region [3]: Mass of gearbox housing (1, pp. 74)
    if gearbox.Input.axles.lower() == 'parallel':

        # Initialization of angles between the axles
        theta = gearbox.results.theta               # Angle between connecting lines of shafts 1-2 and 1-3 [rad]
        zeta = gearbox.results.zeta                 # Angle between connecting lines of shafts 3-1 and 3-2 [rad]

        # Definition of decisive diameters d_x_h for each shaft in mm
        if d_1_max == d_a1:                         # Addition of clearance between gears and housing
            d_1_h = d_a1 + (2 * d_housing)
        else:
            d_1_h = d_1_max + 10

        d_2_h = d_a2 + (2 * d_housing)
        a_13 = a_12 * math.cos(theta) + a_23 * math.cos(zeta)
        d_4_h = d_a4 + (2 * d_housing)

        s_3 = 0.5 * d_1_h * math.sqrt(math.pow(a_13, 2) - math.pow(d_4_h/2 - d_1_h/2, 2)) / (d_4_h/2 - d_1_h/2)
        gamma_3 = math.atan((d_1_h/2) / s_3)
        val = (a_12 * math.sin(theta)) + ((s_3 + (a_12 * math.cos(theta))) * math.tan(gamma_3)) - d_2_h/2

        if val > 0 and not opt_gears.lower() == 'height' and theta > 0:
            # Area 1:
            s_1 = 0.5 * d_1_h * math.sqrt(math.pow(a_12, 2) - math.pow(d_2_h/2 - d_1_h/2, 2)) / (d_2_h/2 - d_1_h/2)
            x_1 = math.sqrt(math.pow(a_12, 2) - math.pow(d_2_h/2 - d_1_h/2, 2))
            gamma_1 = math.atan((d_1_h/2) / s_1)
            A_1_1 = ((math.pi + gamma_1) / (2 * math.pi)) * math.pi * math.pow(d_2_h/2, 2)
            A_1_2 = ((math.pi - gamma_1) / (2 * math.pi)) * math.pi * math.pow(d_1_h/2, 2)
            A_1_3 = 0.5 * x_1 * (d_1_h/2 + d_2_h/2)
            A_1 = A_1_1 + A_1_2 + A_1_3
            D_1_1 = ((math.pi + gamma_1) / (2 * math.pi)) * math.pi * \
                    (math.pow(0.5 * d_2_h + t_housing, 2) - math.pow(d_2_h/2, 2))
            D_1_2 = ((math.pi - gamma_1) / (2 * math.pi)) * math.pi * \
                    (math.pow(0.5 * d_1_h + t_housing, 2) - math.pow(d_1_h/2, 2))
            D_1_3 = x_1 * t_housing
            D_1 = D_1_1 + D_1_2 + D_1_3

            # Area 2:
            if d_2_h < d_4_h:
                s_2 = 0.5 * d_2_h * math.sqrt(math.pow(a_23, 2) - math.pow(d_4_h/2 - d_2_h/2, 2)) / (d_4_h/2 - d_2_h/2)
                x_2 = math.sqrt(math.pow(a_23, 2) - math.pow(d_4_h/2 - d_2_h/2, 2))
                gamma_2 = math.atan((d_2_h/2) / s_2)
                A_2_1 = ((math.pi - gamma_2) / (2 * math.pi)) * math.pi * math.pow(d_2_h/2, 2)
                A_2_2 = ((math.pi + gamma_2) / (2 * math.pi)) * math.pi * math.pow(d_4_h/2, 2)
                A_2_3 = 0.5 * x_2 * (d_2_h/2 + d_4_h/2)
                D_2_1 = ((math.pi - gamma_2) / (2 * math.pi)) * math.pi * (math.pow(0.5 * d_2_h + t_housing, 2) - math.pow(d_2_h/2, 2))
                D_2_2 = ((math.pi + gamma_2) / (2 * math.pi)) * math.pi * (math.pow(0.5 * d_4_h + t_housing, 2) - math.pow(d_4_h/2, 2))
                D_2_3 = x_2 * t_housing
            else:
                s_2 = 0.5 * d_4_h * math.sqrt(math.pow(a_23, 2) - math.pow(d_2_h/2 - d_4_h/2, 2)) / (d_2_h/2 - d_4_h/2)
                x_2 = math.sqrt(math.pow(a_23, 2) - math.pow(d_2_h/2 - d_4_h/2, 2))
                gamma_2 = math.atan((d_4_h/2) / s_2)
                A_2_1 = ((math.pi - gamma_2) / (2 * math.pi)) * math.pi * math.pow(d_4_h/2, 2)
                A_2_2 = ((math.pi + gamma_2) / (2 * math.pi)) * math.pi * math.pow(d_2_h/2, 2)
                A_2_3 = 0.5 * x_2 * (d_2_h/2 + d_4_h/2)
                D_2_1 = ((math.pi - gamma_2) / (2 * math.pi)) * math.pi * (math.pow(0.5 * d_4_h + t_housing, 2) - math.pow(d_4_h/2, 2))
                D_2_2 = ((math.pi + gamma_2) / (2 * math.pi)) * math.pi * (math.pow(0.5 * d_2_h + t_housing, 2) - math.pow(d_2_h/2, 2))
                D_2_3 = x_2 * t_housing

            A_2 = A_2_1 + A_2_2 + A_2_3
            D_2 = D_2_1 + D_2_2 + D_2_3

            # Area 3:
            x_3 = math.sqrt(math.pow(a_13, 2) - math.pow(d_4_h/2 - d_1_h/2, 2))
            A_3_1 = ((math.pi + gamma_3) / (2 * math.pi)) * math.pi * math.pow(d_4_h/2, 2)
            A_3_2 = ((math.pi - gamma_3) / (2 * math.pi)) * math.pi * math.pow(d_1_h/2, 2)
            A_3_3 = 0.5 * x_3 * (d_1_h/2 + d_4_h/2)
            A_3 = A_3_1 + A_3_2 + A_3_3
            D_3_1 = ((math.pi + gamma_2) / (2 * math.pi)) * math.pi * (math.pow(0.5 * d_4_h + t_housing, 2) - math.pow(d_4_h/2, 2))
            D_3_2 = ((math.pi - gamma_2) / (2 * math.pi)) * math.pi * (math.pow(0.5 * d_1_h + t_housing, 2) - math.pow(d_1_h/2, 2))
            D_3_3 = x_3 * t_housing
            D_3 = D_3_1 + D_3_2 + D_3_3

            # Area 4:
            c = (a_12 + a_23 + a_13)/2
            A_4 = math.sqrt(c * (c - a_12) * (c - a_23) * (c - a_13))

            # Subtract surplus areas:
            A_5 = ((math.pi/2 - theta) + (math.pi/2 + zeta)) / (2 * math.pi) * math.pi * math.pow(d_2_h/2, 2)
            A_6 = theta / (2 * math.pi) * math.pi * math.pow(d_1_h/2, 2)
            A_7 = zeta / (2 * math.pi) * math.pi * math.pow(d_4_h/2, 2)
            D_5 = (((math.pi/2 - theta) + (math.pi/2 + zeta)) / (2 * math.pi)) * math.pi * \
                  (math.pow(0.5 * d_2_h + t_housing, 2) - math.pow(d_2_h/2, 2))
            D_6 = theta / (2 * math.pi) * math.pi * (math.pow(0.5 * d_1_h + t_housing, 2) - math.pow(d_1_h/2, 2))
            D_7 = zeta / (2 * math.pi) * math.pi * (math.pow(0.5 * d_4_h + t_housing, 2) - math.pow(d_4_h/2, 2))

            A_tot = A_1 + A_2 + A_3 + A_4 - A_5 - A_6 - A_7
            D_tot = D_1 + D_2 + D_3 - D_5 - D_6 - D_7

        else:
            # Area 1:
            s_1 = 0.5 * d_1_h * math.sqrt(math.pow(a_12, 2) - math.pow(d_2_h/2 - d_1_h/2, 2)) / (d_2_h/2 - d_1_h/2)
            x_1 = math.sqrt(math.pow(a_12, 2) - math.pow(d_2_h/2 - d_1_h/2, 2))
            gamma_1 = math.atan((d_1_h/2)/s_1)
            A_1_1 = ((math.pi + gamma_1) / (2 * math.pi)) * math.pi * math.pow(d_2_h/2, 2)
            A_1_2 = ((math.pi - gamma_1) / (2 * math.pi)) * math.pi * math.pow(d_1_h/2, 2)
            A_1_3 = 0.5 * x_1 * (d_1_h/2 + d_2_h/2)
            A_1 = A_1_1 + A_1_2 + A_1_3
            D_1_1 = ((math.pi + gamma_1)/(2 * math.pi)) * math.pi * (math.pow(0.5 * d_2_h + t_housing, 2) - math.pow(d_2_h/2, 2))
            D_1_2 = ((math.pi - gamma_1)/(2 * math.pi)) * math.pi * (math.pow(0.5 * d_1_h + t_housing, 2) - math.pow(d_1_h/2, 2))
            D_1_3 = x_1 * t_housing
            D_1 = D_1_1 + D_1_2 + D_1_3

            # Area 2:
            if d_2_h < d_4_h:
                s_2 = 0.5 * d_2_h * math.sqrt(math.pow(a_23, 2) - math.pow(d_4_h/2 - d_2_h/2, 2))/(d_4_h/2 - d_2_h/2)
                x_2 = math.sqrt(math.pow(a_23, 2) - math.pow(d_4_h/2 - d_2_h/2, 2))
                gamma_2 = math.atan((d_2_h/2)/s_2)
                A_2_1 = ((math.pi + gamma_2) / (2 * math.pi)) * math.pi * math.pow(d_4_h/2, 2)
                A_2_2 = ((math.pi - gamma_2) / (2 * math.pi)) * math.pi * math.pow(d_2_h/2, 2)
                A_2_3 = 0.5 * x_2 * (d_2_h/2 + d_4_h/2)
                D_2_1 = ((math.pi + gamma_2) / (2 * math.pi)) * math.pi * (math.pow(0.5 * d_4_h + t_housing, 2) - math.pow(d_4_h/2, 2))
                D_2_2 = ((math.pi - gamma_2) / (2 * math.pi)) * math.pi * (math.pow(0.5 * d_2_h + t_housing, 2) - math.pow(d_2_h/2, 2))
                D_2_3 = x_2 * t_housing
            else:
                s_2 = (0.5 * d_4_h) * math.sqrt(math.pow(a_23, 2) - math.pow(d_2_h/2 - d_4_h/2, 2))/(d_2_h/2 - d_4_h/2)
                x_2 = math.sqrt(math.pow(a_23, 2) - math.pow(d_2_h/2 - d_4_h/2, 2))
                gamma_2 = math.atan((d_4_h/2)/s_2)
                A_2_1 = ((math.pi + gamma_2) / (2 * math.pi)) * math.pi * math.pow(d_2_h/2, 2)
                A_2_2 = ((math.pi - gamma_2) / (2 * math.pi)) * math.pi * math.pow(d_4_h/2, 2)
                A_2_3 = 0.5 * x_2 * (d_2_h/2 + d_4_h/2)
                D_2_1 = ((math.pi - gamma_2) / (2 * math.pi)) * math.pi * (math.pow(0.5 * d_2_h + t_housing, 2) - math.pow(d_2_h/2, 2))
                D_2_2 = ((math.pi + gamma_2) / (2 * math.pi)) * math.pi * (math.pow(0.5 * d_4_h + t_housing, 2) - math.pow(d_4_h/2, 2))
                D_2_3 = x_2 * t_housing

            A_2 = A_2_1 + A_2_2 + A_2_3
            D_2 = D_2_1 + D_2_2 + D_2_3

            # Subtract surplus area:
            A_3 = math.pi * math.pow(d_2_h/2, 2)
            D_3 = math.pi * (math.pow(0.5 * d_2_h + t_housing, 2) - math.pow(d_2_h/2, 2))

            A_tot = (2 * A_1) + (2 * A_2) - A_3
            D_tot = (2 * D_1) + (2 * D_2) - D_3

            if gamma_2 > gamma_1:
                a_13 = a_12 + a_23
                x_3 = math.sqrt(math.pow(a_13, 2) - math.pow(d_4_h/2 - d_1_h/2, 2))
                s_3 = 0.5 * d_1_h * math.sqrt(math.pow(a_23, 2) - math.pow(d_4_h/2 - d_1_h/2, 2)) / (d_4_h/2 - d_1_h/2)
                gamma_3 = math.atan((d_1_h/2)/s_3)
                A_3_1 = ((math.pi + gamma_3) / (2 * math.pi)) * math.pi * math.pow(d_4_h/2, 2)
                A_3_2 = ((math.pi - gamma_3) / (2 * math.pi)) * math.pi * math.pow(d_1_h/2, 2)
                A_3_3 = 0.5 * x_3 * (d_1_h/2 + d_4_h/2)
                A_3 = A_3_1 + A_3_2 + A_3_3
                A_tot = 2 * A_3
                D_3_1 = ((math.pi + gamma_3) / (2 * math.pi)) * math.pi * (math.pow(0.5 * d_4_h + t_housing, 2) - math.pow(0.5 * d_4_h, 2))
                D_3_2 = ((math.pi - gamma_3) / (2 * math.pi)) * math.pi * (math.pow(0.5 * d_1_h + t_housing, 2) - math.pow(0.5 * d_1_h, 2))
                D_3_3 = x_3 * t_housing
                D_3 = D_3_1 + D_3_2 + D_3_3
                D_tot = 2 * D_3

    else:   # Coaxial shaft configuration
        # Only for d_4>d_2!
        d_2_h = d_a2 + 2 * d_housing
        d_4_h = d_a4 + 2 * d_housing
        r = min(d_2_h, d_4_h)/2
        R = max(d_2_h, d_4_h)/2
        x = (r * a_12)/(R - r)
        s = r * (math.sqrt(math.pow(a_12, 2) - math.pow(R - r, 2)))/(R - r)
        t = math.sqrt(math.pow(a_12, 2) - math.pow(R - r, 2))
        eps = math.acos(s/x)

        A_1 = r * t
        A_2 = 0.5 * t * a_12 * math.sin(eps)
        A_3 = 0.5 * math.pow(r, 2) * (0.5 * math.pi - eps)
        A_4 = 0.5 * math.pow(R, 2) * (0.5 * math.pi + eps)
        A_tot = 2 * (A_1 + A_2 + A_3 + A_4)

        D_1 = 2*(math.pow(r+t_housing, 2) - math.pow(r, 2)) * (0.5 * math.pi - eps)
        D_2 = 2 * t * t_housing
        D_3 = 2 * (math.pow(R+t_housing, 2) - math.pow(R, 2)) * (0.5 * math.pi + eps)
        D_4 = (math.pow(R + t_housing, 2) - math.pow(R, 2)) * 2 * math.pi

    # Volume in mm^3 and mass in kg of housing cap:
    V_cap = A_tot * t_housing
    m_cap = V_cap * rho_alu

    # Mass of housing bottom in kg:
    m_bottom = V_cap * rho_alu

    # Volumes of housing sides in mm^3:
    if gearbox.Input.num_EM == 1:

        if gearbox.Input.axles.lower() == 'parallel':

            if diff_orientation.lower() == 'in':
                V_side_1 = D_tot * (t_gearbox - (b_seal + b_E + b_diffcage - b_gap - b_1 - b_gap - b_C - t_housing))
                V_side_2 = math.pi * (d_4_h * (b_seal + b_E + b_diffcage - b_gap - b_1 - b_gap - b_C - t_housing))
            else:
                V_side_1 = D_tot * (t_gearbox - (b_seal + b_E + b_diffcage - b_gap - b_D - t_housing))
                V_side_2 = math.pi * (d_4_h * (b_seal + b_E + b_diffcage - b_gap - b_D - t_housing))

        else:   # Coaxial shaft configuration
            V_side_1 = (D_1 + D_2 + D_3) * (t_gearbox - b_seal - b_E - b_diffcage + b_gap + b_D + t_housing)
            V_side_2 = D_4 * (b_seal + b_E + b_diffcage - b_gap - b_D - t_housing)

        V_side = V_side_1 + V_side_2
    else:   # Two E-Machine at the corresponding axle
        if gearbox.Input.axles.lower() == 'parallel':
            V_side = D_tot * t_gearbox
        else:   # Coaxial shaft configuration
            V_side = (D_1 + D_2 + D_3) * t_gearbox

    # Mass of housing sides in kg:
    m_side = V_side * rho_alu

    # Volumes of bearing carriers in housing in mm^3 (1, p. 73) (with thickness of 5 mm)
    if gearbox.Input.axles.lower() == 'parallel' and diff_orientation.lower() == 'in':
        max_b_left = max(b_A + b_gap + b_park, b_C)     # max. width of bearings on the left side of stage 1
        max_b_right = max(b_D, b_F)                     # max. width of bearings on the right side of stage 2
        V_BA = (max_b_left - b_park - b_gap) * math.pi * (math.pow(0.5 * d_A_A + 5, 2)-math.pow(0.5 * d_A_A, 2))
        V_BB = (b_F + b_3) * math.pi * (math.pow(0.5 * d_A_B+5, 2) - math.pow(0.5 * d_A_B, 2))
        V_BC = max_b_left * math.pi * (math.pow(0.5 * d_A_C + 5, 2) - math.pow(0.5 * d_A_C, 2))
        V_BD = max_b_right * math.pi * (math.pow(0.5 * d_A_D + 5, 2) - math.pow(0.5 * d_A_D, 2))
        V_BE = b_E * math.pi * (math.pow(0.5 * d_A_E + 5, 2) - math.pow(d_A_E*0.5, 2))
        V_BF = max_b_right * math.pi * (math.pow(0.5 * d_A_F + 5, 2) - math.pow(0.5 * d_A_F, 2))

    else:
        max_b_left = max([b_A + b_gap + b_park, b_C, b_F])      # max. width of bearings on the left side of stage 1
        V_BA = (max_b_left - b_park - b_gap) * math.pi * (math.pow(0.5 * d_A_A + 5, 2) - math.pow(0.5 * d_A_A, 2))
        V_BB = (b_D + b_gap + b_3) * math.pi * (math.pow(0.5 * d_A_B + 5, 2) - math.pow(0.5*d_A_B, 2))
        V_BC = max_b_left * math.pi * (math.pow(0.5 * d_A_C + 5, 2) - math.pow(0.5 * d_A_C, 2))
        V_BD = b_D * math.pi * (math.pow(0.5 * d_A_D + 5, 2) - math.pow(0.5 * d_A_D, 2))
        V_BE = b_E * math.pi * (math.pow(0.5 * d_A_E + 5, 2) - math.pow(0.5 * d_A_E, 2))
        V_BF = max_b_left * math.pi * (math.pow(0.5 * d_A_F+5, 2) - math.pow(0.5 * d_A_F, 2))

    #  Mass of all bearing carriers in kg:
    m_house_carr = (V_BA + V_BB + V_BC + V_BD + V_BE + V_BF) * rho_alu

    # Total mass of housing in kg:
    m_housing = m_cap + m_bottom + m_side + m_house_carr
    # endregion

    # region [4]: Total mass of gearbox in kg
    if gearbox.Input.num_EM == 1:
        m_gearbox = m_1 + m_2 + m_diff_emp + m_housing
        m_gearing = m_1 + m_2 + m_diff_emp - m_A - m_B - m_C - m_D - m_E - m_F
    else:       # Two E-Machines at the corresponding axle
        m_gearbox = m_1 + m_2 + m_3 + m_housing
        m_gearing = m_1 + m_2 + m_3 - m_A - m_B - m_C - m_D - m_E - m_F
    # endregion

    # region [5]: Output assignment
    setattr(gearbox.results, 'm_gearbox', m_gearbox)        # Total mass of gearbox in kg

    setattr(gearbox.masses, 'm_s1', m_s1)                   # Mass of shaft 1 in kg
    setattr(gearbox.masses, 'm_g1', m_g1)                   # Mass of gear 1 in kg
    setattr(gearbox.masses, 'm_s2', m_s2)                   # Mass of shaft 2 in kg
    setattr(gearbox.masses, 'm_g23', m_g23)                 # Mass of gears 2&3 in kg
    setattr(gearbox.masses, 'm_g4', m_g4)                   # Mass of gear 4 in kg
    setattr(gearbox.masses, 'm_1', m_1)                     # Total mass of shaft 1 with bearings in kg
    setattr(gearbox.masses, 'm_2', m_2)                     # Total mass of shaft 2 with bearings in kg
    setattr(gearbox.masses, 'm_3', m_3)                     # Total mass of differential with bearings in kg
    setattr(gearbox.masses, 'm_housing', m_housing)         # Mass of housing in kg
    setattr(gearbox.masses, 'm_gearing', m_gearing)         # Mass of gearing without bearings in kg
    setattr(gearbox.masses, 'm_tot', m_gearbox)             # Total mass of gearbox in kg

    if gearbox.Input.num_EM == 1:

        setattr(gearbox.masses, 'm_diffcage', m_diffcage)   # Mass of differential cage in kg
        setattr(gearbox.masses, 'm_diffbolt', m_diffbolt)   # Mass of differential bolt in kg
        setattr(gearbox.masses, 'm_bevels', m_bevels)       # Mass of bevel gears in kg
        setattr(gearbox.masses, 'm_diff_emp', m_diff_emp)   # Empirical mass of complete differential with bearings in kg

    else:   # Two E-Machines at the corresponding axle
        setattr(gearbox.masses, 'm_s3', m_s3)               # Mass of shaft 3 in kg
    # endregion

    return gearbox
