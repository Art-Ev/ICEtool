"""
 -----------------------------------------------------------------------------------------------------------
 Original Author:  Arthur Evrard
 Contributors:
 Last edited by: Arthur Evrard
 Repository:  https://github.com/Art-Ev/ICEtool
 Created:   2021-11-12 (Arthur Evrard)
 Updated:   2026-07
 -----------------------------------------------------------------------------------------------------------
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsVectorLayer
from qgis.core import QgsProcessingParameterCrs
from qgis.core import QgsProject
from qgis.core import QgsMessageLog
from qgis.utils import iface
from osgeo import ogr, osr, gdal
import processing
import subprocess
import shutil
import time
import sys
import os

class CreateProject(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile('destinationfolder', 'Destination Folder', behavior=QgsProcessingParameterFile.Folder, fileFilter='Tous les fichiers (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterString('project_name', 'Project Name', defaultValue='ICEtool_NewProject'))
        self.addParameter(QgsProcessingParameterCrs('scr_to_use_for_new_project', 'SCR to use for new project', defaultValue='EPSG:2154'))
    
    def processAlgorithm(self, parameters, context, model_feedback):
        
        i=0
        feedback = QgsProcessingMultiStepFeedback(7, model_feedback)
        
        FilePath = os.path.dirname(__file__)
        
        project_name = parameters['project_name']
        invalid_chars = '<>:"/\\|?*éè '
        project_name = ''.join('_' if c in invalid_chars else c for c in project_name)
        
        Output='Finished'
        shutil.copytree(os.path.join(FilePath, "ProjectModel"),os.path.join(parameters['destinationfolder'],project_name))
        time.sleep(2)
        
        i=i+1
        feedback.setCurrentStep(i)
        
        old_qgz = os.path.join(parameters['destinationfolder'], project_name, 'ICEtool_NewProject.qgz')
        new_qgz = os.path.join(parameters['destinationfolder'], project_name,  project_name + '.qgz')
        os.rename(old_qgz, new_qgz)
        
        
        i=i+1
        feedback.setCurrentStep(i)
        
        
        gpkg=os.path.join(parameters['destinationfolder'],project_name,'Step_1','Project_data.gpkg')
        srs_id=parameters['scr_to_use_for_new_project'].authid()
        
        tmp = gpkg + ".tmp.gpkg"
        if os.path.exists(tmp):
            os.remove(tmp)
        
        ds = ogr.Open(gpkg, 1)
        layer_names = [ds.GetLayerByIndex(i).GetName() for i in range(ds.GetLayerCount())] 
        
        for j, layer in enumerate(layer_names):
            options = gdal.VectorTranslateOptions(
                format="GPKG",
                layers=[layer],
                accessMode="append" if j > 0 else None,
                dstSRS=srs_id,
                reproject=False
            )
            gdal.VectorTranslate(tmp, gpkg, options=options)
            i=i+1
            feedback.setCurrentStep(i)
        
        ds = None
        os.remove(gpkg)
        shutil.move(tmp, gpkg)
        
        subprocess.Popen([sys.executable, new_qgz])
            
        return {'Output': Output}

    def name(self):
        return 'Create a new project'

    def displayName(self):
        return 'Create a new project'

    def group(self):
        return 'Step_1'

    def groupId(self):
        return 'Step_1'
        
    def shortHelpString(self):
        return """
        Select a folder in which create your new ICEtool project
        """

    def createInstance(self):
        return CreateProject()