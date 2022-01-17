"""
 -----------------------------------------------------------------------------------------------------------
 Original Author:  Arthur Evrard
 Contributors:
 Last edited by: Arthur Evrard
 Repository:  https://github.com/Art-Ev/ICEtool
 Created:    2021-11-12 (Arthur Evrard)
 Updated:
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
        param = QgsProcessingParameterNumber('DefaultBheight', 'Default building height [m]', type=QgsProcessingParameterNumber.Double, minValue=1, maxValue=750, defaultValue=20)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        param = QgsProcessingParameterNumber('Defaulttreeheight', 'Default tree height [m]', type=QgsProcessingParameterNumber.Double, minValue=1, maxValue=200, defaultValue=4)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        param = QgsProcessingParameterNumber('Defaulttreeradius', 'Default tree radius [m]', type=QgsProcessingParameterNumber.Double, minValue=1, maxValue=50, defaultValue=2)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
        results = {}
        outputs = {}
        ProjectPath=QgsProject.instance().absolutePath()

        # Updt_bHeight
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': parameters['Buildingsheight'],
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Flottant
            'FORMULA': 'if("'+str(parameters['Buildingsheight'])+'">0,"'+str(parameters['Buildingsheight'])+'","'+str(parameters['DefaultBheight'])+'")',
            'INPUT': parameters['Buildings'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        if Qgis.QGIS_VERSION_INT>=31600:
            outputs['Updt_bheight'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        else:
            outputs['Updt_bheight'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Building_raster
        alg_params = {
            'BURN': 0,
            'DATA_TYPE': 5,  # Float32
            'EXTENT': parameters['Analyseextent'],
            'EXTRA': '',
            'FIELD': parameters['Buildingsheight'],
            'HEIGHT': 0.5,
            'INIT': None,
            'INPUT': outputs['Updt_bheight']['OUTPUT'],
            'INVERT': False,
            'NODATA': 0,
            'OPTIONS': '',
            'UNITS': 1,
            'USE_Z': False,
            'WIDTH': 0.5,
            'OUTPUT': os.path.join(ProjectPath,'Step_2','BuildingTerrain_raster.tif')
        }
        outputs['Building_raster'] = processing.run('gdal:rasterize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Updt_tHeight
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': parameters['Treeheight'],
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Flottant
            'FORMULA': 'if("'+str(parameters['Treeheight'])+'">0,"'+str(parameters['Treeheight'])+'","'+str(parameters['Defaulttreeheight'])+'")',
            'INPUT': parameters['Trees'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        if Qgis.QGIS_VERSION_INT>=31600:
            outputs['Updt_theight'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        else:
            outputs['Updt_theight'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Updt_tRadius
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': parameters['Treeradius'],
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Flottant
            'FORMULA': 'if("'+str(parameters['Treeradius'])+'">0,"'+str(parameters['Treeradius'])+'","'+str(parameters['Defaulttreeradius'])+'")',
            'INPUT': outputs['Updt_theight']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        if Qgis.QGIS_VERSION_INT>=31600:
            outputs['Updt_tradius'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        else:
            outputs['Updt_tradius'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'END_CAP_STYLE': 0,  # Rond
            'FIELD': parameters['Treeradius'],
            'INPUT': outputs['Updt_tradius']['OUTPUT'],
            'JOIN_STYLE': 0,  # Rond
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('qgis:variabledistancebuffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
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
