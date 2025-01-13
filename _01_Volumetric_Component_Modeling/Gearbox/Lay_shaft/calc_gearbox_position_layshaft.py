"""
Description:    This function positions the layshaft gearbox according to the
                calculated gearbox dimensions and the chosen topology. The position of
                the gearbox is furthermore required to position the electric machine (see
                function calc_EM_position)
------------
Sources:    None
------------
Input:   gearbox:    Class where all results of the gearbox calculation are saved
         parameters: Class element which stores all necessary computation parameters
         axle_id: ID of the considered axes (front == 0, rear == 1)
         gearbox_orientation: Position of the gearbox in relation to the axle ('front', 'coaxial', 'rear')
         wheelbase: Wheelbase of the considered vehicle
         CX_wheel: Diameter of the wheels at front and rear axle in mm
         CY_e_machine_length: Length of the e_machine in mm
------------
Output:  Defined position of the planetary gearbox
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Assign global inputs
[2] Parallel lay-shaft gearbox
[2.1] Load the required variable for the parallel gearbox positioning
[2.2] Calculate the X-position of the gearbox shafts
[2.3] Calculate the Y-position of the gearbox shafts
[2.4] Calculate the Z-position of the gearbox shafts
[3] Coaxial layshaft gearbox
[3.1] Load the required variable for the coaxial gearbox positioning
[3.2] Calculate the X-position of the gearbox shafts
[3.3] Calculate the Y-position of the gearbox shafts
[3.4] Calculate the Z-position of the gearbox shafts
[4] Calculate the position of the gearbox housing
[5] Assign Outputs
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
import numpy as np
# Import classes
# Import methods
# endregion


def calc_gearbox_position_layshaft(gearbox, parameters, axle_id, gearbox_orientation, wheelbase, CX_wheel, CY_e_machine_length):
    # region [1]: Assign global inputs
    # Gearbox axis dimensions
    a_12 = gearbox.results.a_12                     # Axis distance between shafts 1-2

    # Gearbox toothwheel dimensions
    b_1 = gearbox.gears_12.b_1                      # Width of wheel 1 in mm
    b_A = gearbox.bearings_1.b_A                    # Width first gearbox on the first shaft (output shaft of the e-machine) in mm
    b_F = gearbox.bearings_3.b_F                    # Width of bearing F
    b_gap = parameters.gearbox.ConstDim.b_gap       # Minimum distance between wheel and bearing in mm
    b_seal = parameters.gearbox.ConstDim.b_seal     # Width of sealings in mm
    d_flange = parameters.gearbox.ConstDim.d_flange # Width of flange for screwing of the gearbox housing
    b_3 = gearbox.gears_34.b_3                      # Width of wheel 3 in mm
    b_C = gearbox.bearings_2.b_C                    # Width of bearing C in mm
    b_diffcage = gearbox.differential.b_diffcage    # Width of the differential cage in mm
    d_diff = gearbox.gears_34.d_4                   # Diameter of the differential wheel in mm

    # Gearbox housing dimensions
    t_housing = parameters.gearbox.ConstDim.t_housing         # Housing thickness in mm
    d_housing = parameters.gearbox.ConstDim.d_housing         # Distance between gears and housing in mm
    tot_length_housing = gearbox.dimension_house.l_gearbox    # Total gearbox housing length in mm
    tot_width_housing = gearbox.dimension_house.t_gearbox     # Total gearbox housing width in mm
    # endregion

    # region [2]: Parallel lay-shaft gearbox
    if gearbox.Input.axles.lower() == 'parallel':
        # region [2.1]: Load the required variable for the parallel gearbox positioning
        # Gearbox axis dimensions:
        a_23 = gearbox.results.a_23         # Axis distance between shafts 2-3
        theta = gearbox.results.theta       # Orientation angle between shafts 1-2 in RAD
        zeta = gearbox.results.zeta         # Orientation angle between shafts 2-3 in RAD

        # Gearbox toothwheel dimensions
        b_park = parameters.gearbox.ConstDim.b_park                 # Width of parking wheel in mm
        b_E = gearbox.bearings_3.b_E                                # Width of bearing E in mm
        diff_orientation = gearbox.differential.diff_orientation    # Orientation of the differential (in/out)
        # endregion

        # region [2.2]: Calculate the X-position of the gearbox shafts
        EX_shaft_3_front_axle = wheelbase * axle_id       # X position shaft 3 (differential shaft)
        # X position shaft 2
        EX_shaft_2_front_axle = wheelbase * axle_id + (a_23 * math.cos(zeta))*(-gearbox_orientation['ID'])
        # X position shaft 1
        EX_shaft_1_front_axle = wheelbase * axle_id + (a_23 * math.cos(zeta) + a_12 * math.cos(theta)) * (-gearbox_orientation['ID'])
        # endregion

        # region [2.3]:  Calculate the Y-position of the gearbox shafts
        # Workflow: If we have only one machine per axle, calculate the total required space for the gearbox machine combination in Y direction
        # and position the machine-gearbox combination in the very middle of the vehicle. If we have two machine per axle calculate the width
        # of both machines and gearbox and position it in the middle of the vehicle
        if gearbox.Input.num_EM == 2:  # there are 2 machine on the axle -> Minimum distance in Y direction between the 2 machine is 30 mm

            CY_gearbox_machine = 2 * (tot_width_housing + CY_e_machine_length) + 30
        else:    # There is only on e_machine on the axle
            CY_gearbox_machine = tot_width_housing + CY_e_machine_length

        # Minimum distance between gearbox and vehicle center in Y
        EY_gearbox_vehicle_center = CY_gearbox_machine * 0.5 - tot_width_housing

        # Position the element of shaft 1 (wheel, bearing A and bearing B)
        if gearbox.Input.num_EM == 1 and diff_orientation.lower() == 'in':
            EY_gearbox_bearing_A = EY_gearbox_vehicle_center + (b_seal + b_diffcage + b_E) -\
                                   (b_gap + b_1 + b_gap + b_park + b_gap + b_A)
        else:
            EY_gearbox_bearing_A = EY_gearbox_vehicle_center + b_seal

        EY_gearbox_wheel_1 = EY_gearbox_bearing_A + b_A + b_gap + b_park + b_gap
        EY_gearbox_bearing_B = EY_gearbox_wheel_1 + b_1 + b_gap

        # Position the element of shaft 2 (wheels, bearing C and bearing D)
        EY_gearbox_wheel_2 = EY_gearbox_wheel_1
        EY_gearbox_shaft_2 = EY_gearbox_wheel_2 + b_1
        EY_gearbox_wheel_3 = EY_gearbox_shaft_2 + b_gap
        EY_gearbox_bearing_C = EY_gearbox_wheel_2 - b_gap - b_C
        EY_gearbox_bearing_D = EY_gearbox_wheel_2 + b_1 + b_gap + b_3 + b_gap

        # Position the element of shaft 3 (wheel, bearing E and bearing F and differential cage)
        EY_gearbox_wheel_4 = EY_gearbox_wheel_3
        if diff_orientation.lower() == 'in':
            EY_diff_cage = EY_gearbox_wheel_4 - b_diffcage
            EY_gearbox_bearing_E = EY_diff_cage - b_E
            EY_gearbox_bearing_F = EY_gearbox_wheel_4 + b_3 + b_gap
        else:
            EY_diff_cage = EY_gearbox_wheel_4 + b_3
            EY_gearbox_bearing_E = EY_diff_cage + b_diffcage
            EY_gearbox_bearing_F = EY_gearbox_wheel_4 - b_gap - b_1 - b_gap - b_F
        # endregion

        # region [2.4]: Calculate the Z-position of the gearbox shafts
        # The differential shaft is positioned at the same height of the axle. The other shaft are positioned correspondingly to the
        # calculated theta and zeta
        EZ_shaft_3_front_axle = CX_wheel[axle_id]/2
        EZ_shaft_2_front_axle = EZ_shaft_3_front_axle + a_23 * math.sin(zeta)
        EZ_shaft_1_front_axle = EZ_shaft_3_front_axle + a_23 * math.sin(zeta) + a_12 * math.sin(theta)
        # endregion
    # endregion

    # region [3]: Coaxial layshaft gearbox
    else:
        # region [3.1]: Load the required variable for the coaxial gearbox positioning
        # Gearbox toothwheel dimensions
        b_B = gearbox.bearings_1.b_B                            # Width of bearing B
        # endregion

        # region [3.2]: Calculate the X-position of the gearbox shafts
        EX_shaft_3_front_axle = wheelbase * axle_id                                         # X position shaft 3 (differential shaft)
        EX_shaft_2_front_axle = wheelbase * axle_id + a_12 * (-gearbox_orientation['ID'])   # X position shaft 2
        EX_shaft_1_front_axle = wheelbase * axle_id
        # endregion

        # region [3.3]:  Calculate the Y-position of the gearbox shafts
        # Workflow: If we have only one machine per axle, calculate the total required space for the gearbox machine combination in Y direction
        # and position the machine-gearbox combination in the very middle of the vehicle. If we have two machine per axle calculate the width
        # of both machines and gearbox and position it in the middle of the vehicle
        if gearbox.Input.num_EM == 2:  # there are 2 machine on the axle -> Minimum distance in Y direction between the 2 machine is 30 mm
            CY_gearbox_machine = 2 * (tot_width_housing + CY_e_machine_length) + 30
        else:   # There is only one e_machine on the axle
            CY_gearbox_machine = tot_width_housing + CY_e_machine_length

        # Minimum distance between gearbox and vehicle center in Y
        EY_gearbox_vehicle_center = CY_gearbox_machine * 0.5 - tot_width_housing

        # Position the element of shaft 1 (wheel, bearing A and bearing B)
        EY_gearbox_bearing_A = EY_gearbox_vehicle_center + b_seal
        EY_gearbox_wheel_1 = EY_gearbox_bearing_A + b_A + b_gap
        EY_gearbox_bearing_B = EY_gearbox_wheel_1 + b_1 + b_gap

        # Position the element of shaft 2 (wheels, bearing C and bearing D)
        EY_gearbox_wheel_2 = EY_gearbox_wheel_1
        EY_gearbox_shaft_2 = EY_gearbox_wheel_2 + b_1
        EY_gearbox_wheel_3 = EY_gearbox_shaft_2 + b_gap + b_B + b_gap + b_F + b_gap
        EY_gearbox_bearing_C = EY_gearbox_wheel_2 - b_gap - b_C
        EY_gearbox_bearing_D = EY_gearbox_wheel_3 + b_3 + b_gap

        # Position the element of shaft 3 (wheel, bearing E and bearing F and differential cage)
        EY_gearbox_wheel_4 = EY_gearbox_wheel_3
        EY_diff_cage = EY_gearbox_wheel_4 + b_3
        EY_gearbox_bearing_E = EY_diff_cage + b_diffcage
        EY_gearbox_bearing_F = EY_gearbox_wheel_4 - b_gap - b_F
        # endregion

        # region [3.4]:  Calculate the Z-position of the gearbox shafts
        # The differential shaft is positioned at the same height of the axle. The other shaft are positioned correspondingly to the
        # calculated theta and zeta
        EZ_shaft_3_front_axle = CX_wheel[axle_id]/2
        EZ_shaft_2_front_axle = EZ_shaft_3_front_axle    # May be changed
        EZ_shaft_1_front_axle = EZ_shaft_3_front_axle
        # endregion
    # endregion

    # region [4]: Calculate the position of the gearbox housing
    # X position of the housing with respect to the front axle
    EX_gearbox_housing = np.zeros(2)
    if gearbox_orientation['position'].lower() == 'front':      # Gearbox is in front of the axle
        EX_gearbox_housing[0] = wheelbase * axle_id - tot_length_housing + d_flange + t_housing + d_housing + d_diff/2
        EX_gearbox_housing[1] = EX_gearbox_housing[0] + tot_length_housing
    else:  # Gearbox is behind the axle
        EX_gearbox_housing[0] = wheelbase * axle_id - (d_flange + t_housing + d_housing + d_diff/2)
        EX_gearbox_housing[1] = EX_gearbox_housing[0]+tot_length_housing

    # Y position of the housing with respect to the front axle
    EY_gearbox_housing = np.zeros(2)
    EY_gearbox_housing[0] = EY_gearbox_vehicle_center   # Minimum distance between gearbox and vehicle center in Y
    EY_gearbox_housing[1] = CY_gearbox_machine * 0.5    # Maximum distance between gearbox and vehicle center in Y

    # Z position of the housing with respect to the front axle
    EZ_gearbox_housing = np.zeros(2)
    EZ_gearbox_housing[0] = (CX_wheel[axle_id] - d_diff) * 0.5 - d_flange - t_housing - d_housing
    EZ_gearbox_housing[1] = (CX_wheel[axle_id] + d_diff) * 0.5 + d_flange + t_housing + d_housing
    # endregion

    # region [5]: Assign Outputs
    setattr(gearbox.position, 'EX_shaft_1_front_axle', EX_shaft_1_front_axle)
    setattr(gearbox.position, 'EX_shaft_2_front_axle', EX_shaft_2_front_axle)
    setattr(gearbox.position, 'EX_shaft_3_front_axle', EX_shaft_3_front_axle)
    setattr(gearbox.position, 'EY_gearbox_bearing_A', EY_gearbox_bearing_A)
    setattr(gearbox.position, 'EY_gearbox_bearing_B', EY_gearbox_bearing_B)
    setattr(gearbox.position, 'EY_gearbox_wheel_1', EY_gearbox_wheel_1)
    setattr(gearbox.position, 'EY_gearbox_wheel_2', EY_gearbox_wheel_2)
    setattr(gearbox.position, 'EY_gearbox_wheel_3', EY_gearbox_wheel_3)
    setattr(gearbox.position, 'EY_gearbox_shaft_2', EY_gearbox_shaft_2)
    setattr(gearbox.position, 'EY_gearbox_bearing_C', EY_gearbox_bearing_C)
    setattr(gearbox.position, 'EY_gearbox_bearing_D', EY_gearbox_bearing_D)
    setattr(gearbox.position, 'EY_diff_cage', EY_diff_cage)
    setattr(gearbox.position, 'EY_gearbox_bearing_E', EY_gearbox_bearing_E)
    setattr(gearbox.position, 'EY_gearbox_bearing_F', EY_gearbox_bearing_F)
    setattr(gearbox.position, 'EZ_shaft_1_front_axle', EZ_shaft_1_front_axle)
    setattr(gearbox.position, 'EZ_shaft_2_front_axle', EZ_shaft_2_front_axle)
    setattr(gearbox.position, 'EZ_shaft_3_front_axle', EZ_shaft_3_front_axle)
    setattr(gearbox.position, 'EY_gearbox_wheel_4', EY_gearbox_wheel_4)
    setattr(gearbox.position, 'EX_gearbox_housing', EX_gearbox_housing)
    setattr(gearbox.position, 'EY_gearbox_housing', EY_gearbox_housing)
    setattr(gearbox.position, 'EZ_gearbox_housing', EZ_gearbox_housing)
    # endregion

    return gearbox
