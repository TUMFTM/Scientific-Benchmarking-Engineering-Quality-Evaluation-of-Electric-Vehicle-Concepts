"""
Description:    This function computes the mass of the planetary gearbox in kg according to the volume of its components.
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


def calc_mass_planetary(gearbox, parameters):
    # region [1]: Initialization of required values
    # Assign general gearbox parameters from the parameters class
    rho_alu = parameters.gearbox.MatProp.rho_alu/math.pow(10, 9)    # Density of housing material AlSi9Cu3 (3, p. 517) [kg/m^3]
    rho_gear = parameters.gearbox.MatProp.rho_gear/math.pow(10, 9)  # Density 16MnCr5 (1, p. 67) [kg/m^3]
    t_housing = parameters.gearbox.ConstDim.t_housing           # Housing thickness as mean of database (2, p. 60) [mm]
    t_diffcage = parameters.gearbox.ConstDim.t_diffcage         # Thickness of differential cage [mm]
    b_seal = parameters.gearbox.ConstDim.b_seal                 # Width of sealings as mean of database (2, p. 61) [mm]
    d_diffbolt = parameters.gearbox.ConstDim.d_diffbolt         # Diameter of differential bolt (1, p. 55) [mm]
    d_planbolt = parameters.gearbox.ConstDim.d_planbolt         # Diameter of planet bolt [mm]
    b_gap = parameters.gearbox.ConstDim.b_gap                   # Gap between components on the shafts (1, p. 64) [mm]

    # Assign the parameters of the gears
    m_n_1 = gearbox.gears_12.m_n_1                      # Normal module of first stage [mm]
    m_n_2 = gearbox.gears_12.m_n_2                      # Normal module of second stage [mm]
    b_1 = gearbox.gears_12.b_1                          # Width of first stage wheels [mm]
    b_2 = gearbox.gears_12.b_2                          # Width of second stage wheels [mm]
    d_1 = gearbox.gears_12.d_1                          # Pitch diameter of sun gear [mm]
    d_p1 = gearbox.gears_12.d_p1                        # Pitch diameter of planet 1 [mm]
    d_p2 = gearbox.gears_12.d_p2                        # Pitch diameter of planet 2 [mm]
    d_2 = gearbox.gears_12.d_2                          # Pitch diameter of ring gear [mm]
    d_s = gearbox.gears_12.d_s                          # Diameter of planet circle [mm]
    d_fp1 = gearbox.gears_12.d_fp1                      # Root diameter of planet 1 [mm]
    d_fp2 = gearbox.gears_12.d_fp2                      # Root diameter of planet 2 [mm]
    d_f2 = gearbox.gears_12.d_f2                        # Root diameter of ring gear [mm]
    d_ap2 = gearbox.gears_12.d_ap2                      # Outside diameter of planet 2 [mm]

    # Assign the shaft parameters of the gearbox
    d_inn_1 = gearbox.shafts.d_inn_1                    # Inner diameter of hollow sun shaft [mm]
    d_inn_p = gearbox.shafts.d_inn_p                    # Inner diameter of hollow planet shaft [mm]
    d_sh_3 = gearbox.shafts.d_sh_3                      # Outer diameter of output shaft [mm]
    d_1_max = gearbox.shafts.d_1_max                    # Maximum diameter of the gears on the first stage [mm]
    d_2_max = gearbox.shafts.d_2_max                    # Maximum diameter of the ring gear (second stage) [mm]

    # Assign the bearing values of the first shaft (bearing A and B)
    b_A = gearbox.bearings_1.b_B                        # Width of bearing B [mm]
    d_sh_A = gearbox.bearings_1.d_sh_A                  # Inner diameter of bearing A [mm]
    d_sh_B = gearbox.bearings_1.d_sh_B                  # Inner diameter of bearing B [mm]
    d_1_A = gearbox.bearings_1.d_1_B                    # Outer diameter of Bs inner bearing ring [mm]
    d_A_A = gearbox.bearings_1.d_A_B                    # Outer diameter of bearing B [mm]
    m_A = gearbox.bearings_1.m_A                        # Mass of bearing A [kg]

    # Assign the bearing values of the second shaft (bearing C and D)
    b_C = gearbox.bearings_2.b_C                        # Width of bearing C [mm]
    b_D = gearbox.bearings_2.b_D                        # Width of bearing D [mm]
    d_sh_C = gearbox.bearings_2.d_sh_C                  # Inner diameter of bearing C [mm]
    d_sh_D = gearbox.bearings_2.d_sh_D                  # Inner diameter of bearing D [mm]
    d_1_C = gearbox.bearings_2.d_1_C                    # Outer diameter of Cs inner bearing ring [mm]
    d_1_D = gearbox.bearings_2.d_1_D                    # Outer diameter of Ds inner bearing ring [mm]
    d_A_C = gearbox.bearings_2.d_A_C                    # Outer diameter of bearing C [mm]
    d_A_D = gearbox.bearings_2.d_A_D                    # Outer diameter of bearing D [mm]
    m_C = gearbox.bearings_2.m_C                        # Mass of bearing C [kg]
    m_D = gearbox.bearings_2.m_D                        # Mass of bearing D [kg]

    # Assign the bearing values of the third shaft (bearing E and F)
    b_E = gearbox.bearings_3.b_E                        # Width of bearing E [mm]
    b_F = gearbox.bearings_3.b_F                        # Width of bearing F [mm]
    d_sh_E = gearbox.bearings_3.d_sh_E                  # Inner diameter of bearing E [mm]
    d_sh_F = gearbox.bearings_3.d_sh_F                  # Inner diameter of bearing F [mm]
    d_1_E = gearbox.bearings_3.d_1_E                    # Outer diameter of Es inner bearing ring [mm]
    d_A_E = gearbox.bearings_3.d_A_E                    # Outer diameter of bearing E [mm]
    d_A_F = gearbox.bearings_3.d_A_F                    # Outer diameter of bearing F [mm]
    m_E = gearbox.bearings_3.m_E                        # Mass of bearing E [kg]
    m_F = gearbox.bearings_3.m_F                        # Mass of bearing F [kg]

    # Assign the housing dimensions of the gearbox
    d_gearing = gearbox.dimension_house.d_gearing       # Outer diameter of largest gears [mm]

    # Assign the differential parameters
    d_diffcage = gearbox.differential.d_diffcage        # Diameter of differential cage [mm]
    b_diffcage = gearbox.differential.b_diffcage        # Width of differential cage [mm]
    t_diff = gearbox.differential.t_diff                # Width of differential [mm]

    # Assign additional differential parameters (only necessary when there is only one E-Machine placed at the axle
    if gearbox.Input.num_EM == 1:
        b_bev = gearbox.differential.b_bev              # Width of bevel gears in differential [mm]
        d_bev_l = gearbox.differential.d_bev_l          # Diameter of larger bevel gears in differential [mm]
        d_bev_s = gearbox.differential.d_bev_s          # Diameter of smaller bevel gears in differential [mm]

    else:       # Set values to zero to avoid a Pycharm warning (referencing before assigning)
        b_bev = 0
        d_bev_l = 0
        d_bev_s = 0
    # endregion

    # region [2]: Calculation of the Masses of shafts, bearings and gears
    #  region [2.1]: Sun shaft
    # Volumes of first wheel and shaft in mm^3
    V_gear_1 = (math.pow(d_1/2, 2) - math.pow(d_inn_1/2, 2)) * math.pi * b_1
    V_shaft_1 = ((b_seal + b_F + 5 + b_C + b_gap - 5 - b_A) * (math.pow(d_sh_B/2, 2) - math.pow(d_inn_1/2, 2)) * math.pi) + \
                (b_A * (math.pow(d_sh_A/2, 2) - math.pow(d_inn_1/2, 2)) * math.pi) + \
                (5 * (math.pow(d_1_A/2, 2) - math.pow(d_inn_1/2, 2)) * math.pi)

    # Masses of first wheel and shaft in kg
    m_g1 = V_gear_1 * rho_gear
    m_s1 = V_shaft_1 * rho_gear

    # Total mass of sun shaft without bearings in kg
    m_1 = m_g1 + m_s1 + m_A
    # endregion

    # region [2.2]: Planets
    # Volumes of planets in mm^3 (gear web thickness of planet gears is decreased if diameter is large enough)
    if d_fp1 - 6 * m_n_1 - d_1_C > 40:
        V_gp1 = ((math.pow(0.5 * d_p1, 2) - math.pow(0.5*d_inn_p, 2)) * math.pi * b_1) - \
                ((math.pow(0.5 * d_fp1 - 3 * m_n_1, 2) - math.pow(d_1_C/2, 2)) * math.pi * b_1 * 0.7)
    else:
        V_gp1 = (math.pow(0.5 * d_p1, 2) - math.pow(0.5 * d_inn_p, 2)) * math.pi * b_1

    if d_fp2 - 6 * m_n_2 - d_1_D > 20:
        V_gp2 = ((math.pow(0.5 * d_p2, 2) - math.pow(0.5 * d_inn_p, 2)) * math.pi * b_2) - \
                ((math.pow(0.5 * d_fp2 - 3 * m_n_2, 2) - math.pow(d_1_D/2, 2)) * math.pi * b_2 * 0.7)
    else:
        V_gp2 = (math.pow(0.5 * d_p2, 2) - math.pow(0.5 * d_inn_p, 2)) * math.pi * b_2

    # Volume of both planet gears in mm^3
    V_gp = V_gp1 + V_gp2

    # Volume of planet bolts in mm^3
    V_sp = (b_C * (math.pow(d_sh_C/2, 2) - math.pow(d_inn_p/2, 2)) * math.pi) + \
           (b_D * (math.pow(d_sh_D/2, 2) - math.pow(d_inn_p/2, 2)) * math.pi) + \
           (b_gap * (math.pow(d_1_C/2, 2) - math.pow(d_inn_p/2, 2)) * math.pi) + \
           (b_gap * (math.pow(d_1_D/2, 2) - math.pow(d_inn_p/2, 2)) * math.pi) + \
           (b_gap * (math.pow(min(d_1_C, d_1_D)/2, 2) - math.pow(d_inn_p/2, 2)) * math.pi)

    # Masses of planet wheels and planet bolts in kg
    m_gp = V_gp * rho_gear
    m_sp = V_sp * rho_gear

    # Total mass of one planet with bearings in kg
    m_p = m_gp + m_sp + m_C + m_D
    # endregion

    # region [2.3]: Ring gear
    # Volume of ring gear in mm^3
    V_g2 = b_2 * (math.pow(d_f2/2 + 6 * m_n_2, 2) - math.pow(d_2/2, 2)) * math.pi

    # Mass of ring gear in kg
    m_g2 = V_g2 * rho_gear
    # endregion

    # region [2.4]: Planet carrier with integrated differential
    # Calculation of the planet carrier's volume, separated in input side (pc1),
    # differential side (pc2) and connecting bolts (pcbolt)
    g_1 = math.sqrt(3) * (d_s/2 + 2 * (d_A_C/2 + 5))
    g_2 = math.sqrt(3) * (d_s/2 + 2 * (d_A_D/2 + 5))
    V_pc1 = ((math.sqrt(3)/4 * math.pow(g_1, 2)) - 3 * ((math.sqrt(3)/4 * math.pow(d_A_C + 10, 2) +
            1/2 * math.pow(d_A_C/2+5, 2) * math.pi))) * t_housing - \
            (math.pow(d_A_A/2, 2) * math.pi * 5) + 3 * ((math.pow(d_A_C/2 + 5, 2) - math.pow(d_A_C/2, 2)) * b_C * math.pi +
            (math.pow(d_A_C/2 + 5, 2) - math.pow(d_A_C/2-3, 2)) * 5 * math.pi) + (math.pow(d_sh_F/2, 2) - math.pow(d_A_A/2, 2)) * (b_C + 5 + b_F) * math.pi

    V_pcbolt = math.pow(d_planbolt/2, 2) * math.pi * (b_gap + b_1 + b_gap + b_2 + b_gap)

    if gearbox.Input.num_EM == 1:
        V_pc2 = ((math.sqrt(3)/4 * math.pow(g_2, 2)) - 3 * (math.sqrt(3)/4 * math.pow(d_A_D + 10, 2) + 1/2 * math.pow(d_A_D/2 + 5, 2) * math.pi)) * \
                t_housing - (math.pow(d_diffcage/2, 2) * math.pi * 5) + 3 * ((math.pow(d_A_D/2 + 5, 2) - math.pow(d_A_D/2, 2)) * b_D * math.pi + (math.pow(d_A_D/2 + 5, 2) - math.pow(d_A_D/2 - 3, 2)) * 5 * math.pi)

        # Volume in mm^3 and mass in kg of the planet carrier
        V_pc = V_pc1 + V_pc2 + 3 * V_pcbolt
        m_pc = V_pc * rho_gear

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
        V1 = math.pow(d_diffcage/2, 2) * math.pi * b_diffcage

        # Truncated cone with diameter d_diffcage on one side and d_1_E on the other and length of 10 mm
        R = d_diffcage/2
        r = d_1_E/2
        length = t_diffcage
        V2 = math.pi/3 * length * (math.pow(R, 2) + R * r + math.pow(r, 2))

        # Cylinder with diameter of larger bevels plus ball segments on smaller bevels
        r = math.sqrt(2)/2 * d_bev_s
        R = 0.5 * d_bev_l
        V3 = math.pow(R, 2) * math.pi * d_bev_s + 2 * (math.pi/3 * math.pow(h, 2) * (3 * r - 5))

        # Opening for montage of bevel gears (2*120 deg)
        V4 = 2/3 * ((math.pow(0.5 * d_diffcage, 2) - math.pow(R, 2)) * math.pi * d_bev_s)

        # Bore for fitting section for profile shaft on output bevels
        r = d_sh_3/2 + 5
        V5 = math.pow(r, 2) * math.pi * t_diffcage

        # Volume of left differential wall (fitting of bevel next to sun gear) in mm^3
        r = d_sh_E/2 - 5
        V6 = math.pow(r, 2) * math.pi * t_diffcage

        # Total volume of the diffcage as sum of subvolumes in mm^3
        V_diffcage = V1 + V2 - V3 - V4 - V5 - V6

        # Volume of output shaft and shaft bearing E carrier in mm^3
        V_sh_carr = (math.pow(0.5 * d_sh_E, 2) - math.pow(0.5 * d_sh_3 + 2, 2)) * math.pi * b_E

        # Masses of differential cage, bearing carriers, differential bolt and bevel gears in kg
        m_diffcage = V_diffcage * rho_gear
        m_carrier = V_sh_carr * rho_gear
        m_diffbolt = V_diffbolt * rho_gear
        m_bevels = V_bevels * rho_gear

        # Total mass of differential with components in kg
        m_planetcarrier = m_pc + m_diffcage + m_carrier + m_diffbolt + m_bevels + m_E + m_F

    else:   # There are two E-Machines at the corresponding axles
        V_pc2 = ((math.sqrt(3)/4 * math.pow(g_2, 2)) - 3 * (math.sqrt(3)/4 * math.pow(d_A_D+10, 2) + 1/2 * math.pow(d_A_D/2 + 5, 2) * math.pi)) * \
                t_housing - (math.pow(d_sh_3/2, 2) * math.pi * 5) + 3 * \
                ((math.pow(d_A_D/2 + 5, 2) - math.pow(d_A_D/2, 2)) * b_D * math.pi + (math.pow(d_A_D/2 + 5, 2) - math.pow(d_A_D/2 - 3, 2)) * 5 * math.pi)

        # Volume in mm^3 and mass in kg of the planet carrier
        V_pc = V_pc1 + V_pc2 + 3 * V_pcbolt
        m_pc = V_pc * rho_gear

        # Volume and mass of bearing E carrier in mm^3 and kg
        V_sh_carr = (math.pow(0.5 * d_sh_E, 2) - math.pow(0.5 * d_sh_3 + 2, 2)) * math.pi * b_E
        m_carrier = V_sh_carr * rho_gear

        m_planetcarrier = m_pc + m_carrier + m_E + m_F
    # endregion

    # region [3]: Mass of gearbox housing
    # Calculation of volumes via cylindrical surfaces with indices A for cylinder bases and D for shell surfaces
    if d_gearing == d_1_max:
        A_1 = (math.pow(d_1_max/2 + 3 * t_housing, 2) - math.pow(d_A_F/2 + 5, 2)) * math.pi
        A_2 = (math.pow(d_1_max/2 + 3 * t_housing, 2) - math.pow(d_2_max/2, 2)) * math.pi
        A_3 = (math.pow(d_2_max/2 + 3 * t_housing, 2) - math.pow(d_A_E/2 + 5, 2)) * math.pi
        A_tot = A_1 + A_2 + A_3

        D_1 = (math.pow(d_1_max/2 + 3 * t_housing, 2) - math.pow(d_1_max/2, 2)) * math.pi
        D_2 = (math.pow(d_2_max/2 + 3 * t_housing, 2) - math.pow(d_2_max/2, 2)) * math.pi
        D_3 = (math.pow(d_A_E/2 + 5 + 3 * t_housing, 2) - math.pow(d_A_E/2 + 5, 2)) * math.pi
        V_shell_1 = D_1 * (b_gap + 5 + b_C + b_gap + b_1 + b_gap)
        V_shell_2 = D_2 * (-3 * t_housing + b_2 + b_gap + b_D + 5 + b_gap)

        if gearbox.Input.num_EM == 1:
            if d_s - d_ap2 - 4 > d_diffcage:
                V_shell_3 = D_3 * (-3 * t_housing - b_gap + t_diff - (5 + b_D + b_gap + b_2) + 2 * b_seal)
            else:
                V_shell_3 = D_3 * (-3 * t_housing - b_gap + t_diff - (30 - b_bev) + 2 * b_seal)

        else:    # There are two E-Machines located at the corresponding axle
            if b_E - 3 * t_housing >= 0:
                V_shell_3 = D_3 * (b_E - 3 * t_housing + b_seal)
            else:
                V_shell_3 = D_3 * b_E + b_seal

        V_shells = V_shell_1 + V_shell_2 + V_shell_3

    elif d_gearing == d_2_max:
        A_1 = (math.pow(d_2_max/2 + 3 * t_housing, 2) - math.pow(d_A_F/2 + 5, 2)) * math.pi
        A_3 = (math.pow(d_2_max/2 + 3 * t_housing, 2) - math.pow(d_A_E/2 + 5, 2)) * math.pi
        A_tot = A_1 + A_3

        D_2 = (math.pow(d_2_max/2 + 3 * t_housing, 2) - math.pow(d_2_max/2, 2)) * math.pi
        D_3 = (math.pow(d_A_E/2 + 5 + 3 * t_housing, 2) - math.pow(d_A_E/2 + 5, 2)) * math.pi
        V_shell_2 = D_2 * (b_gap + 5 + b_C + b_gap + b_1 + b_gap + b_2 + b_gap + b_D + 5 + b_gap)

        if gearbox.Input.num_EM == 1:
            if d_s - d_ap2 - 4 > d_diffcage:
                V_shell_3 = D_3 * (-3 * t_housing - b_gap + t_diff - (5 + b_D + b_gap + b_2))
            else:
                V_shell_3 = D_3 * (-3 * t_housing - b_gap + t_diff - (30 - b_bev))

        else:   # There are two E-Machines located at the corresponding axle
            if b_E - 3 * t_housing >= 0:
                V_shell_3 = D_3 * (b_E - 3 * t_housing + b_seal)
            else:
                V_shell_3 = D_3 * b_E + b_seal

        V_shells = V_shell_2 + V_shell_3

    # noinspection PyUnboundLocalVariable
    V_bases = A_tot * 3 * t_housing

    # Mass of housing without bearing carriers in kg
    # noinspection PyUnboundLocalVariable
    m_house = (V_bases + V_shells) * rho_alu

    # Volumes of bearing carriers in housing in mm^3 (Zaehringer, p. 73)
    # (with carrier thickness of 5 mm)
    V_BE = b_E * math.pi * (math.pow(0.5 * d_A_E + 5, 2) - math.pow(d_A_E * 0.5, 2))
    V_BF = b_F * math.pi * (math.pow(0.5 * d_A_F + 5, 2) - math.pow(0.5 * d_A_F, 2))

    # Mass of all bearing carriers in kg:
    m_house_carr = (V_BE + V_BF) * rho_alu

    # Total mass of housing in kg:
    m_housing = m_house + m_house_carr
    # endregion

    # region [4]: Total mass of gearbox in kg
    m_gearbox = m_1 + 3 * m_p + m_g2 + m_planetcarrier + m_housing
    m_gearing = m_1 + 3 * m_p + m_g2 + m_planetcarrier - m_A - 3 * (m_C + m_D) - m_E - m_F
    # endregion

    # region [5]: Output assignment
    setattr(gearbox.results, 'm_gearbox', m_gearbox)                # Total mass of gearbox in kg

    setattr(gearbox.masses, 'm_s1', m_s1)                           # Mass of sun shaft in kg
    setattr(gearbox.masses, 'm_g1', m_g1)                           # Mass of sun gear in kg
    setattr(gearbox.masses, 'm_sp', m_sp)                           # Mass of planet shaft in kg
    setattr(gearbox.masses, 'm_gp', m_gp)                           # Mass of planet gears in kg
    setattr(gearbox.masses, 'm_gr', m_g2)                           # Mass of ring gear in kg

    # Total masses of shafts with gears and bearings of each shaft in kg
    setattr(gearbox.masses, 'm_1', m_1)                             # Total mass of sun shaft with bearings in kg
    setattr(gearbox.masses, 'm_planet', m_p)                        # Total mass of one planet with bearings in kg
    setattr(gearbox.masses, 'm_planetcarrier', m_planetcarrier)     # Total mass of planet carrier without planets but with bearings E&F in kg
    setattr(gearbox.masses, 'm_housing', m_housing)                 # Mass of housing in kg
    setattr(gearbox.masses, 'm_gearing', m_gearing)                 # Mass of gearing without bearings in kg
    setattr(gearbox.masses, 'm_tot', m_gearbox)                     # Total mass of gearbox in kg

    if gearbox.Input.num_EM == 1:
        # noinspection PyUnboundLocalVariable
        setattr(gearbox.masses, 'm_diffcage', m_diffcage)           # Mass of differential cage in kg
        # noinspection PyUnboundLocalVariable
        setattr(gearbox.masses, 'm_diffbolt', m_diffbolt)           # Mass of differential bolt in kg
        # noinspection PyUnboundLocalVariable
        setattr(gearbox.masses, 'm_bevels', m_bevels)               # Mass of bevel gears in kg

    # endregion

    return gearbox
