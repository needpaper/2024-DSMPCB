# -*- coding: utf-8 -*-
# Writen by Wang Haobo .  HIT .Harbin .China
#
# BucklingAnalysis class structure
# ├── __init__(self, design_spaces, temperatures, angle_range, radius_range)
# │   └── Initialize class member variables and ensure the working directory is 'CTLT_NonLinearBuckling'
# ├── check_conditions(self, angle, radius, design_space)
# │   └── Check if the given angle and radius meet the conditions
# ├── get_modulus_based_on_temperature(self, temperature)
# │   └── Return the corresponding elastic modulus based on the temperature
# ├── finite_element_analysis(self, angle, radius, design_space, temperature)
# │   └── Perform finite element analysis, including geometry creation, material definition, mesh generation, step setup, etc.
# ├── finite_element_check(self, angle, radius, design_space, temperature)
# │   └── Check if the analysis is complete, and if not, perform the analysis
# ├── count_cases(self)
# │   └── Calculate the total number of valid cases
# └── run(self)
#     └── Iterate through all combinations and perform finite element analysis
#
#
#
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
import os
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

        # Ensure working directory is 'CTLT_NonLinearBuckling'
        current_directory = os.getcwd()
        if os.path.basename(current_directory) != 'CTLT_NonLinearBuckling':
            folder_name = 'CTLT_NonLinearBuckling'
            if not os.path.exists(folder_name):
                os.mkdir(folder_name)
            os.chdir(folder_name)

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

    def get_modulus_based_on_temperature(self, temperature):
        """
        Return the corresponding elastic modulus based on the temperature.

        Parameters:
        - temperature: Temperature

        Returns:
        - list: Corresponding elastic modulus list
        """
        modulus_25 = [120000.0, 8800.0, 0.31, 8200.0, 8200.0, 7200.0]
        modulus_60 = [72000.0, 5300.0, 0.36, 5100.0, 5100.0, 4800.0]
        modulus_100 = [36000.0, 3000.0, 0.42, 2700.0, 2700.0, 2600.0]
        modulus_130 = [16300.0, 1620.0, 0.45, 1500.0, 1500.0, 1200.0]

        if temperature == 25:
            return modulus_25
        elif temperature == 60:
            return modulus_60
        elif temperature == 100:
            return modulus_100
        elif temperature == 130:
            return modulus_130
        else:
            raise ValueError("Unsupported temperature value: {}".format(temperature))

    def finite_element_analysis(self, angle, radius, design_space, temperature):
        """
        Perform finite element analysis.
        Parameters:
        - angle: Angle in degrees
        - radius: Radius
        - design_space: Design space
        - temperature: Temperature
        """
        Mdb()
        length = 1000.0
        composite_thickness = 0.15
        Design_space = design_space

        l1 = length
        a1 = angle
        r1 = radius
        r11 = r1 * np.cos(angle * np.pi / 180.0) / (1 - np.cos(angle * np.pi / 180.0))
        t1 = composite_thickness
        w1 = (Design_space - angle * r1 * np.pi / 90 - angle * r11 * np.pi / 90) / 2

        # Part
        mdb.models.changeKey(fromName='Model-1', toName='Model-LinearBuckling')
        mdb.models['Model-LinearBuckling'].ConstrainedSketch(name='profile', sheetSize=400.0)
        mdb.models['Model-LinearBuckling'].sketches['profile'].ArcByCenterEnds(
            center=(0.0, 0.0),
            direction=CLOCKWISE,
            point1=(-r1 * np.sin(a1 * np.pi / 180.0), r1 * np.cos(a1 * np.pi / 180.0)),
            point2=(r1 * np.sin(a1 * np.pi / 180.0), r1 * np.cos(a1 * np.pi / 180.0)))
        mdb.models['Model-LinearBuckling'].sketches['profile'].ArcByCenterEnds(
            center=(r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0), r11),
            direction=COUNTERCLOCKWISE,
            point1=(r1 * np.sin(a1 * np.pi / 180.0), r1 * np.cos(a1 * np.pi / 180.0)),
            point2=(r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0), 0.0))
        mdb.models['Model-LinearBuckling'].sketches['profile'].ArcByCenterEnds(
            center=(-r1 * np.sin(a1 * np.pi / 180.0) - r11 * np.sin(a1 * np.pi / 180.0), r11),
            direction=CLOCKWISE,
            point1=(-r1 * np.sin(a1 * np.pi / 180.0), r1 * np.cos(a1 * np.pi / 180.0)),
            point2=(-r1 * np.sin(a1 * np.pi / 180.0) - r11 * np.sin(a1 * np.pi / 180.0), 0.0))
        mdb.models['Model-LinearBuckling'].sketches['profile'].Line(
            point1=(r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0), 0.0),
            point2=(r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0) + w1, 0.0))
        mdb.models['Model-LinearBuckling'].sketches['profile'].Line(
            point1=(-r1 * np.sin(a1 * np.pi / 180.0) - r11 * np.sin(a1 * np.pi / 180.0), 0.0),
            point2=(-r1 * np.sin(a1 * np.pi / 180.0) - r11 * np.sin(a1 * np.pi / 180.0) - w1, 0.0))
        mdb.models['Model-LinearBuckling'].sketches['profile'].ArcByCenterEnds(
            center=(0.0, 0.0),
            direction=CLOCKWISE,
            point1=(r1 * np.sin(a1 * np.pi / 180.0), -r1 * np.cos(a1 * np.pi / 180.0)),
            point2=(-r1 * np.sin(a1 * np.pi / 180.0), -r1 * np.cos(a1 * np.pi / 180.0)))
        mdb.models['Model-LinearBuckling'].sketches['profile'].ArcByCenterEnds(
            center=(r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0), -r11),
            direction=CLOCKWISE,
            point1=(r1 * np.sin(a1 * np.pi / 180.0), -r1 * np.cos(a1 * np.pi / 180.0)),
            point2=(r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0), 0.0))
        mdb.models['Model-LinearBuckling'].sketches['profile'].ArcByCenterEnds(
            center=(-r1 * np.sin(a1 * np.pi / 180.0) - r11 * np.sin(a1 * np.pi / 180.0), -r11),
            direction=COUNTERCLOCKWISE,
            point1=(-r1 * np.sin(a1 * np.pi / 180.0), -r1 * np.cos(a1 * np.pi / 180.0)),
            point2=(-r1 * np.sin(a1 * np.pi / 180.0) - r11 * np.sin(a1 * np.pi / 180.0), 0.0))
        mdb.models['Model-LinearBuckling'].Part(dimensionality=THREE_D, name='ctlt', type=DEFORMABLE_BODY)
        mdb.models['Model-LinearBuckling'].parts['ctlt'].BaseShellExtrude(depth=l1, sketch=mdb.models['Model-LinearBuckling'].sketches['profile'])
        del mdb.models['Model-LinearBuckling'].sketches['profile']

        # Material and Section
        elastic_moduli = self.get_modulus_based_on_temperature(temperature)

        ##set ctlt_single and ctlt_double
        mdb.models['Model-LinearBuckling'].parts['ctlt'].Set(
            faces=mdb.models['Model-LinearBuckling'].parts['ctlt'].faces.findAt((
                (r1 * sin(a1 * pi / 180.0) + r11 * sin(a1 * pi / 180.0) - r11 * sin(a1 * pi / 360.0),
                 r11 - r11 * cos(a1 * pi / 360.0),
                 l1 / 2),), ((0.0, r1, l1 / 2),),
                ((-(r1 * sin(a1 * pi / 180.0) + r11 * sin(a1 * pi / 180.0) - r11 * sin(a1 * pi / 360.0)),
                  r11 - r11 * cos(a1 * pi / 360.0), l1 / 2),),
                ((r1 * sin(a1 * pi / 180.0) + r11 * sin(a1 * pi / 180.0) - r11 * sin(a1 * pi / 360.0),
                  -(r11 - r11 * cos(a1 * pi / 360.0)), l1 / 2),), ((0.0, -r1, l1 / 2),), (
                    (-(r1 * sin(a1 * pi / 180.0) + r11 * sin(a1 * pi / 180.0) - r11 * sin(a1 * pi / 360.0)),
                     -(r11 - r11 * cos(a1 * pi / 360.0)),
                     l1 / 2),), ), name='ctlt_single')

        mdb.models['Model-LinearBuckling'].parts['ctlt'].Set(faces=
                                                             mdb.models['Model-LinearBuckling'].parts[
                                                                 'ctlt'].faces.findAt(((r1 * sin(
                                                                 a1 * pi / 180.0) + r11 * sin(a1 * pi / 180.0) + w1,
                                                                                        0.0, 0.0),), ((r1 * sin(
                                                                 a1 * pi / 180.0) + r11 * sin(a1 * pi / 180.0) + w1,
                                                                                                       0.0, l1),), ),
                                                             name='ctlt_doub1')
        mdb.models['Model-LinearBuckling'].parts['ctlt'].Set(faces=
                                                             mdb.models['Model-LinearBuckling'].parts[
                                                                 'ctlt'].faces.findAt(((-r1 * sin(
                                                                 a1 * pi / 180.0) - r11 * sin(a1 * pi / 180.0) - w1,
                                                                                        0.0, 0.0),), ((-r1 * sin(
                                                                 a1 * pi / 180.0) - r11 * sin(a1 * pi / 180.0) - w1,
                                                                                                       0.0, l1),), ),
                                                             name='ctlt_doub2')

        mdb.models['Model-LinearBuckling'].Material(name='Composite')
        mdb.models['Model-LinearBuckling'].materials['Composite'].Elastic(
            table=(tuple(elastic_moduli),),
            type=LAMINA
        )
        mdb.models['Model-LinearBuckling'].materials['Composite'].Density(table=((1.6e-09,),))

        mdb.models['Model-LinearBuckling'].CompositeShellSection(idealization=NO_IDEALIZATION,
                                                                 integrationRule=SIMPSON,
                                                                 layup=(SectionLayer(thickness=t1 / 6, orientAngle=45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=-45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=-45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=45.0, material='Composite')),
                                                                 name='Section-6ply',
                                                                 poissonDefinition=DEFAULT, preIntegrate=OFF,
                                                                 symmetric=False, temperature=GRADIENT,
                                                                 thicknessModulus=None, thicknessType=UNIFORM,
                                                                 useDensity=OFF)

        mdb.models['Model-LinearBuckling'].parts['ctlt'].SectionAssignment(
            offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE,
            region=mdb.models['Model-LinearBuckling'].parts['ctlt'].sets['ctlt_single'],
            sectionName='Section-6ply', thicknessAssignment=FROM_SECTION)

        mdb.models['Model-LinearBuckling'].CompositeShellSection(idealization=NO_IDEALIZATION,
                                                                 integrationRule=SIMPSON,
                                                                 layup=(SectionLayer(thickness=t1 / 6, orientAngle=45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=-45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=-45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=-45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=-45.0, material='Composite'),
                                                                        SectionLayer(thickness=t1 / 6, orientAngle=45.0, material='Composite')),
                                                                 name='Section-12ply',
                                                                 poissonDefinition=DEFAULT, preIntegrate=OFF,
                                                                 symmetric=True, temperature=GRADIENT,
                                                                 thicknessModulus=None, thicknessType=UNIFORM,
                                                                 useDensity=OFF)

        mdb.models['Model-LinearBuckling'].parts['ctlt'].SectionAssignment(
            offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE,
            region=mdb.models['Model-LinearBuckling'].parts['ctlt'].sets['ctlt_doub1'],
            sectionName='Section-12ply', thicknessAssignment=FROM_SECTION)
        mdb.models['Model-LinearBuckling'].parts['ctlt'].SectionAssignment(
            offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE,
            region=mdb.models['Model-LinearBuckling'].parts['ctlt'].sets['ctlt_doub2'],
            sectionName='Section-12ply', thicknessAssignment=FROM_SECTION)

        mdb.models['Model-LinearBuckling'].parts['ctlt'].MaterialOrientation(additionalRotationType=ROTATION_NONE, axis=AXIS_2, fieldName='',
                                                                             localCsys=None, orientationType=GLOBAL, region=mdb.models['Model-LinearBuckling'].parts['ctlt'].sets['ctlt_single'])
        mdb.models['Model-LinearBuckling'].parts['ctlt'].MaterialOrientation(additionalRotationType=ROTATION_NONE, axis=AXIS_2, fieldName='',
                                                                             localCsys=None, orientationType=GLOBAL, region=mdb.models['Model-LinearBuckling'].parts['ctlt'].sets['ctlt_doub1'])
        mdb.models['Model-LinearBuckling'].parts['ctlt'].MaterialOrientation(additionalRotationType=ROTATION_NONE, axis=AXIS_2, fieldName='',
                                                                             localCsys=None, orientationType=GLOBAL, region=mdb.models['Model-LinearBuckling'].parts['ctlt'].sets['ctlt_doub2'])

        # Assembly
        mdb.models['Model-LinearBuckling'].rootAssembly.DatumCsysByDefault(CARTESIAN)
        mdb.models['Model-LinearBuckling'].rootAssembly.Instance(dependent=ON, name='ctlt-1', part=mdb.models['Model-LinearBuckling'].parts['ctlt'])

        # Create reference points
        mdb.models['Model-LinearBuckling'].rootAssembly.ReferencePoint(point=(0.0, 0.0, 0.0))
        mdb.models['Model-LinearBuckling'].rootAssembly.ReferencePoint(point=(0.0, 0.0, l1))

        # Create section
        mdb.models['Model-LinearBuckling'].rootAssembly.Set(edges=mdb.models['Model-LinearBuckling'].rootAssembly.instances['ctlt-1'].edges.findAt(
            ((-(r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0) + w1 / 2), 0.0, 0.0),),
            ((-(r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0) - r11 * np.sin(a1 * np.pi / 360.0)), r11 - r11 * np.cos(a1 * np.pi / 360.0), 0.0),),
            ((0.0, r1, 0.0),),
            ((r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0) - r11 * np.sin(a1 * np.pi / 360.0), r11 - r11 * np.cos(a1 * np.pi / 360.0), 0.0),),
            ((r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0) + w1 / 2, 0.0, 0.0),),
            ((-(r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0) - r11 * np.sin(a1 * np.pi / 360.0)), -(r11 - r11 * np.cos(a1 * np.pi / 360.0)), 0.0),),
            ((0.0, -r1, 0.0),), ((r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0) - r11 * np.sin(a1 * np.pi / 360.0), -(r11 - r11 * np.cos(a1 * np.pi / 360.0)), 0.0),)), name='ctlt_section1')
        mdb.models['Model-LinearBuckling'].rootAssembly.Set(edges=mdb.models['Model-LinearBuckling'].rootAssembly.instances['ctlt-1'].edges.findAt(
            ((-(r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0) + w1 / 2), 0.0, l1),),
            ((-(r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0) - r11 * np.sin(a1 * np.pi / 360.0)), r11 - r11 * np.cos(a1 * np.pi / 360.0), l1),),
            ((0.0, r1, l1),),
            ((r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0) - r11 * np.sin(a1 * np.pi / 360.0), r11 - r11 * np.cos(a1 * np.pi / 360.0), l1),),
            ((r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0) + w1 / 2, 0.0, l1),),
            ((-(r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0) - r11 * np.sin(a1 * np.pi / 360.0)), -(r11 - r11 * np.cos(a1 * np.pi / 360.0)), l1),),
            ((0.0, -r1, l1),), ((r1 * np.sin(a1 * np.pi / 180.0) + r11 * np.sin(a1 * np.pi / 180.0) - r11 * np.sin(a1 * np.pi / 360.0), -(r11 - r11 * np.cos(a1 * np.pi / 360.0)), l1),)), name='ctlt_section2')

        # Mesh
        mdb.models['Model-LinearBuckling'].parts['ctlt'].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=4.0)
        mdb.models['Model-LinearBuckling'].parts['ctlt'].generateMesh()
        mdb.models['Model-LinearBuckling'].parts['ctlt'].setElementType(elemTypes=(ElemType(elemCode=S4R, elemLibrary=EXPLICIT, secondOrderAccuracy=OFF, hourglassControl=STIFFNESS), ElemType(elemCode=S3R, elemLibrary=EXPLICIT)), regions=(mdb.models['Model-LinearBuckling'].parts['ctlt'].faces,))

        # Set node
        mdb.models['Model-LinearBuckling'].rootAssembly.Set(referencePoints=(mdb.models['Model-LinearBuckling'].rootAssembly.referencePoints[5],), name='Nodes')

        # Step
        mdb.models['Model-LinearBuckling'].BuckleStep(name='Step-LinearBuckle', previous='Initial', numEigen=20, eigensolver=LANCZOS, minEigen=0.0, blockSize=DEFAULT, maxBlocks=DEFAULT)
        mdb.models['Model-LinearBuckling'].fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'U', 'RM'))

        # Interaction
        mdb.models['Model-LinearBuckling'].Coupling(name='RP-1_with_ctltsection1', controlPoint=Region(referencePoints=(mdb.models['Model-LinearBuckling'].rootAssembly.referencePoints[4],)), surface=mdb.models['Model-LinearBuckling'].rootAssembly.sets['ctlt_section1'], influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)
        mdb.models['Model-LinearBuckling'].Coupling(name='RP-2_with_ctltsection2', controlPoint=Region(referencePoints=(mdb.models['Model-LinearBuckling'].rootAssembly.referencePoints[5],)), surface=mdb.models['Model-LinearBuckling'].rootAssembly.sets['ctlt_section2'], influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)

        # Load
        mdb.models['Model-LinearBuckling'].DisplacementBC(name='BC-1', createStepName='Initial', region=Region(referencePoints=(mdb.models['Model-LinearBuckling'].rootAssembly.referencePoints[4],)), u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
        mdb.models['Model-LinearBuckling'].DisplacementBC(name='BC-2', createStepName='Step-LinearBuckle', region=Region(referencePoints=(mdb.models['Model-LinearBuckling'].rootAssembly.referencePoints[5],)), u1=UNSET, u2=SET, u3=-1.0, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

        # Add keywords
        mdb.models['Model-LinearBuckling'].keywordBlock.synchVersions(storeNodesAndElements=False)
        mdb.models['Model-LinearBuckling'].keywordBlock.insert(64, "*node file\nu")

        # Job
        jobName_Linear = 'ctltLinear_radius{}_angle{}_design{}_temp{}'.format(r1, a1, Design_space, temperature)
        mdb.Job(model='Model-LinearBuckling', name=jobName_Linear, numCpus=8, numDomains=8)
        mdb.saveAs(pathName=jobName_Linear)
        mdb.jobs[jobName_Linear].submit()
        mdb.jobs[jobName_Linear].waitForCompletion()

        # Copy model
        mdb.Model(name='Model-NonLinearBuckling', objectToCopy=mdb.models['Model-LinearBuckling'])
        del mdb.models['Model-NonLinearBuckling'].steps['Step-LinearBuckle']

        # NonLinearStep
        mdb.models['Model-NonLinearBuckling'].StaticRiksStep(name='Step-NonLinearBuckle', previous='Initial', initialArcInc=0.01, minArcInc=1e-08, maxArcInc=0.05, nlgeom=ON)
        mdb.models['Model-NonLinearBuckling'].fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'U', 'RM'))
        mdb.models['Model-NonLinearBuckling'].FieldOutputRequest(name='F-Output-2', createStepName='Step-NonLinearBuckle', variables=('S', 'U', 'UR', 'RM'), region=mdb.models['Model-NonLinearBuckling'].rootAssembly.sets['Nodes'], sectionPoints=DEFAULT, rebar=EXCLUDE)
        mdb.models['Model-NonLinearBuckling'].HistoryOutputRequest(name='H-Output-2', createStepName='Step-NonLinearBuckle', variables=('UR', 'RM'), region=mdb.models['Model-NonLinearBuckling'].rootAssembly.sets['Nodes'], sectionPoints=DEFAULT, rebar=EXCLUDE)

        # NonLinearLoad
        mdb.models['Model-NonLinearBuckling'].DisplacementBC(name='BC-1', createStepName='Initial', region=Region(referencePoints=(mdb.models['Model-NonLinearBuckling'].rootAssembly.referencePoints[4],)), u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
        mdb.models['Model-NonLinearBuckling'].DisplacementBC(name='BC-2', createStepName='Step-NonLinearBuckle', region=Region(referencePoints=(mdb.models['Model-NonLinearBuckling'].rootAssembly.referencePoints[5],)), u1=0.0, u2=UNSET, u3=UNSET, ur1=-1.0, ur2=0.0, ur3=0.0, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

        # Add keywords
        mdb.models['Model-NonLinearBuckling'].keywordBlock.setValues(edited=0)
        mdb.models['Model-NonLinearBuckling'].keywordBlock.synchVersions(storeNodesAndElements=False)
        new_line = "*imperfection,file=ctltLinear_radius{}_angle{}_design{}_temp{},Step=1\n1,0.4e-3\n".format(r1, a1, Design_space, temperature)
        mdb.models['Model-NonLinearBuckling'].keywordBlock.insert(54, new_line)

        # Job
        jobName_NonLinear = 'ctltNonLinear_radius{}_angle{}_design{}_temp{}'.format(radius, angle, design_space, temperature)
        mdb.Job(model='Model-NonLinearBuckling', name=jobName_NonLinear, numCpus=8, numDomains=8)
        mdb.saveAs(pathName=jobName_NonLinear)
        mdb.jobs[jobName_NonLinear].submit()
        mdb.jobs[jobName_NonLinear].waitForCompletion()
        mdb.save()

    def finite_element_check(self, angle, radius, design_space, temperature):
        """
        Check if the analysis is complete, and if not, perform the analysis.

        Parameters:
        - angle: Angle in degrees
        - radius: Radius
        - design_space: Design space
        - temperature: Temperature
        """
        jobName = 'ctltNonLinear_radius{}_angle{}_design{}_temp{}'.format(radius, angle, design_space, temperature)
        if os.path.exists("{}.odb".format(jobName)):
            print("Skipping completed analysis for angle {} and radius {} with design space {} and temperature {}".format(angle, radius, design_space, temperature))
            return
        else:
            self.finite_element_analysis(angle, radius, design_space, temperature)

    def count_cases(self):
        """
        Calculate the total number of valid cases.

        Returns:
        - int: Total number of valid cases
        """
        total_cases = 0
        for design_space in self.design_spaces:
            for temperature in self.temperatures:
                for angle in range(self.angle_start, self.angle_end + 1, self.angle_step):
                    for radius in range(self.radius_start, self.radius_end + 1, self.radius_step):
                        if self.check_conditions(angle, radius, design_space):
                            total_cases += 1
        return total_cases

    def run(self):
        """
        Iterate through all combinations and perform finite element analysis.
        """
        for design_space in self.design_spaces:
            for temperature in self.temperatures:
                for angle in range(self.angle_start, self.angle_end + 1, self.angle_step):
                    for radius in range(self.radius_start, self.radius_end + 1, self.radius_step):
                        if self.check_conditions(angle, radius, design_space):
                            self.finite_element_check(angle, radius, design_space, temperature)

if __name__ == "__main__":
    design_spaces = [80, 100, 120]
    temperatures = [25, 60, 100, 130]
    angle_range = (30, 90, 2)
    radius_range = (5, 30, 1)

    analysis = BucklingAnalysis(design_spaces, temperatures, angle_range, radius_range)
    total_cases = analysis.count_cases()

    print("Total number of valid cases:", total_cases)
    analysis.run()

    print("All analyses are completed and results are saved.")
