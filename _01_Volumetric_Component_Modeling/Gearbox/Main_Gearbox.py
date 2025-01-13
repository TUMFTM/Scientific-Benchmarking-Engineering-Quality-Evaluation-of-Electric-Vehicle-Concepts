"""
Description:    This Main is equivalent to the function calc_gearbox_dimensions,
                but differently from the function it allows a "standalone" run of the gearbox modeling
------------
Sources:    (1) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Semester Thesis, TUM, 2020
            (2) P. Koehler, "Semi-physikalische Modellierung von Antriebsstrangkomponenten fuer Elektrofahrzeuge", Master Thesis, TUM, 2020
------------
Input:   See section [1] of this script
------------
Output:  Gearbox housing dimensions, bearings dimensions, gears dimensions, shafts dimensions, transmission ratio etc.
------------

Implementation
[0] Import all necessary modules, classes and methods
[1] Create Parameters and Gearbox Class
[2] Assign Inputs
[3] Check if Inputs are valid
[4] Calculate gearbox dimension and mass
[5] Calc position of the gearbox
[6] Calculation of drive shaft mass
"""

# region [0] Import all necessary modules, classes and methods
# Import modules
import math
import os
import pickle
import pandas as pd
# Import classes
from _00_Preprocessing_Python.Vehicle_single_class.Class_Gearbox import Gearbox
# Import methods
from Lay_shaft.set_layshaft_transmission import set_layshaft_transmission
from Lay_shaft.calc_dimensions import calc_dimensions
from Planetary.set_planetary_transmission import set_planetary_transmission
from Planetary.calc_dimensions_plan import calc_dimensions_plan
from Lay_shaft.calc_mass_laysh import calc_mass_laysh
from Lay_shaft.calc_J_laysh import calc_J_laysh
from Planetary.calc_mass_planetary import calc_mass_planetary
from Planetary.calc_J_planetary import calc_J_planetary
from calc_gearbox_position_Main import calc_gearbox_position_Main
from calc_mass_driveshaft import calc_mass_driveshaft
# endregion


