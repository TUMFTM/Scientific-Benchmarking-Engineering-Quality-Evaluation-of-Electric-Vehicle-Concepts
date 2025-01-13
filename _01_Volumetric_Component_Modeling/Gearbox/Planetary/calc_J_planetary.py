"""
Description:    This function computes the moment of inertia with regard to input of the  and output shaft speed of
                the spinning components of the planetary gearbox in kg*mm^2 according to
                Gross et al.: "Technische Mechanik 2" (starting p. 80 and 134).
------------
Sources:    (1) Gross et al.: "Technische Mechanik 2", Springer Vieweg, 2021, ISBN: 978-3-662-61862-2
            (2) M. Zaehringer, "Erstellung eines analytischen Ersatzmodells fuer Getriebe von Elektrofahrzeugen", Bachelor Thesis, TUM, 2018
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
------------
Output:  Moment of inertia of the planetary gearbox
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Initialization of required values
[2] Sun shaft: Calculation of the moment of inertia in kg*mm^2
[3] Planets: Calculation of the moment of inertia in kg*mm^2
[4] Bearings: Calculation of the moment of inertia in kg*mm^2
[5] Calculate total moment of inertia in kg*mm^2
[6] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
# Import classes
# Import methods
# endregion


def calc_J_planetary(gearbox, parameters):
    # region [1]: Initialization of required values
    # Assign the constant gearbox parameters from the parameters class
    b_gap = parameters.gearbox.ConstDim.b_gap                       # Gap between components on the shafts (2, p. 64) [mm]
    t_housing = parameters.gearbox.ConstDim.t_housing               # Housing thickness [mm]
    d_diffbolt = parameters.gearbox.ConstDim.d_diffbolt             # Diameter of differential bolt (2, p. 55) [mm]
    d_planbolt = parameters.gearbox.ConstDim.d_planbolt             # Diameter of planet bolt [mm]
    b_seal = parameters.gearbox.ConstDim.b_seal                     # Width of sealings of the housing [mm]
    rho_gear = parameters.gearbox.MatProp.rho_gear/math.pow(10, 9)  # Density 16MnCr5 (2, p. 67) [kg/m^3]

    # Assign the transmission ratios from the transmission stages
    i_0 = gearbox.results.i_0                       # Stationary gear ratio [-]
    i_1s = gearbox.results.i_1s                     # Transmission ratio between sun gear and planet carrier [-]
    i_p_rel = gearbox.results.i_p_rel               # Relative transmission ratio of the planets [-]

    # Assign the values from the gears of the planetary gearbox
    m_n_1 = gearbox.gears_12.m_n_1                  # Normal module of first stage [mm]
    d_1 = gearbox.gears_12.d_1                      # Pitch diameter of sun gear [mm]
    d_p1 = gearbox.gears_12.d_p1                    # Pitch diameter of first planet [mm]
    d_p2 = gearbox.gears_12.d_p2                    # Pitch diameter of second planet [mm]
    d_s = gearbox.gears_12.d_s                      # Diameter of planet circle [mm]
    b_1 = gearbox.gears_12.b_1                      # Width of first stage gears [mm]
    b_2 = gearbox.gears_12.b_2                      # Width of second stage gears [mm]
    d_fp1 = gearbox.gears_12.d_fp1                  # Root diameter of first planet [mm]
    d_fp2 = gearbox.gears_12.d_fp2                  # Root diameter of second planet [mm]

    # Assign the values from the bearings of the first transmission stage (Bearings A and B)
    b_A = gearbox.bearings_1.b_A                    # Width of bearing A [mm]
    b_B = gearbox.bearings_1.b_B                    # Width of bearing B [mm]
    d_sh_A = gearbox.bearings_1.d_sh_A              # Inner diameter of bearing A [mm]
    d_sh_B = gearbox.bearings_1.d_sh_B              # Inner diameter of bearing B [mm]
    d_1_A = gearbox.bearings_1.d_1_A                # Outer diameter of As inner bearing ring [mm]
    d_1_B = gearbox.bearings_1.d_1_B                # Outer diameter of Bs inner bearing ring [mm]
    d_A_A = gearbox.bearings_1.d_A_A                # Outer diameter of bearing A [mm]

    # Assign the values from the bearings of the second transmission stage (Bearings C and D)
    b_C = gearbox.bearings_2.b_C                    # Width of bearing C [mm]
    b_D = gearbox.bearings_2.b_D                    # Width of bearing D [mm]
    d_sh_C = gearbox.bearings_2.d_sh_C              # Inner diameter of bearing C [mm]
    d_sh_D = gearbox.bearings_2.d_sh_D              # Inner diameter of bearing D [mm]
    d_1_C = gearbox.bearings_2.d_1_C                # Outer diameter of Cs inner bearing ring [mm]
    d_1_D = gearbox.bearings_2.d_1_D                # Outer diameter of Ds inner bearing ring [mm]
    d_A_C = gearbox.bearings_2.d_A_C                # Outer diameter of bearing C [mm]
    d_A_D = gearbox.bearings_2.d_A_D                # Outer diameter of bearing D [mm]
    m_C = gearbox.bearings_2.m_C                    # Mass of bearing C [kg]
    m_D = gearbox.bearings_2.m_D                    # Mass of bearing D [kg]

    # Assign the values from the bearings of the third transmission stage (Bearings E and F)
    b_E = gearbox.bearings_3.b_E                    # Width of bearing E [mm]
    b_F = gearbox.bearings_3.b_F                    # Width of bearing F [mm]
    d_sh_E = gearbox.bearings_3.d_sh_E              # Inner diameter of bearing E [mm]
    d_sh_F = gearbox.bearings_3.d_sh_F              # Inner diameter of bearing F [mm]
    d_1_E = gearbox.bearings_3.d_1_E                # Outer diameter of Es inner bearing ring [mm]
    d_1_F = gearbox.bearings_3.d_1_F                # Outer diameter of Fs inner bearing ring [mm]

    # Assign the parameters from the gearbox shafts
    d_inn_1 = gearbox.shafts.d_inn_1                # Inner diameter of hollow sun shaft [mm]
    d_inn_p = gearbox.shafts.d_inn_p                # Inner diameter of hollow planet shafts [mm]
    d_sh_3 = gearbox.shafts.d_sh_3                  # Outer diameter of output shaft [mm]

    # Assign the mass of the planets
    m_planet = gearbox.masses.m_planet             # Mass of each planet with bearings [kg]

    # Assign the differential parameters
    d_diffcage = gearbox.differential.d_diffcage    # Diameter of differential cage [mm]
    if gearbox.Input.num_EM == 1:
        d_bev_l = gearbox.differential.d_bev_l      # Diameter of larger bevel gears in differential [mm]
        d_bev_s = gearbox.differential.d_bev_s      # Diameter of smaller bevel gears in differential [mm]
        b_bev = gearbox.differential.b_bev          # Width of bevel gears in differential [mm]
    else:   # Set variables to zero to avoid Pycharm warnings
        d_bev_l = 0
        d_bev_s = 0
        b_bev = 0
    # endregion

    # region [2]: Sun shaft: Calculation of the moment of inertia in kg*mm^2
    # Lengths of shaft segments left and right of wheel in mm
    l_1_1 = b_seal + b_F + 5 + b_C + b_gap - 5 - b_A
    l_1_2 = b_A
    l_1_3 = 5

    # Moment of inertia of shaft segments in kg*mm^2
    J_1_1 = math.pi/2 * (math.pow(d_sh_B/2, 4) - math.pow(d_inn_1/2, 4)) * l_1_1 * rho_gear
    J_1_2 = math.pi/2 * (math.pow(d_sh_A/2, 4) - math.pow(d_inn_1/2, 4)) * l_1_2 * rho_gear
    J_1_3 = math.pi/2 * (math.pow(d_1_A/2, 4) - math.pow(d_inn_1/2, 4)) * l_1_3 * rho_gear
    J_g1 = math.pi/2 * (math.pow(d_1/2, 4) - math.pow(d_inn_1/2, 4)) * b_1 * rho_gear

    # Total moment of inertia of the sun shaft in kg*mm^2
    J_1 = J_1_1 + J_1_2 + J_1_3 + J_g1
    # endregion

    # region [3]: Planets: Calculation of the moment of inertia in kg*mm^2
    # Planets about planet axis:
    d_p1a = d_fp1 - 6 * m_n_1
    J_p_1 = math.pi/2 * (math.pow(d_sh_C/2, 4) - math.pow(d_inn_p/2, 4)) * b_C * rho_gear
    J_p_2 = math.pi/2 * (math.pow(d_1_C/2, 4) - math.pow(d_inn_p/2, 4)) * b_gap * rho_gear
    J_gp1 = math.pi/2 * (math.pow(d_p1/2, 4) - math.pow(d_inn_p/2, 4)) * b_1 * rho_gear
    J_gp1_sub = math.pi/2 * (math.pow(d_p1a/2, 4) - math.pow(d_1_C/2, 4)) * 0.3 * b_1 * rho_gear
    J_p_3 = math.pi/2 * (math.pow(d_fp2/2, 4) - math.pow(d_inn_p/2, 4)) * b_gap * rho_gear
    J_gp2 = math.pi/2 * (math.pow(d_p2/2, 4) - math.pow(d_inn_p/2, 4)) * b_2 * rho_gear
    J_p_4 = math.pi/2 * (math.pow(d_1_D/2, 4) - math.pow(d_inn_p/2, 4)) * b_gap * rho_gear
    J_p_5 = math.pi/2 * (math.pow(d_sh_D/2, 4) - math.pow(d_inn_p/2, 4)) * b_D * rho_gear

    # Moment of inertia of the bearings on the planet axle
    J_C = math.pi/2 * (math.pow(d_1_C/2, 4) - math.pow(d_sh_C/2, 4)) * b_C * rho_gear
    J_D = math.pi/2 * (math.pow(d_1_D/2, 4) - math.pow(d_sh_D/2, 4)) * b_D * rho_gear

    # Total moment of inertia of one planet (about the planet axis)
    J_p = J_p_1 + J_p_2 + (J_gp1 - 2 * J_gp1_sub) + J_p_3 + J_gp2 + J_p_4 + J_p_5 + J_C + J_D

    # Moment of inertia of one planet about the center axis (plus pc bolts):
    m_p = m_planet - m_C - m_D + (((math.pow(d_1_C/2, 2) - math.pow(d_sh_C/2, 2)) * math.pi * b_C +
                                   (math.pow(d_1_D/2, 2) - math.pow(d_sh_D/2, 2)) * math.pi * b_D) * rho_gear)
    J_p_center = J_p + math.pow(d_s/2, 2) * m_p

    # Planet carrier with differential (planet carrier approximated as prisma with 3 sides):
    g_1 = (d_s/2 + 2 * (d_A_C/2 + 5) * (1 + math.sqrt(3)/2))
    g_2 = (d_s/2 + 2 * (d_A_D/2 + 5) * (1 + math.sqrt(3)/2))
    J_pc_1 = ((math.sqrt(3) * math.pow(g_1, 4))/48 - math.pi/2 * math.pow(d_A_A/2, 4)) * t_housing * rho_gear

    # Planet carrier bolts
    l_pcb = b_gap + b_1 + b_gap + b_2 + b_gap
    m_pcb = math.pow(d_planbolt/2, 2) * math.pi * l_pcb * rho_gear
    J_pcb = math.pi/2 * math.pow(d_planbolt/2, 4) * l_pcb * rho_gear + m_pcb * math.pow(d_s/2, 2)

    if gearbox.Input.num_EM == 1:
        J_pc_2 = ((math.sqrt(3) * math.pow(g_2, 4))/48 - math.pi/2 * math.pow(d_diffcage/2, 4)) * t_housing * rho_gear

        # Differential cage
        J_dc_1 = math.pi/2 * (math.pow(d_diffcage/2, 4) - math.pow(d_bev_l/2, 4)) * d_bev_s * rho_gear
        J_dc_2 = math.pi/2 * (math.pow((d_diffcage + d_1_E)/4, 4) - math.pow(d_sh_3/2 + 5, 4)) * 10 * rho_gear
        J_dc_3 = math.pi/2 * (math.pow(d_diffcage/2, 4) - math.pow(d_sh_3/2 + 5, 4)) * t_housing*rho_gear

        # Planet carrier side of bearing E:
        J_pc_E = math.pi/2 * (math.pow(d_sh_E/2, 4) - math.pow(d_sh_E/2-5, 4)) * b_E * rho_gear

        # Planet carrier side of bearing F:
        J_pc_F = math.pi/2 * (math.pow(d_sh_F/2, 4) - math.pow(d_A_A/2, 4)) * b_F * rho_gear + \
                 math.pi/2 * (math.pow(d_1_F/2, 4) - math.pow(d_A_A/2, 4)) * 5 * rho_gear

        # Bevel gears
        J_bev_l = math.pi/2 * (math.pow((d_bev_l + d_bev_l - b_bev)/4, 4) - math.pow(d_sh_3/2, 4)) * b_bev * rho_gear
        m_bev_s = (math.pow((d_bev_s + d_bev_s - b_bev)/4, 2)) * math.pi * b_bev * rho_gear
        J_bev_s = math.pi/2 * math.pow((d_bev_s + d_bev_s - b_bev)/4, 4) * b_bev * rho_gear + \
                  m_bev_s * math.pow((d_bev_l+d_bev_l-b_bev)/4, 2)

        # Differential bolt
        m_db = math.pow(d_diffbolt/2, 2) * math.pi * (d_bev_l - b_bev) * rho_gear
        J_db = 1/4 * m_db * math.pow(d_diffbolt/2, 2) + 1/12 * m_db * math.pow(d_bev_l-b_bev, 2)

        # Total moment of inertia of the planet carrier with differential
        J_pc = J_pc_1 + J_pc_2 + J_pcb + J_dc_1 + J_dc_2 + J_dc_3 + 2 * J_bev_l + 2 * J_bev_s + J_db + J_pc_E + J_pc_F

    else:       # There are two E-Machines located on the corresponding axle
        J_pc_2 = (math.sqrt(3) * math.pow(g_2, 4))/48 * t_housing * rho_gear

        # Bearing carriers differential shaft
        J_pc_E = math.pi/2 * math.pow(d_sh_E/2, 4) * (b_E + b_seal) * rho_gear
        J_pc_F = math.pi/2 * (math.pow(d_sh_F/2, 4) - math.pow(d_A_A/2, 4)) * b_F * rho_gear + \
                 math.pi/2 * (math.pow(d_1_F/2, 4) - math.pow(d_A_A/2, 4)) * 5 * rho_gear

        # Total moment of inertia of the planet carrier
        J_pc = J_pc_1 + J_pc_2 + J_pcb + J_pc_E + J_pc_F
    # endregion

    # region [4]: Bearings: Calculation of the moment of inertia in kg*mm^2
    # Moment of inertia of the bearings (approximated as spinning inner ring)
    J_A = math.pi/2 * (math.pow(d_1_A/2, 4) - math.pow(d_sh_A/2, 4)) * b_A * rho_gear
    J_B = math.pi/2 * (math.pow(d_1_B/2, 4) - math.pow(d_sh_B/2, 4)) * b_B * rho_gear
    J_E = math.pi/2 * (math.pow(d_1_E/2, 4) - math.pow(d_sh_E/2, 4)) * b_E * rho_gear
    J_F = math.pi/2 * (math.pow(d_1_F/2, 4) - math.pow(d_sh_F/2, 4)) * b_F * rho_gear
    # endregion

    # region [5]: Calculate total moment of inertia in kg*mm^2
    # Relative transmission ratio of the planets in relation to the planet carrier
    i_sp = (-2 * i_0)/(i_0 + 1)

    # Total reduced moment of inertia based on input shaft speed
    J_tot_in = (J_1 + J_A + J_B) + ((3 * J_p)/math.pow(i_p_rel, 2)) + ((3 * J_p_center + J_E + J_F + J_pc)/math.pow(i_1s, 2))

    # Total reduced moment of inertia based on wheel speed
    J_tot_out = ((J_1 + J_A + J_B) * math.pow(i_1s, 2)) + ((3 * J_p) * math.pow(i_sp, 2)) + (3 * J_p_center + J_E + J_F + J_pc)
    # endregion

    # region [6]: Output assignment
    setattr(gearbox.results, 'J_tot_in', J_tot_in)      # Moment of inertia with regard to input rotational speed in kg*mm^2
    setattr(gearbox.results, 'J_tot_out', J_tot_out)    # Moment of inertia with regard to output rotational speed in kg*mm^2
    # endregion

    return gearbox
