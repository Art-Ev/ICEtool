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
        feedback = QgsProcessingMultiStepFeedback(5, model_feedback)
        
        FilePath = os.path.dirname(__file__)
        
        project_name = parameters['project_name']
        invalid_chars = '<>:"/\\|?*éè '
        project_name = ''.join('_' if c in invalid_chars else c for c in project_name)
        
        feedback.pushInfo(f"Creating new project based on ICEtool template...")
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
        crs_id=parameters['scr_to_use_for_new_project'].authid()
        
        tmp = gpkg + ".tmp.gpkg"
        if os.path.exists(tmp):
            os.remove(tmp)
        
        options = gdal.VectorTranslateOptions(
            format="GPKG",
            dstSRS=crs_id,
            reproject=False,
        )
        gdal.VectorTranslate(tmp, gpkg, options=options)
       
        i=i+1
        feedback.setCurrentStep(i)
        
        os.remove(gpkg)
        shutil.move(tmp, gpkg)
        time.sleep(2)
           
        crs = parameters['scr_to_use_for_new_project']
        gpkg_target = os.path.normcase(os.path.normpath(gpkg))

        proj = QgsProject()
        if not proj.read(new_qgz):
            feedback.reportError("Cannot read project : " + new_qgz)

        count = 0
        for layer in proj.mapLayers().values():
            src_path = layer.source().split('|', 1)[0]
            src_path = os.path.normcase(os.path.normpath(src_path))
            if src_path == gpkg_target:
                layer.setCrs(crs)
                count += 1
                
        i=i+1
        feedback.setCurrentStep(i)
        feedback.pushInfo(f"Trying to fix QGIS new project...")

        if not proj.write():
            feedback.reportError("Cannot update QGIS project : " + new_qgz)
        
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
        return (' Select a folder in which create your new ICEtool project'
                'For CRS : use only projected coordinate systems')

    def createInstance(self):
        return CreateProject()