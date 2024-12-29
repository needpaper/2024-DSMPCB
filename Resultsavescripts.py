# -*- coding: utf-8 -*-

from abaqusConstants import *
from abaqus import session
from odbAccess import *
import os
import csv
import numpy as np

class BucklingAnalysis:
    def __init__(self, design_spaces, temperatures, angle_range, radius_range):
        """
        Initialize the BucklingAnalysis class instance.

        Parameters:
        - design_spaces: List of design spaces
        - temperatures: List of temperatures
        - angle_range: Tuple representing the angle range (start, end, step)
        - radius_range: Tuple representing the radius range (start, end, step)
        """
        self.design_spaces = design_spaces
        self.temperatures = temperatures
        self.angle_start, self.angle_end, self.angle_step = angle_range
        self.radius_start, self.radius_end, self.radius_step = radius_range

    def check_conditions(self, angle, radius, design_space):
        """
        Check if the given angle and radius meet the conditions.

        Parameters:
        - angle: Angle in degrees
        - radius: Radius
        - design_space: Design space

        Returns:
        - bool: Whether the conditions are met
        """
        angle_rad = angle * np.pi / 180.0
        safe_denominator = 1 - np.cos(angle_rad)
        r2 = np.where(safe_denominator != 0, radius * np.cos(angle_rad) / safe_denominator, 0)
        w2 = (design_space - angle * radius * np.pi / 90 - angle * r2 * np.pi / 90) / 2
        return r2 >= 2 and w2 >= 2

    def postprocessing(self, angle, radius):
        """
        Perform post-processing on the analysis results.

        Parameters:
        - angle: Angle in degrees
        - radius: Radius
        """
        r1 = radius
        a1 = angle

        current_directory = os.getcwd()
        odb_filename = "ctltNonLinear_radius{}_angle{}.odb".format(r1, a1)
        odb_path = os.path.join(current_directory, odb_filename)
        odb = session.openOdb(odb_path)

        session.viewports['Viewport: 1'].setValues(displayedObject=odb)
        odbName = session.viewports[session.currentViewportName].odbDisplay.name

        session.odbData[odbName].setValues(activeFrames=(('Step-NonLinearBuckle', (10000,)),))
        session.xyDataListFromField(odb=odb, outputPosition=NODAL, variable=(
        ('RM', NODAL, ((INVARIANT, 'Magnitude'),)), ('UR', NODAL, ((INVARIANT, 'Magnitude'),)),), nodeSets=("NODES",))

        def create_or_open_csv(csv_path):
            if not os.path.exists(csv_path):
                with open(csv_path, 'w') as file:
                    writer = csv.writer(file)
                    writer.writerow(['UR', 'RM'])
                print("CSV file created:", csv_path)

        def get_combined_data():
            xy1 = session.xyDataObjects['UR:Magnitude PI: ASSEMBLY N: 2']
            xy2 = session.xyDataObjects['RM:Magnitude PI: ASSEMBLY N: 2']
            xy3 = combine(xy1, xy2)
            data = xy3.data
            return data

        def save_data_to_csv(data, csv_path):
            with open(csv_path, 'wb') as file:
                writer = csv.writer(file)
                writer.writerows(data)
            print("Data appended to CSV file:", csv_path)

        data = get_combined_data()
        csv_path = 'radius{}_angle{}_UR_RM_data.csv'.format(r1, a1)
        create_or_open_csv(csv_path)
        save_data_to_csv(data, csv_path)
        del session.xyDataObjects['RM:Magnitude PI: ASSEMBLY N: 2']
        del session.xyDataObjects['UR:Magnitude PI: ASSEMBLY N: 2']

    def run(self):
        """
        Iterate through all combinations and perform finite element analysis.
        """
        for design_space in self.design_spaces:
            for temperature in self.temperatures:
                for angle in range(self.angle_start, self.angle_end + 1, self.angle_step):
                    for radius in range(self.radius_start, self.radius_end + 1, self.radius_step):
                        if self.check_conditions(angle, radius, design_space):
                            self.postprocessing(angle, radius)

if __name__ == "__main__":
    design_spaces = [80, 100, 120]
    temperatures = [25, 60, 100, 130]
    angle_range = (30, 90, 2)
    radius_range = (5, 30, 1)

    analysis = BucklingAnalysis(design_spaces, temperatures, angle_range, radius_range)
    analysis.run()

    print("All analyses are completed and results are saved.")
