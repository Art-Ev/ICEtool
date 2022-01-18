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
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProject
from qgis.core import QgsMessageLog
from qgis.utils import iface
from .ShadowGenerator.shadow_generator import ShadowGenerator
import processing
import os

class UMEP_shadows(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        project = QgsProject.instance()

    def processAlgorithm(self, parameters, context, model_feedback):

        FilePath = os.path.dirname(__file__)
        Output='UMEP shadows'
        ProjectPath=QgsProject.instance().absolutePath()
        
        sg = ShadowGenerator(iface)
        sg.run()
  
        return {'Output': Output}

    def name(self):
        return 'Compute shadows [UMEP]'

    def displayName(self):
        return 'Compute shadows [UMEP]'

    def group(self):
        return 'Step_3'

    def groupId(self):
        return 'Step_3'
        
    def shortHelpString(self):
        return """
        Compute shadows with UMEP
        """

    def createInstance(self):
        return UMEP_shadows()
