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
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProject
from qgis.core import QgsMessageLog
from qgis.utils import iface
import processing
import shutil
import time
import os

class SeeEXAMPLE(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        project = QgsProject.instance()
        self.addParameter(QgsProcessingParameterFile('destinationfolder', 'Destination Folder', behavior=QgsProcessingParameterFile.Folder, fileFilter='Tous les fichiers (*.*)', defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):

        FilePath = os.path.dirname(__file__)
        Output='Finished'
        project = QgsProject.instance()
        shutil.copytree(os.path.join(FilePath, "Example"),os.path.join(parameters['destinationfolder'],'ICEtool_example'))
        return {'Output': Output}

    def name(self):
        return 'Generate an example project'

    def displayName(self):
        return 'Generate an example project'

    def group(self):
        return 'Help'

    def groupId(self):
        return '0help'
        
    def shortHelpString(self):
        return """
        Select a folder in which create an example project
        """

    def createInstance(self):
        return SeeEXAMPLE()