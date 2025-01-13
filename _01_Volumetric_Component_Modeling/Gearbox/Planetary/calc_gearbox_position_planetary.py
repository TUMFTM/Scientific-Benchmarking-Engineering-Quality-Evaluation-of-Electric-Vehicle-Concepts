"""
Description:    This function positions the planetary gearbox according to the
                calculated gearbox dimensions and the chosen topology. The position of
                the gearbox is furthermore required to position the electric machine (see function calc_EM_position)
------------
Sources:    None
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
         axle_id: ID of the considered axes (front == 0, rear == 1)
         wheelbase: Wheelbase of the considered vehicle
         CX_wheel: Diameter of the wheels at front and rear axle in mm
         CY_e_machine_length: Length of the e_machine in mm
------------
Output:  Defined position of the planetary gearbox
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Assign Inputs
[2] Gearbox Y-Position determination
[3] Compute position of sun shaft
[4] Determination of planets position
[5] Determination of differential position
[6] Position of the planet carrier bolts
[7] Calculate the position of the gearbox housing
[8] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
import numpy as np
# Import classes
# Import methods
# endregion


def calc_gearbox_position_planetary(gearbox, parameters, axle_id, wheelbase, CX_wheel, CY_e_machine_length):
    # region [1]: Assign Inputs
    b_gap = parameters.gearbox.ConstDim.b_gap       # Minimum distance between wheel and bearing
    b_seal = parameters.gearbox.ConstDim.b_seal     # Width of sealings
    b_1 = gearbox.gears_12.b_1                      # Width of first stage gears
    b_2 = gearbox.gears_12.b_2                      # Width of second stage gears

    # Bearing width in mm (for bearings A,C,D,E,F)
    b_A = gearbox.bearings_1.b_A
    b_C = gearbox.bearings_2.b_C
    b_D = gearbox.bearings_2.b_D
    b_F = gearbox.bearings_3.b_F

    tot_width_housing = gearbox.dimension_house.t_gearbox   # Total width of the planetary gearbox housing in mm
    d_gearbox = gearbox.dimension_house.d_gearbox           # Diameter of the planetary gearbox housing in mm
    d_p2 = gearbox.gears_12.d_p2                            # Diameter of planet 2

    # Dimensions differental cage in mm
    d_diffcage = gearbox.differential.d_diffcage
    b_diffcage = gearbox.differential.b_diffcage

    # Dimensions and position of planet bolts in mm
    d_s = gearbox.gears_12.d_s                              # Diameter of planet circle
    d_planbolt = parameters.gearbox.ConstDim.d_planbolt     # Diameter of planet bolts

    d_A_C = gearbox.bearings_2.d_A_C
    d_A_D = gearbox.bearings_2.d_A_D
    ang_plan = 60 * math.pi/180                             # Angle between planets
    r = 0.5 * (d_s/2 + min(d_A_C, d_A_D) - d_planbolt)      # Radius of planet carrier bolts
    # endregion

    # region [2]: Gearbox Y-Position determination
    if gearbox.Input.num_EM == 2:
        # there are 2 machine on the axle -> Minimum distance in Y direction between the 2 machine is 30 mm
        CY_gearbox_machine = 2 * (tot_width_housing + CY_e_machine_length) + 30

    else:   # There is only on e_machine on the axle
        CY_gearbox_machine = tot_width_housing + CY_e_machine_length

    EY_gearbox_vehicle_center = CY_gearbox_machine * 0.5 - tot_width_housing
    # endregion

    # region [3]: Compute position of sun shaft
    # X and Z Position of the sun shaft
    EX_shaft_1_front_axle = wheelbase * axle_id
    EZ_shaft_1_front_axle = CX_wheel[axle_id] / 2

    # Y Position of the different gearbox elements:
    EY_gearbox_bearing_A = EY_gearbox_vehicle_center + b_seal + b_F + b_C + b_gap - b_A
    EY_sun = EY_gearbox_bearing_A + 5 + b_A
    # endregion

    # region [4]: Determination of planets position
    EY_plan_2 = EY_sun + b_gap + b_1

    # Position of the bearings C and D
    EY_gearbox_bearing_C = EY_sun - b_gap - b_C
    EY_gearbox_bearing_D = EY_plan_2 + b_2 + b_gap
    # endregion

    # region [5]: Determination of differential position
    if gearbox.Input.num_EM == 1 and (d_s - d_p2 - 2) > d_diffcage:
        # Integration of differential in planet carrier if planet circle is large enough
        EY_diff = EY_plan_2
    else:
        EY_diff = EY_gearbox_bearing_D + b_D + 5

    # Position of the beatings E and F
    EY_gearbox_bearing_E = EY_diff + b_diffcage
    EY_gearbox_bearing_F = EY_gearbox_bearing_C - 5 - b_F
    # endregion

    # region [6]: Position of the planet carrier bolts
    EX_pcb_1 = EX_shaft_1_front_axle + r * math.cos(ang_plan/2)
    EX_pcb_2 = EX_shaft_1_front_axle - r * math.cos(ang_plan/2)
    EX_pcb_3 = EX_shaft_1_front_axle
    EY_pcb = EY_gearbox_bearing_C + b_C
    EZ_pcb_1 = EZ_shaft_1_front_axle + r * math.sin(ang_plan/2)
    EZ_pcb_2 = EZ_pcb_1
    EZ_pcb_3 = EZ_shaft_1_front_axle - r
    # endregion

    # region [7]: Calculate the position of the gearbox housing
    # X position of the housing with respect to the front axle
    EX_gearbox_housing = np.zeros(2)
    EX_gearbox_housing[0] = wheelbase * axle_id - d_gearbox * 0.5
    EX_gearbox_housing[1] = wheelbase * axle_id + d_gearbox * 0.5

    # Y position of the housing with respect to the front axle
    EY_gearbox_housing = np.zeros(2)
    EY_gearbox_housing[0] = EY_gearbox_vehicle_center
    EY_gearbox_housing[1] = CY_gearbox_machine * 0.5

    # Z position of the housing with respect to the front axle
    EZ_gearbox_housing = np.zeros(2)
    EZ_gearbox_housing[0] = -d_gearbox * 0.5
    EZ_gearbox_housing[1] = d_gearbox * 0.5
    # endregion

    # region [8]: Assign Outputs
    setattr(gearbox.position, 'EX_shaft_1_front_axle', EX_shaft_1_front_axle)
    setattr(gearbox.position, 'EZ_shaft_1_front_axle', EZ_shaft_1_front_axle)
    setattr(gearbox.position, 'EY_gearbox_bearing_A', EY_gearbox_bearing_A)
    setattr(gearbox.position, 'EY_sun', EY_sun)
    setattr(gearbox.position, 'EY_plan_2', EY_plan_2)
    setattr(gearbox.position, 'EY_gearbox_bearing_C', EY_gearbox_bearing_C)
    setattr(gearbox.position, 'EY_gearbox_bearing_D', EY_gearbox_bearing_D)
    setattr(gearbox.position, 'EY_diff', EY_diff)
    setattr(gearbox.position, 'EY_gearbox_bearing_E', EY_gearbox_bearing_E)
    setattr(gearbox.position, 'EY_gearbox_bearing_F', EY_gearbox_bearing_F)
    setattr(gearbox.position, 'EX_pcb_1', EX_pcb_1)
    setattr(gearbox.position, 'EX_pcb_2', EX_pcb_2)
    setattr(gearbox.position, 'EX_pcb_3', EX_pcb_3)
    setattr(gearbox.position, 'EY_pcb', EY_pcb)
    setattr(gearbox.position, 'EZ_pcb_1', EZ_pcb_1)
    setattr(gearbox.position, 'EZ_pcb_2', EZ_pcb_2)
    setattr(gearbox.position, 'EZ_pcb_3', EZ_pcb_3)
    setattr(gearbox.position, 'EX_gearbox_housing', EX_gearbox_housing)
    setattr(gearbox.position, 'EY_gearbox_housing', EY_gearbox_housing)
    setattr(gearbox.position, 'EZ_gearbox_housing', EZ_gearbox_housing)
    # endregion

    return gearbox
