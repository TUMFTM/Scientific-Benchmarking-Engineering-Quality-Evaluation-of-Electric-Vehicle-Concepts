"""
Description: This function fills the tunnel of lowfloor vehicles. This is necessary because for this type
             of vehicles a intermittent tunnel might be occur (as be seen in the Opel Mokka e).
             To fill the tunnel the predefined cell dimensions are put into both available areas

             More information can be found in Chapter 4.6 of (1) and Chapter 3.4.6 of (2)
------------
Sources: (1) Fundel, "Weiterentwicklung eines Simulationsmodells zur Optimierung & Bewertung von Fahrzeugkonzepten", Master Thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2023
         (2) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", P. D. Thesis, Technical University of Munich, Institute of Automotive Technology, 2022
         (3) P. Köhler, „Semi-physikalische Modellierung von Antriebsstrangkomponenten für Elektrofahrzeuge,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       tunnel_1_dim: Dimensions of the available space for the tunnel_1 segment
       tunnel_2_dim: Dimensions of the available space for the tunnel_2 segment
       cell_dim: Dimensions of the cells used in the underfloor of the vehicle
       pack_dim: Dimensions of the packs used in the underfloor of the vehicle
------------
Output: cell_dim_tunnel: Cell Dimensions that also fit in the tunnel
        pack_dim_tunnel: Pack Dimensions that also fit in the tunnel
        num_cell_tunnel_1: Number of cells that can be placed in the tunnel_1 segment
        num_cell_tunnel_2: Number of cells that can be placed in the tunnel_2 segment
------------

Implementation
[0] Import modules, classes and functions
[1] Calculate number of cells
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
import numpy as np
# endregion


def calc_filling_tunnel_lowfloor(vehicle, tunnel_1_dim, tunnel_2_dim, cell_dim, pack_dim):

    # region [1] Calculate number of cells
    if vehicle.settings.fill_tunnel == 0:  # option tunnel deactivated --> set number of cells to 0
        cell_dim_tunnel = np.zeros(np.shape(cell_dim))
        pack_dim_tunnel = np.zeros(np.shape(cell_dim))
        num_cell_tunnel_1 = np.zeros(np.shape(cell_dim))
        num_cell_tunnel_2 = np.zeros(np.shape(cell_dim))

    else:
        # There are no cells in the underfloor. This configuration is the lowfloor variant
        cell_dim_tunnel = cell_dim
        pack_dim_tunnel = pack_dim

        # How many cells can fit into the tunnel (calculate considering the package factors)
        num_cell_tunnel_1 = np.floor(tunnel_1_dim / pack_dim_tunnel)
        num_cell_tunnel_2 = np.floor(tunnel_2_dim / pack_dim_tunnel)
    # endregion

    return cell_dim_tunnel, pack_dim_tunnel, num_cell_tunnel_1, num_cell_tunnel_2
