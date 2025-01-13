"""
Description: This function calculates the mass of the traction battery
             ALL THE GIVEN MASSES ARE CALCULATED IN KG

             All the models were first created in the work of Romano (2),
             and then further detailed in another publication (3) and in
             the Ph.D. thesis (1). A complete overview of the models is available at the
             Appendix E and at the chapter 3.5 of the Ph. D thesis (1)
------------
Sources: (1) Lorenzo Nicoletti, "Parametric Modeling of Battery Electric Vehicles in the Early Development Phase", Technical University of Munich, Institute of Automotive Technology, 2022
         (2) A. Romano, „Data-based Analysis for Parametric Weight Estimation of new BEV Concepts,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021.
         (3) L. Nicoletti, A. Romano, A. König, P. Köhler, M. Heinrich and M. Lienkamp, „An Estimation of the Lightweight Potential of Battery Electric Vehicles,“ Energies, vol. 14, no. 15, p. 4655, 2021, DOI: 10.3390/en14154655.
         (4) P. Köhler, „Semi-physikalische Modellierung von Antriebsstrangkomponenten für Elektrofahrzeuge,“Master thesis, Institute of Automotive Technology, Technical University of Munich, Munich, 2021
------------
Input: vehicle: Class element, where all elements from the Excel-Table are stored
       Parameters: Stores the constant values and regressions for volume and mass models
------------
Output: The vehicle structure updated with the mass of the battery
------------

Implementation
[0] Import modules, classes and functions
[1] Initialize the required variables
[2] Calculate the volumetric energy density of the battery
[3] Calculate the mass of the battery
[4] Assign the outputs
------------
"""

# region [0] Import modules, classes and functions
# Import functions
# Import modules
import numpy as np
import math
# endregion


