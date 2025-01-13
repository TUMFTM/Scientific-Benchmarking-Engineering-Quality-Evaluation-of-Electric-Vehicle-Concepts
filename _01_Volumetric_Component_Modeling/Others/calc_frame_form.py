"""
Description: This function uses discretized frameforms (which where derived from picture analysis) to plot the
             exterieur of the vehicle. The frameform are done for the following vehicles:
             -> Hatchback: A1
             -> Sedan: A8
             -> SUV: Q5
             Since the proportion of the frameforms do not necessarily represent the simulated vehicle dimensions
             (overhangs, wheelbase and height), the frameform point cloud is scaled
------------
Sources: (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", Technical University of Munich, Institute of Automotive Technology, 2022
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: A point cloud (expressed as tri-dimensional vector) describing the frame form of the vehicle.
        This result will be used in the calculation of the trunk volume
------------

Implementation
[0] Import modules, classes and functions
[1] Assign Inputs
[2] Load the desired frameform point cloud
[3] Calculate the frameform overhangs and scaling factors
[4] Scale middle part of the vehicle
[5] Scale front-end of the vehicle
[6] Scale rear-end of the vehicle
[7] Assign Outputs
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
import os
import json
import numpy as np
# endregion


def calc_frame_form(vehicle):

    # region [1] Assign Inputs
    frameform_str = vehicle.topology.frameform              # Chosen frameform (Hatchback, Sedan, SUV)
    wheelbase = vehicle.dimensions.GX.wheelbase             # Wheelbase of the simulated vehicle in mm
    overhang_f = vehicle.dimensions.GX.vehicle_overhang_f   # Front overhang of the simulated vehicle in mm
    overhang_r = vehicle.dimensions.GX.vehicle_overhang_r   # Rear overhang of the simulated vehicle in mm
    height = vehicle.dimensions.GZ.vehicle_height           # Height of the simulated vehicle in mm
    # endregion

    # region [2] Load the desired frameform point cloud
    # Get the path where the frameform is stored
    path_project = os.getcwd()
    path_frameform = os.path.join(path_project, '_04_Visualization', 'Frameform')

    suffix_file = 'frameform_' + frameform_str.lower() + '.json'
    file_frameform = os.path.join(path_frameform, suffix_file)      # Loading path

    # Open the json file
    with open(file_frameform, "r") as f:
        frameform_json = json.load(f)
    wheelbase_orig = frameform_json['wheelbase_frameform']
    height_orig = frameform_json['height_frameform']

    # Initialize all three directions of the frameform point cloud
    size_outline = len(frameform_json['frameform'])
    frameform = np.zeros((size_outline, 3))

    # Fill each direction with the data of the point cloud
    for i, point in enumerate(frameform_json['frameform']):
        frameform[i, 0] = point[0]  # Pointcloud in X-Direction
        frameform[i, 1] = point[1]  # Pointcloud in Y-Direction
        frameform[i, 2] = point[2]  # Pointcloud in Z-Direction
    # endregion

    # region [3] Calculate the frameform overhangs and scaling factors
    # Retrieve the overhangs of the reference frameform
    overhang_f_frameform = abs(min(frameform[:, 0]))
    overhang_r_frameform = max(frameform[:, 0]) - wheelbase_orig

    # Calculate the scaling factor for the 3 frameform areas in x direction
    scale_x_rear_area = overhang_r/overhang_r_frameform
    scale_x_front_area = overhang_f/overhang_f_frameform
    scale_x_middle_area = wheelbase/wheelbase_orig

    # Calculate the scaling factor in Z direction (equal for all the areas)
    scale_z = height/height_orig
    # endregion

    # region [4] Scale middle part of the vehicle
    # Derive the middle area (wheelbase area)
    middle_area = frameform[frameform[:, 0] >= 0, :]
    middle_area = middle_area[middle_area[:, 0] <= wheelbase_orig, :]

    # Scale the middle area (wheelbase area)
    middle_area[:, 0] = middle_area[:, 0] * scale_x_middle_area
    middle_area[:, 2] = middle_area[:, 2] * scale_z

    # Shift the middle area (wheelbase area)
    offset_z = height - max(middle_area[:, 2])
    middle_area[:, 2] = middle_area[:, 2] + offset_z
    # endregion

    # region [5] Scale front-end of the vehicle
    # Derive the front area (front overhang area)
    front_area = frameform[frameform[:, 0] < 0, :]

    # Scale the front area (front overhang area)
    front_area[:, 0] = front_area[:, 0] * scale_x_front_area
    front_area[:, 2] = front_area[:, 2] * scale_z

    # Shift the front area (front overhang area)
    idx = np.argmin(middle_area[:, 0])
    z_idm_front = middle_area[idx, 2]           # Z coord of the point middle area in contact with the front area
    idx = np.argmax(front_area[:, 0])
    z_idf_front = front_area[idx, 2]            # Z coord of the point front area in contact with the middle area

    offset_f_z = z_idm_front - z_idf_front      # Offset so that the 2 points are at the same height

    front_area[:, 2] = front_area[:, 2] + offset_f_z    # Shift in Z
    # endregion

    # region [6] Scale rear-end of the vehicle
    # Derive the rear area (rear overhang area)
    rear_area = frameform[frameform[:, 0] > wheelbase_orig, :]

    # Scale the rear area (rear overhang area)
    rear_area[:, 0] = rear_area[:, 0] * scale_x_rear_area
    rear_area[:, 2] = rear_area[:, 2] * scale_z

    # Shift the rear area (rear overhang area)
    idx = np.argmax(middle_area[:, 0])
    x_idm_rear = middle_area[idx, 0]                # X coord of the point of the middle area close to the rear one
    z_idm_rear = middle_area[idx, 2]                # Z coord of the point of the middle area close to the rear one
    idx = np.argmin(rear_area[:, 0])
    x_idr_rear = rear_area[idx, 0]                  # X coord of the point of the rear area close to the middle one
    z_idr_rear = rear_area[idx, 2]                  # Z coord of the point of the rear area close to the middle one

    offset_rear_area_z = z_idm_rear - z_idr_rear    # Offset so that the 2 points are at the same height
    offset_rear_area_x = x_idm_rear - x_idr_rear    # Offset so that the 2 points are at the same length

    rear_area[:, 0] = rear_area[:, 0] + offset_rear_area_x      # Shift in X
    rear_area[:, 2] = rear_area[:, 2] + offset_rear_area_z      # Shift in Z
    # endregion

    # region [7] Assign Outputs
    # The point cloud is expressed in mm and referenced to the coordinate system of the vehicle
    setattr(vehicle.exterior, 'frameform_rear_sec', rear_area)
    setattr(vehicle.exterior, 'frameform_front_sec', front_area)
    setattr(vehicle.exterior, 'frameform_middle_sec', middle_area)
    # endregion

    return vehicle
