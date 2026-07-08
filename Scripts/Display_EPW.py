"""
 -----------------------------------------------------------------------------------------------------------
 Original Author:  Arthur Evrard
 Contributors:
 Last edited by: Arthur Evrard
 Repository:  https://github.com/Art-Ev/ICEtool
 Created:
 Updated:
 -----------------------------------------------------------------------------------------------------------
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsVectorLayer, QgsField, QgsFeature
from PyQt5.QtCore import QVariant
from qgis.core import QgsProject
from qgis.core import QgsMessageLog
from qgis.utils import iface
import pandas as pd
import processing
import os
import csv

class DisplayEPW(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        project = QgsProject.instance()
        self.addParameter(QgsProcessingParameterFile('weatherdataepw', 'Weather data (epw)', behavior=QgsProcessingParameterFile.File, fileFilter='EPW (*.epw)', defaultValue=os.path.join(QgsProject.instance().absolutePath(), 'Step_1', 'WeatherData.epw')))

    def processAlgorithm(self, parameters, context, model_feedback):

        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
        
        with open(str(parameters['weatherdataepw']), newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for i,row in enumerate(csvreader):
                if row[0].isdigit():
                    break
        first_row=i # Get first row of epw file
        names=['Year', 'month','day', 'hour','Minute','Data Source and Uncertainty Flags','Dry Bulb Temperature [DegC]','Dew Point Temperature','Relative Humidity','Atmospheric Station Pressure','Extraterrestrial Horizontal Radiation','Extraterrestrial Direct Normal Radiation','Horizontal Infrared Radiation Intensity','Global Horizontal Radiation [Wh/m2]','Direct Normal Radiation','Diffuse Horizontal Radiation','Global Horizontal Illuminance','Direct Normal Illuminance','Diffuse Horizontal Illuminance','Zenith Luminance','Wind Direction','Wind Speed','Total Sky Cover','Opaque Sky Cover','Visibility','Ceiling Height','Present Weather Observation','Present Weather Codes','Precipitable Water','Aerosol Optical Depth','Snow Depth','Days Since Last Snowfall','Albedo','Liquid Precipitation Depth','Liquid Precipitation Quantity']
        WeatherData=pd.read_csv(parameters['weatherdataepw'], skiprows=first_row, header=None, names=names)
        
        temp = QgsVectorLayer("none","EPW_file","memory")
        temp_data = temp.dataProvider()
        temp.startEditing()

        # Creation of my fields 
        for head in WeatherData :
            Field = QgsField( head, QVariant.Double )
            temp.addAttribute(Field) 
        temp.updateFields()

        # Addition of features
        for index, row in WeatherData.iterrows():
            f = QgsFeature()
            list=[]
            i=0
            for head in WeatherData :
                list.append(row[i])
                i=i+1
            f.setAttributes(list)
            temp.addFeature(f)
        
        temp.commitChanges()
        QgsProject.instance().addMapLayer(temp)
        
        Output='EPW added to QGIS'
        return {'Output': Output}

    def name(self):
        return 'Load an EPW file'

    def displayName(self):
        return 'Load an EPW file'

    def group(self):
        return 'Help'

    def groupId(self):
        return '0help'
        
    def shortHelpString(self):
        return """
        Display a *.epw file
        """

    def createInstance(self):
        return DisplayEPW()
