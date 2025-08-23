# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 13:19:04 2025

@author: Kaike Sa Teles Rocha Alves
@email_1: kaikerochaalves@outlook.com
@email_2: kaike.alves@estudante.ufjf.br

As a Data Science Manager at PGE-PR and a Ph.D. in Computational Modeling
at the Federal University of Juiz de Fora (UFJF), I specialize in artificial
intelligence, focusing on the study, development, and application of machine
learning models. My academic journey includes a scholarship that allowed me
to pursue a year of my Ph.D. at the University of Nottingham/UK, where I was
a member of the LUCID (Laboratory for Uncertainty in Data and Decision Making)
under the supervision of Professor Christian Wagner. My background in Industrial
Engineering provides me with a holistic view of organizational processes,
enabling me to propose efficient solutions and reduce waste.
"""

# Libraries
import os
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Wedge

class Ishikawa:
    """
    An Object-Oriented representation of an Ishikawa (Fishbone) Diagram generator.
    
    """
    def __init__(self, data: dict, target: str = "PROBLEM", figsize: tuple = (12, 7)):
        """
        Initializes the diagram object and sets up the matplotlib canvas.
        
        Parameters
        ----------
        data : dict
            A dictionary of problem categories and their associated causes.
        figsize : tuple, optional
            The size of the plot figure.
        """
        self.data = data
        self.target = target.replace(" ", "\n")
        self.fig, self.ax = plt.subplots(figsize=figsize, layout='constrained')
        
        # Set up the canvas exactly as in the original script
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-5, 5)
        self.ax.axis('off')

    def _draw_category(self, data: str, problem_x: float, problem_y: float, 
                       angle_x: float, angle_y: float):
        """
        Draws a single problem category arrow. 
        (Formerly the 'problems' function)
        """
        self.ax.annotate(str.upper(data), xy=(problem_x, problem_y),
                         xytext=(angle_x, angle_y),
                         fontsize=10,
                         color='white',
                         weight='bold',
                         xycoords='data',
                         verticalalignment='center',
                         horizontalalignment='center',
                         textcoords='offset fontsize',
                         arrowprops=dict(arrowstyle="->", facecolor='black'),
                         bbox=dict(boxstyle='square', facecolor='tab:blue', pad=0.8))

    def _draw_causes(self, data: list, cause_x: float, cause_y: float, 
                     cause_xytext=(-9, -0.3), top: bool = True):
        """
        Draws the causes for a single category.
        (Formerly the 'causes' function)
        """
        for index, cause in enumerate(data):
            # Coordinates are exactly as in the original function
            coords = [[0.02, 0], [0.23, 0.5], [-0.46, -1],
                      [0.69, 1.5], [-0.92, -2], [1.15, 2.5]]
            
            cause_x -= coords[index][0]
            cause_y += coords[index][1] if top else -coords[index][1]

            self.ax.annotate(cause, xy=(cause_x, cause_y),
                             horizontalalignment='center',
                             xytext=cause_xytext,
                             fontsize=9,
                             xycoords='data',
                             textcoords='offset fontsize',
                             arrowprops=dict(arrowstyle="->", facecolor='black'))

    def _draw_spine(self, xmin: int, xmax: int):
        """
        Draws the main spine, head, and tail.
        (Formerly the 'draw_spine' function)
        """
        self.ax.plot([xmin - 0.1, xmax], [0, 0], color='tab:blue', linewidth=2)
        self.ax.text(xmax + 0.1, -0.05, self.target, fontsize=10, 
                     weight='bold', color='white')
        semicircle = Wedge((xmax, 0), 1, 270, 90, fc='tab:blue')
        self.ax.add_patch(semicircle)
        
        tail_pos = [[xmin - 0.8, 0.8], [xmin - 0.8, -0.8], [xmin, -0.01]]
        triangle = Polygon(tail_pos, fc='tab:blue')
        self.ax.add_patch(triangle)

    def draw(self):
        """
        Orchestrates the drawing of the diagram using the original logic.
        (This method contains the exact logic from the 'draw_body' function)
        """
        # The entire logic below is copied directly from your 'draw_body' function
        length = (math.ceil(len(self.data) / 2)) - 1
        self._draw_spine(-2 - length, 2 + length)

        offset = 0
        prob_section = [1.55, 0.8]
        for index, problem in enumerate(self.data.values()):
            plot_above = index % 2 == 0
            cause_arrow_y = 1.7 if plot_above else -1.7
            y_prob_angle = 16 if plot_above else -16

            prob_arrow_x = prob_section[0] + length + offset
            cause_arrow_x = prob_section[1] + length + offset
            if not plot_above:
                offset -= 2.5
            if index > 5:
                raise ValueError(f'Maximum number of problems is 6, you have entered '
                                 f'{len(self.data)}')
            for k in self.data.keys():
                if len(self.data[k]) > 5:
                    raise ValueError('Maximum number of causes is 5 per category.')

            # Call the internal methods which were converted from your functions
            self._draw_category(list(self.data.keys())[index], prob_arrow_x, 0, -12, y_prob_angle)
            self._draw_causes(problem, cause_arrow_x, cause_arrow_y, top=plot_above)

    def plot_and_save(self, output_folder: str = 'Figures', filename: str = 'pareto_flight_analysis', extension: str = 'png', quality_dpi: int = 1200):
        """Displays and save the generated plot."""
        
        # Create the folder if it does not exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Define the full path for the output file
        file_path = os.path.join(output_folder, f'{filename}.{extension}')
        
        # Save the figure to the specified path with high resolution
        plt.savefig(file_path, dpi=quality_dpi, bbox_inches='tight')
        
        plt.show()
        