def calc_battery_weight(vehicle, parameters):
    # region [1] Initialize the required variables
    energy_density_gravimetric = vehicle.battery.cell.energy_density_grav   # in Wh/kg
    battery_energy = vehicle.battery.energy_is_gross_in_kWh * 1000          # in Wh
    cell_type = vehicle.battery.cell.cell_type                              # prismatic, pouch or cylindrical

    # Regression between battery housing (including tunnel and second level -if present- but no sills) (4, p. 78)
    regr_battery_structure_coeff = parameters.regr.mass.battery_structural.coefficients

    # Values for the Z dimensional chain (the battery cooling is already included in CZ underfloor) (4, p. 73)
    CZ_bottom_cover = vehicle.dimensions.CZ.batt_bottom_cover                           # in mm
    CZ_top_cover = parameters.dimensions.CZ.batt_top_cover                              # in mm (4, p.76)
    EZ_free_space_mod2cover = parameters.dimensions.EZ.free_space_module_to_top_cover   # in mm (4, p. 76)

    # Installation space underfloor and tunnel
    space_table = vehicle.battery.spacetable
    installationspace_underfloor = space_table['underfloor'].to_numpy()[0:3]        # in mm
    installationspace_tunnel_1 = space_table['tunnel_1'].to_numpy()[0:3]            # in mm
    installationspace_tunnel_2 = space_table['tunnel_2'].to_numpy()[0:3]            # in mm
    installationspace_sec_lev = space_table['second_level'].to_numpy()[0:3]         # in mm
    installationspace_front_seat = space_table['front_seat'].to_numpy()[0:3]        # in mm

    # Settings (filled battery areas and driven axles)
    fill_sec_lev = vehicle.settings.fill_second_level
    fill_front_seat = vehicle.settings.fill_frontseat_area
    filled_axles = vehicle.topology.filled_axles

    # Installation space small overlap (all in mm)
    CX_small_overlap = vehicle.battery.installationspace.CX_batt_small_overlap
    CY_small_overlap = vehicle.battery.installationspace.CY_batt_small_overlap

    # Masses of the battery electrics components (cables, relais, BMS) (4, p. 78)
    mass_elec_AWD = parameters.masses.battery_electrics.AWD         # Masses of battery if the vehicle is AWD in kg
    mass_elec_noAWD = parameters.masses.battery_electrics.noAWD     # Masses if the vehicle is not AWD in kg

    # Mass ratio from cell to module -> f_mod= (mass_cell+mass_module)/mass_cell
    # Considers the added mass of the module housing and module cables (4, p. 77)
    f_mod_pouch = parameters.battery.massfactor_cell_to_module.pouch
    f_mod_pris = parameters.battery.massfactor_cell_to_module.prismatic
    f_mod_cyl = parameters.battery.massfactor_cell_to_module.cylindrical

    # Conversion factor from gross to net battery energy
    gross2net = parameters.battery.net_to_gross_capacity_factor
    # endregion

    # region [2] Calculate the volumetric energy density of the battery
    # 2a) Consider also the volume of the battery cover and the cooling for the battery volume
    installationspace_underfloor[2] = installationspace_underfloor[2] + CZ_top_cover + CZ_bottom_cover + \
                                      EZ_free_space_mod2cover

    # Volume of the battery housing in liters
    volume_battery_underfloor = np.prod(installationspace_underfloor)/math.pow(10, 6)

    # 2b) Volume of the tunnel in liters
    volume_tunnel = np.prod(installationspace_tunnel_1)/math.pow(10, 6) + np.prod(installationspace_tunnel_2)/math.pow(10, 6)

    # 2c) Volume of the small overlap area
    if np.size(CX_small_overlap) > 1:           # The smalloverlap space is defined
        # Basis area of the small overlap section (simplified as rectangular shape section)
        basis_area_small_overlap = max(CX_small_overlap) * (max(CY_small_overlap) + min(CY_small_overlap)) * 0.5
    else:
        basis_area_small_overlap = CX_small_overlap * CY_small_overlap
    # Volume of the small overlap area, also here correct the total height
    volume_small_overlap = basis_area_small_overlap * installationspace_underfloor[2] / math.pow(10, 6)

    # 2d) Volume of the second level
    if fill_sec_lev:
        installationspace_sec_lev[2] = installationspace_sec_lev[2] + CZ_bottom_cover + EZ_free_space_mod2cover

        # Volume of the second level in liters
        volume_battery_sec_lev = np.prod(installationspace_sec_lev)/math.pow(10, 6)
    else:
        volume_battery_sec_lev = 0

    # 2e) Volume of the area under the front seat
    if fill_front_seat:
        installationspace_front_seat[2] = installationspace_front_seat[2] + CZ_bottom_cover + EZ_free_space_mod2cover

        # Volume of the front seat area in liters
        volume_battery_front_seat = np.prod(installationspace_front_seat)/math.pow(10, 6)
    else:
        volume_battery_front_seat = 0

    # 2f) Total volume of the battery and volumetric energy density
    volume_battery_total = volume_tunnel + volume_small_overlap + volume_battery_underfloor + \
                           volume_battery_sec_lev + volume_battery_front_seat

    # Volumetric energy density on the battery level
    volumetric_energy_density = battery_energy/volume_battery_total
    # endregion

    # region [3] Calculate the mass of the battery
    # Mass split into three shares: cells, electrical, and structural components with cooling

    # 3a) Mass of the cells and modules:
    # Total mass of cells in kg, calculated with the volumetric energy density (4, p. 77)
    mass_cells = battery_energy/energy_density_gravimetric

    # Mass of cell modules in kg, depending on the cell type the modules
    # have a different weight (4, p. 77)
    match cell_type:
        case 'pouch':
            mass_modules = f_mod_pouch * mass_cells
        case 'prismatic':
            mass_modules = f_mod_pris * mass_cells
        case 'cylindrical':
            mass_modules = f_mod_cyl * mass_cells
        case _:
            raise Exception("The cell type is invalid. Only prismatic, cylindrical and pouch cells are possible")

    # 3b) Mass electrical components (cables and so on) (4, p. 78)
    if filled_axles['front'] and filled_axles['rear']:      # AWD
        mass_elec = mass_elec_AWD
    else:                                                   # RWD or FWD
        mass_elec = mass_elec_noAWD

    # 3c) Mass of structural AND cooling components in kg (4, p. 78)
    mass_structural = regr_battery_structure_coeff[0] + regr_battery_structure_coeff[1] * volume_battery_total

    # 3d) Total gravimetric energy density at pack level
    gravimetric_energy_density = battery_energy/(mass_structural + mass_modules + mass_elec)
    # endregion

    # region [4] Assign the outputs
    # All outputs are expressed in kg
    setattr(vehicle.masses.powertrain, 'battery_structural_components', mass_structural)
    setattr(vehicle.masses.powertrain, 'battery_cells', mass_modules)
    setattr(vehicle.masses.powertrain, 'battery_electrical', mass_elec)
    setattr(vehicle.battery, 'volumetric_energy_density_gross', volumetric_energy_density)
    setattr(vehicle.battery, 'gravimetric_energy_density_gross', gravimetric_energy_density)
    setattr(vehicle.battery, 'volumetric_energy_density_net', volumetric_energy_density * gross2net)
    setattr(vehicle.battery, 'gravimetric_energy_density_net', gravimetric_energy_density * gross2net)

    setattr(vehicle.battery, 'volume_battery_total', volume_battery_total)
    # endregion

    return vehicle, parameters
