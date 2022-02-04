"""
 -----------------------------------------------------------------------------------------------------------
 Original Author:  Arthur Evrard
 Contributors:
 Last edited by: Arthur Evrard
 Repository:  https://github.com/Art-Ev/ICEtool
 Created:    2021-11-12 (Arthur Evrard)
 Updated:
    Remove updt height and radius as it's now integrated into the input process
 -----------------------------------------------------------------------------------------------------------
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterExtent
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterDefinition
from qgis.core import QgsProject
from qgis.core import Qgis
import processing
import os


class CreateRastersTreePoints(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('Buildings', 'Buildings', types=[QgsProcessing.TypeVectorPolygon], defaultValue='Buildings'))
        self.addParameter(QgsProcessingParameterField('Buildingsheight', 'Buildings_height[m]', type=QgsProcessingParameterField.Numeric, parentLayerParameterName='Buildings', allowMultiple=False, defaultValue='Height [m]'))
        self.addParameter(QgsProcessingParameterVectorLayer('Trees', 'Trees', types=[QgsProcessing.TypeVectorPoint], defaultValue='Trees'))
        self.addParameter(QgsProcessingParameterField('Treeheight', 'Tree_height [m]', type=QgsProcessingParameterField.Numeric, parentLayerParameterName='Trees', allowMultiple=False, defaultValue='Height [m]'))
        self.addParameter(QgsProcessingParameterField('Treeradius', 'Tree_radius [m]', type=QgsProcessingParameterField.Numeric, parentLayerParameterName='Trees', allowMultiple=False, defaultValue='Radius [m]'))
        self.addParameter(QgsProcessingParameterExtent('Analyseextent', 'Analyse extent', defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}
        ProjectPath=QgsProject.instance().absolutePath()

        # Building_raster
        alg_params = {
            'BURN': 0,
            'DATA_TYPE': 5,  # Float32
            'EXTENT': parameters['Analyseextent'],
            'EXTRA': '',
            'FIELD': parameters['Buildingsheight'],
            'HEIGHT': 0.5,
            'INIT': None,
            'INPUT': parameters['Buildings'],
            'INVERT': False,
            'NODATA': 0,
            'OPTIONS': '',
            'UNITS': 1,
            'USE_Z': False,
            'WIDTH': 0.5,
            'OUTPUT': os.path.join(ProjectPath,'Step_2','BuildingTerrain_raster.tif')
        }
        outputs['Building_raster'] = processing.run('gdal:rasterize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'END_CAP_STYLE': 0,  # Rond
            'FIELD': parameters['Treeradius'],
            'INPUT': parameters['Trees'],
            'JOIN_STYLE': 0,  # Rond
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('qgis:variabledistancebuffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Tree_raster
        alg_params = {
            'BURN': 0,
            'DATA_TYPE': 5,  # Float32
            'EXTENT': parameters['Analyseextent'],
            'EXTRA': '',
            'FIELD': parameters['Treeheight'],
            'HEIGHT': 0.5,
            'INIT': None,
            'INPUT': outputs['Buffer']['OUTPUT'],
            'INVERT': False,
            'NODATA': 0,
            'OPTIONS': '',
            'UNITS': 1,
            'USE_Z': False,
            'WIDTH': 0.5,
            'OUTPUT': os.path.join(ProjectPath,'Step_2','Tree_raster.tif')
        }
        outputs['Tree_raster'] = processing.run('gdal:rasterize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'Create rasters (tree points)'

    def displayName(self):
        return 'Create rasters (tree points)'

    def group(self):
        return 'Step_2'

    def groupId(self):
        return 'Step_2'

    def createInstance(self):
        return CreateRastersTreePoints()