def Main_Gearbox():
    # region [1]: Create Parameters and Gearbox Class
    # load parameters and gearbox object
    gearbox = Gearbox()

    # Get the path of the Parameters.pkl file
    path_folder = os.path.abspath(os.path.join(__file__, os.path.join('..', '..', '..')))
    complete_name = os.path.join(path_folder, "_00_Preprocessing_Python", "Parameters" + ".pkl")

    # Parameters class file exists then load it
    with open(complete_name, 'rb') as input_parameters:
        parameters = pickle.load(input_parameters)

    # Get the path of the catalogues
    path_project = os.getcwd()
    path_catalogue = os.path.join(path_project, 'Catalogs')

    # Load ang_ball csv
    path_ang_ball = os.path.join(path_catalogue, 'ctlg_ang_ball_bearing.csv')
    setattr(parameters.gearbox.BearCtlg, 'ang_ball', pd.read_csv(path_ang_ball, sep=','))

    # Load ball csv
    path_ball = os.path.join(path_catalogue, 'ctlg_ball_bearing.csv')
    setattr(parameters.gearbox.BearCtlg, 'ball', pd.read_csv(path_ball, sep=','))

    # Load roller csv
    path_roller = os.path.join(path_catalogue, 'ctlg_tapfer_roller_bearing.csv')
    setattr(parameters.gearbox.BearCtlg, 'roller', pd.read_csv(path_roller, sep=','))
    # endregion

    # region [2]: Assign Inputs
    setattr(gearbox.Input, 'T_max', 250)                        # Maximum torque of el. motor [Nm]
    setattr(gearbox.Input, 'T_nom', 150)                        # Nominal torque of el. motor [Nm]
    setattr(gearbox.Input, 'i_tot', 9.66)                       # Total transmission ratio [-]
    setattr(gearbox.Input, 'n_nom', 4800)                       # Nominal engine speed [rpm]
    setattr(gearbox.Input, 'd_mot', 275)                        # Diameter of el. motor [mm]
    overload_factor = gearbox.Input.T_max/gearbox.Input.T_nom
    setattr(gearbox.Input, 'overload_factor', overload_factor)  # Overload factor of el. motor [-]
    setattr(gearbox.Input, 'inc_init', 0)                       # Angle between shafts with manual selection [deg]
    setattr(gearbox.Input, 'opt_gears', 'Height')               # Optimization goal (Height/Length/Mass/Manual)
    setattr(gearbox.Input, 'type', 'lay-shaft')                 # Type of transmission (lay-shaft/planetary)
    setattr(gearbox.Input, 'axles', 'parallel')                 # In- and output shafts parallel or coaxial
    setattr(gearbox.Input, 'num_EM', 1)                         # Number of el. motors on vehicle axle [-]
    setattr(gearbox.differential, 'diff_orientation', '')       # Desired orientation of the differential (empty for automatic selection)

    # Switch for manual selection of number of teeth and with that
    # transmission ratio
    setattr(gearbox.Input, 'manTR', 0)      # 0 for automatic selection, 1 for manual selection-> if 0 number of teeth is not required
    setattr(gearbox.Input, 'z_1', 36)       # Number of teeth of first wheel-> ONLY USED IF manTR=1
    setattr(gearbox.Input, 'z_2', 69)       # Number of teeth of second wheel-> ONLY USED IF manTR=1
    setattr(gearbox.Input, 'z_3', 23)       # Number of teeth of third wheel-> ONLY USED IF manTR=1
    setattr(gearbox.Input, 'z_4', -97)       # Number of teeth of forth wheel-> ONLY USED IF manTR=1

    # Material properties
    setattr(parameters.gearbox.MatProp, 'E_steel', 210000)      # Young's modulus of steel from Niemann/Winter, p. 372 [N/mm^2]
    setattr(parameters.gearbox.MatProp, 'sigma_fe', 860)        # Fatigue strength of 16MnCr5 from Zaehringer, p. xiv[N/mm^2]
    setattr(parameters.gearbox.MatProp, 'sigma_Hlim', 1470)     # Fatigue strength against gear flank pressure 16MnCr5 from Zaehringer, p. xiv [N/mm^2]
    setattr(parameters.gearbox.MatProp, 'R_mn', 900)            # Yield strength 16MnCr5 from Stahl, p. 135 [N/mm^2]
    setattr(parameters.gearbox.MatProp, 'tau_tw', 270)          # Torsional fatigue strength 16MnCr5 from Kirchner, p. 158 [N/mm^2]
    setattr(parameters.gearbox.MatProp, 'c_gamma', 20)          # Mesh stiffness steel/steel from Decker, p. 148 [N/mm*mym]
    setattr(parameters.gearbox.MatProp, 'rho_gear', 7760)       # Density 16MnCr5 from Zaehringer, p. 67 [kg/m^3]
    setattr(parameters.gearbox.MatProp, 'rho_alu', 2750)        # Density of housing material AlSi9Cu3 from Naunheimer, p. 517 [kg/m^3]

    # Gearing constants
    setattr(parameters.gearbox.GearingConst, 'epsilon_beta', 2)          # Desired overlap ratio [-]
    setattr(parameters.gearbox.GearingConst, 'm_n_1_min', 1.6)           # Minimum normal module of first stage [mm]
    setattr(parameters.gearbox.GearingConst, 'm_n_1_max', 2.6)           # Maximum normal module of first stage from Zaehringer, p. xxi [mm]
    setattr(parameters.gearbox.GearingConst, 'm_n_3_min', 2.0)           # Minimum normal module of second stage [mm]
    setattr(parameters.gearbox.GearingConst, 'm_n_3_max', 3.0)           # Maximum normal module of second stage from Zaehringer, p. xxi [mm]
    setattr(parameters.gearbox.GearingConst, 'alpha_n', 20*math.pi/180)  # Normal pressure angle [rad] --> 20deg
    setattr(parameters.gearbox.GearingConst, 'b_d_1', 0.58)              # Ratio of gear width and pitch diameter of first stage (empirical) [-]
    setattr(parameters.gearbox.GearingConst, 'b_d_3', 0.65)              # Ratio of gear width and pitch diameter of second stage (empirical) [-]
    setattr(parameters.gearbox.GearingConst, 'b_d_bevel', 0.22)          # Ratio of bevel gear width and outer diameter (empirical) [-]
    setattr(parameters.gearbox.GearingConst, 'd_bevel', 0.75)            # Ratio between smaller and larger bevel gears of the differential (empirical) [-]

    # Minimum safety factors
    setattr(parameters.gearbox.MinSafety, 'S_H_min', 1.0)   # Minimum safety factor against flank break from Niemann/Winter, p. 344 [-] (1.0-1.2)
    setattr(parameters.gearbox.MinSafety, 'S_F_min', 1.4)   # Minimum safety factor against root break from Niemann/Winter, p. 344 [-] (1.4-1.5)
    setattr(parameters.gearbox.MinSafety, 'S_Dt_min', 1.5)  # Minimum safety factor against torsional fatigue fracture from Stahl, p. 33 [-]

    # Constant dimensions
    setattr(parameters.gearbox.ConstDim, 'b_gap', 3)        # Gap between components on the shafts from Zaehringer, p. 64 [mm]
    setattr(parameters.gearbox.ConstDim, 'd_housing', 5.5)  # Distance between gears and housing as average of database [mm]
    setattr(parameters.gearbox.ConstDim, 't_housing', 5)    # Housing thickness as average of database [mm]
    setattr(parameters.gearbox.ConstDim, 'd_flange', 20)    # Additional space for screws on housing flange as average of database [mm]
    setattr(parameters.gearbox.ConstDim, 'b_seal', 12)      # Width of seals on output shafts as average of database [mm]
    setattr(parameters.gearbox.ConstDim, 'l_park', 100)     # Additional space for parking lock mechanism (database) [mm]
    setattr(parameters.gearbox.ConstDim, 'b_park', 13)      # Width of parking gear from Zaehringer, p. 64 [mm]
    setattr(parameters.gearbox.ConstDim, 't_diffcage', 6)   # Minimum thickness of differential housing [mm]
    setattr(parameters.gearbox.ConstDim, 'd_diffbolt', 18)  # Diameter of differential bolt from Zaehringer, p. 55 [mm]
    setattr(parameters.gearbox.ConstDim, 'd_planbolt', 20)  # Diameter of planet bolt [mm]

    # Calculation factors
    setattr(parameters.gearbox.CalcFactors, 'K_app', 1.5)                    # Application factor for static strength verification from DIN 3990-1, p.55 [-]
    setattr(parameters.gearbox.CalcFactors, 'K_1', 8.6)                      # Factor for calculation of dynamic factor K_v from DIN 3990-1, p. 18 [-]
    setattr(parameters.gearbox.CalcFactors, 'K_2', 0.0087)                   # Factor for calculation of dynamic factor K_v from DIN 3990-1, p. 18 [-]
    setattr(parameters.gearbox.CalcFactors, 'Z_E', math.sqrt(0.175*210000))  # Elasticity factor for material combination steel/steel from Decker, p. 151 [(N/mm^2)^1/2]
    setattr(parameters.gearbox.CalcFactors, 'L_10h', 2000)                   # Lifetime of the bearings at maximum torque with 10% default probability [h]
    setattr(parameters.gearbox.CalcFactors, 'L_10h_1', 600)                  # Lifetime of the bearings at maximum torque with 10% default probability [h], first gear
    setattr(parameters.gearbox.CalcFactors, 'L_10h_2', 800)                  # Lifetime of the bearings at maximum torque with 10% default probability [h], second gear
    L_10 = parameters.gearbox.CalcFactors.L_10h*60*gearbox.Input.n_nom/math.pow(10, 6)
    setattr(parameters.gearbox.CalcFactors, 'L_10', L_10)                   # Lifetime factor regarding input speed [10^6 revolutions]
    setattr(parameters.gearbox.CalcFactors, 'Z_H', 2.25)                    # Zonal factor for consideration of flank curvature from Naunheimer, p.287 [-]
    setattr(parameters.gearbox.CalcFactors, 'Z_eps', 0.95)                  # Overlap factor for tooth flank load capacity from Naunheimer, p.287 [-]
    setattr(parameters.gearbox.CalcFactors, 'Z_beta', 0.95)                 # Helix angle factor from Naunheimer, p.287 [-]
    setattr(parameters.gearbox.CalcFactors, 'K_a_1', 0.346)                 # Axle distance factor for first stage (empirical)
    setattr(parameters.gearbox.CalcFactors, 'K_a_2', 0.292)                 # Axle distance factor for second stage (empirical)
    setattr(parameters.gearbox.CalcFactors, 'K_b_1', 0.223)                 # Gear width factor for first stage (empirical)
    setattr(parameters.gearbox.CalcFactors, 'K_b_2', 0.145)                 # Gear width factor for second stage (empirical)
    # endregion

    # region [3]: Check if Inputs are valid
    # Check number of E-machines
    if gearbox.Input.num_EM not in (1, 2):
        print('The vehicle can only have exactly one or exactly two e-machines.')
        exit()
    if gearbox.Input.type.lower() not in ('lay-shaft', 'planetary'):
        print('The gearbox\' type has to be either lay-shaft or planetary')
        exit()
    if gearbox.Input.axles.lower() not in ('parallel', 'coaxial'):
        print('The lay shaft configuration of the gearbox must be either parallel or coaxial')
        exit()
    # endregion

    # region [4]: Calculate gearbox dimensions and mass
    if gearbox.Input.type.lower() == 'lay-shaft':
        # Calculation of lay-shaft gearbox parameters
        gearbox = set_layshaft_transmission(gearbox, parameters)
        # Calculation of gearbox main dimensions in mm
        gearbox = calc_dimensions(gearbox, parameters)
        # Calculation of gearbox mass in kg (parallel and coaxial design)
        gearbox = calc_mass_laysh(gearbox, parameters)
        # Calculation of gearbox moment of inertia in kg*mm^2 (parallel and coaxial design)
        gearbox = calc_J_laysh(gearbox, parameters)
    elif gearbox.Input.type.lower() == 'planetary':
        # Calculation of planetary gearbox parameters
        gearbox = set_planetary_transmission(gearbox, parameters)
        # Calculation of gearbox main dimensions in mm
        gearbox = calc_dimensions_plan(gearbox, parameters)
        # Calculation of gearbox mass in kg
        gearbox = calc_mass_planetary(gearbox, parameters)
        # Calculation of moment of inertia in kg*mm^2
        gearbox = calc_J_planetary(gearbox, parameters)
        pass
    # endregion

    # region [5]: Calc position of the gearbox
    # The values are based on the concept of the VW ID.3 but can easily be changed
    key = 'rear'
    wheelbase = 2766                # Wheelbase of the vehicle in mm
    tire_diameter = 701.5           # Tire Diameter in mm
    gear_orientation = {'position': 'front', 'ID': 1}
    CY_e_machine_length = 300       # Typical value just to make the function set_drive_shaft run
    calc_gearbox_position_Main(gearbox, parameters, key, wheelbase, tire_diameter, gear_orientation, CY_e_machine_length)
    # endregion

    # region [6]: Calculation of drive shaft mass
    gearbox = calc_mass_driveshaft(gearbox, parameters, CY_e_machine_length)
    # endregion

    print('Gearbox mass is: ', gearbox.masses.m_tot, ' kg')


if __name__ == "__main__":
    Main_Gearbox()
