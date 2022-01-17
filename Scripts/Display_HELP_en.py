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
import processing
import webbrowser
import os

class DisplayHELPen(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        project = QgsProject.instance()

    def processAlgorithm(self, parameters, context, model_feedback):

        FilePath = os.path.dirname(__file__)
        Output='Aide ouverte'
        project = QgsProject.instance()
        webbrowser.open_new(os.path.join(FilePath, "Docs","HOW_TO_english.pdf"))     
        return {'Output': Output}

    def name(self):
        return 'Open user manual'

    def displayName(self):
        return 'Open user manual'

    def group(self):
        return 'Help'

    def groupId(self):
        return '0help'
        
    def shortHelpString(self):
        return """
        Display english user manual
        """

    def createInstance(self):
        return DisplayHELPen()
