"""
Description: This function creates a spiderplot based on the given information from the benchmarking_vehicles file
------------
Sources: None
------------
Input: vehicle_name: Name of the vehicle (necessary for the legend and the path name)
       result: Array with stores the value for each spiderplot category
       variables: Name of each spiderplot category
       ranges: Rang of each spiderplot category (minimum and maximum value)
       num_rows: Number of rings inside the spiderplot
       custom_colors: Plot color
       legend: string inside the legend
       title: Title of the plot
       save_file: Check if plot shall be saved (.pgf/.svg/None)
       method: method of the plot (absolute or relative)
------------
Output: Spiderplot
------------
"""

# Implementation
# [0] Import all necessary modules, classes and methods
# [1] Set ploting information
# [2] Create Spiderplot
# [3] Save the plots
# endregion

# region [0] Import all necessary modules, classes and methods
# Import modules
import matplotlib.pyplot as plt
import matplotlib as mp_lib
import os
# Import classes
from .Radar_Chart_Class import ComplexRadar
# Import methods
# endregion


def create_spiderplot(vehicle_name, result, variables, ranges, num_rows, custom_colors, legend, title, save_file, method):
    # region [1] Set ploting information
    # Define necessary variables for saving as pgf
    if save_file == 'pgf':
        mp_lib.use("pgf")
        mp_lib.rcParams.update({
            'pgf.texsystem': 'pdflatex',
            'font.family': 'sans-serif',
            'font.sans-serif': 'Arial',
            'text.usetex': True,
            'pgf.rcfonts': False,
            'interactive': True,
            'pgf.preamble': '\n'.join([  # plots will use this preamble
                r'\usepackage[utf8]{inputenc}',
                r'\usepackage[T1]{fontenc}',
                r'\usepackage[detect-all,locale=UK]{siunitx}'])
        })
        mp_lib.rc('text', usetex=True)

    # Define format of the radarchart
    format_cfg = {
        'rad_ln_args': {'visible': True},
        'outer_ring': {'visible': True},
        'rgrid_tick_lbls_args': {'fontsize': 10},
        'theta_tick_lbls': {'fontsize': 10},
        'theta_tick_lbls_pad': 5,
        'incl_endpoint': True
    }
    # endregion

    # region [2] Create Spiderplot
    # Define figure
    fig1 = plt.figure(figsize=(7, 4), dpi=150)

    # Initialize spiderchart
    radar = ComplexRadar(fig1, variables, ranges, num_rows, show_scales=True, format_cfg=format_cfg)

    # Plot each of the spiderplot categories
    for g, c in zip(result.index, custom_colors):
        radar.plot(result.loc[g].values, label=f"cluster {g}", color=c)

    # Set title and legend
    radar.set_title(title)
    radar.use_legend(legend, loc=[0.97, 0.97], fontsize='8')
    # endregion

    # region [3] Save the plots
    path_project = os.getcwd()

    if save_file == 'pgf':
        # Save as .pgf file
        file_name = vehicle_name + method + ".pgf"
        path_pfg = os.path.join(path_project, "_05_Benchmarking", "Spiderplots_pgf", file_name)
        fig1.savefig(path_pfg, backend='pgf', bbox_inches='tight')
    elif save_file == 'svg':
        # Save as .svg file
        file_name = vehicle_name + method + ".svg"
        path_svg = os.path.join(path_project, "_05_Benchmarking", "Spiderplots_svg", file_name)
        fig1.savefig(path_svg, dpi='figure')
    else:
        # Do not save the plot
        plt.show(block=False)
        plt.pause(3)
        plt.close('all')

    # Close all open figures
    plt.close('all')
    # endregion
