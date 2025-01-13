"""
Description:  This function fills the underfloor and calculates how many cell fit in total.
              The cell dimensions calculated in this function are later used to fill all the other areas of the vehicle.
              More information to the battery model can be found in Chapters 3.4.6 of (1) and Chapter 4.6 of (3)
------------
Sources:  (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", P. D. Thesis, Technical University of Munich, Institute of Automotive Technology, 2022
          (2) P. Köhler, „Semi-physikalische Modellierung von Antriebsstrangkomponenten für Elektrofahrzeuge,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021
          (3) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
------------
Input: vehicle: Class element, which stores all values of the vehicle
       underfloor_dim: The dimensions of the underfloor as vector [X,Y,Z]
       cell_dim_underfloor: Dimensions of all cells that may fit into the underfloor
       pack_dim_underfloor: Dimensions of all packs that may fit into the underfloor
------------
Output: cell_dim_underfloor: Cell Dimensions that fit into the underfloor
        pack_dim_underfloor: Pack Dimensions that fit into the underfloor
        num_cell_underfloor: Number of cells that fit into the underfloor
------------
Implementation
[0] Import modules, classes and functions
[1] Calculate the geometrical filling of the underfloor
------------
"""

# region [0] Import modules, classes and functions
# import modules
import numpy as np
# import functions
# endregion


def calc_filling_underfloor(underbody_dim, cell_dim_underfloor, pack_dim_underfloor):

    # region [1] Calculate the geometrical filling of the underfloor
    # How many cells can fit into the underfloor (calculate considering the package factors)
    no_cells_underfloor = np.floor(underbody_dim/pack_dim_underfloor)

    # Identify the cell combinations, for which the number of cells in x, y or z direction is 0, and filter them out, as they do not need to be further simulated
    empty_underfloor_id = np.asarray(np.where(no_cells_underfloor[:, 0]*no_cells_underfloor[:, 1]*no_cells_underfloor[:, 2] == 0))

    if np.size(empty_underfloor_id) == np.shape(no_cells_underfloor)[0]:  # No cell fits in the underfloor

        no_cells_underfloor = np.zeros((np.shape(pack_dim_underfloor)[0], 3), dtype=np.intc)

    else:   # Some (or all) cells fit in the underfloor

        # Filter out the cells which do not fit in the underfloor. They will not be used to fill the tunnel or second level either!
        no_cells_underfloor = np.delete(no_cells_underfloor, empty_underfloor_id, 0)

        # Rewrite packdim and celldim keeping only the cells which fit in the underfloor
        pack_dim_underfloor = np.delete(pack_dim_underfloor, empty_underfloor_id, 0)
        cell_dim_underfloor = np.delete(cell_dim_underfloor, empty_underfloor_id, 0)
    # endregion

    return cell_dim_underfloor, pack_dim_underfloor, no_cells_underfloor
