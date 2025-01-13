"""
Description: This function assigns in a first step the dimensions of the cross member along the X
             direction (driving direction). After that the position of the cross members (at both front
             and rear axle) will be determined along the X direction.
             The used values are empirical values which where derived by Adrian König (1)
------------
Sources:   (1) A. König, "Methodik zur Auslegung von autonomen Fahrzeugkonzepten", Dissertation, Institute for Automotive Technology, TUM, 2022
           (2) T. Schröder, “Entwicklung geometrischer Ersatzmodelle für Komponenten des Vorderwagens,” Term Thesis, Institute for Automotive Technology, TUM, Munich, 2018.
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The vehicle structure updated with the position and dimensions of the crossbar
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Assign crossbar dimension parameters
[3] Calculate crossbar position
[4] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
# endregion


def calc_crossmember(vehicle):
    # region [1] Assign Inputs
    overhang_f = vehicle.dimensions.GX.vehicle_overhang_f               # Vehicle front overhang in mm
    overhang_r = vehicle.dimensions.GX.vehicle_overhang_r               # Vehicle rear overhang in mm
    wheelbase = vehicle.dimensions.GX.wheelbase                         # Vehicle wheelbase in mm
    width = vehicle.dimensions.GY.vehicle_width                         # Vehicle width in mm
    wheelhouse_f_width = vehicle.dimensions.CY.wheelhouse_f_width       # Front wheelhouse width in mm
    wheelhouse_r_width = vehicle.dimensions.CY.wheelhouse_r_width       # Rear wheelhouse width in mm
    # endregion

    # region [2] Assign crossbar dimension parameters
    # Assign the length of the cross member at the vehicle's front and rear end
    CX_crossmember_f = 48.20        # The length of the cross member at the vehicle's front end in mm
    CX_crossmember_r = 61.71        # The length of the cross member at the vehicle's rear end in mm

    # Assign the width of the cross member at the vehicle's front and rear end. Only for plot purposes. Assumed to be slightly wider than the distance comprised between the wheelhouses
    CY_crossmember_f = width - wheelhouse_f_width           # in mm
    CY_crossmember_r = width - wheelhouse_r_width * 1.5     # in mm

    # Assign the height of the cross member at the vehicle's front and rear end. Define the dimensions in Z using the value of (2)
    CZ_crossmember_f = 95.34    # in mm
    CZ_crossmember_r = 109.09   # in mm

    # Minimum distance between plate and cross member along the X direction (in mm)
    CX_plate_cross_member_front = 107.78
    CX_plate_cross_member_rear = 40.41
    # endregion

    # region [3] Calculate crossbar position
    CX_plate = 10
    CY_plate = 520
    CZ_plate = 110

    # Calculate position of the licence plate along X
    EX_licence_plate = overhang_f - CX_plate

    # Calculate position of the passenger safety foam along X
    EX_passenger_safety_foam = overhang_f - CX_plate_cross_member_front
    # The safety foam is only calculated at the front axle

    # Calculate position of the crossmember at front and rear axle
    EX_crossmember_front_axle = overhang_f - CX_plate_cross_member_front - CX_crossmember_f
    EX_crossmember_rear_axle = overhang_r + wheelbase - CX_plate_cross_member_rear - CX_crossmember_r
    # endregion

    # region [4] Assign Outputs
    setattr(vehicle.dimensions.CX, 'crossmember_f', CX_crossmember_f)   # in mm
    setattr(vehicle.dimensions.CX, 'crossmember_r', CX_crossmember_r)   # in mm

    setattr(vehicle.dimensions.CY, 'crossmember_f', CY_crossmember_f)   # in mm
    setattr(vehicle.dimensions.CY, 'crossmember_r', CY_crossmember_r)   # in mm

    setattr(vehicle.dimensions.CZ, 'crossmember_f', CZ_crossmember_f)   # in mm
    setattr(vehicle.dimensions.CZ, 'crossmember_r', CZ_crossmember_r)   # in mm

    # X position crossmember in mm
    setattr(vehicle.dimensions.EX, 'crossmember_front_axle', EX_crossmember_front_axle)
    setattr(vehicle.dimensions.EX, 'crossmember_rear_axle', EX_crossmember_rear_axle)

    # Dimensions and position of the licence plate in mm
    setattr(vehicle.dimensions.CX, 'licence_plate', CX_plate)
    setattr(vehicle.dimensions.CY, 'licence_plate', CY_plate)
    setattr(vehicle.dimensions.CZ, 'licence_plate', CZ_plate)
    setattr(vehicle.dimensions.EX, 'licence_plate_front_axle', EX_licence_plate)

    # Dimensions and position of the passenger foam in mm (only for front axle)
    setattr(vehicle.dimensions.CX, 'passenger_safety_foam', CX_plate_cross_member_front)
    setattr(vehicle.dimensions.CY, 'passenger_safety_foam', CY_crossmember_f)
    setattr(vehicle.dimensions.EX, 'passenger_safety_foam', EX_passenger_safety_foam)
    # endregion

    return vehicle
