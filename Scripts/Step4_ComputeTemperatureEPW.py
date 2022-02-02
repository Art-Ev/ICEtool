"""
 -----------------------------------------------------------------------------------------------------------
 Original Author:  Arthur Evrard
 Contributors:
 Last edited by: Arthur Evrard
 Repository:  https://github.com/Art-Ev/ICEtool
 Created:    2021-11-12 (Arthur Evrard)
 Updated:
   2022-02-02   Fix Stefan - Boltzman constant
 -----------------------------------------------------------------------------------------------------------
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterDefinition
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProcessingContext
from qgis.core import QgsProject
from qgis.core import Qgis
from qgis.core import QgsVectorLayer
import processing
import time
import sys
import os
import statistics
import pandas as pd
from scipy import optimize
import csv

class ComputeGroundTemperatureEPW(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('grounddescriptionlayer', 'Ground description layer', types=[QgsProcessing.TypeVectorPolygon], defaultValue='Ground'))
        self.addParameter(QgsProcessingParameterVectorLayer('buildingslayer', 'Buildings layer', types=[QgsProcessing.TypeVectorPolygon], defaultValue='Buildings'))
        self.addParameter(QgsProcessingParameterFile('etpdata', 'ETP data (csv)', behavior=QgsProcessingParameterFile.File, fileFilter='CSV (*.csv)', defaultValue=os.path.join(QgsProject.instance().absolutePath(), 'Step_1', 'ETP.csv')))
        self.addParameter(QgsProcessingParameterFile('weatherdataepw', 'Weather data (epw)', behavior=QgsProcessingParameterFile.File, fileFilter='EPW (*.epw)', defaultValue=os.path.join(QgsProject.instance().absolutePath(), 'Step_1', 'WeatherData.epw')))
        self.addParameter(QgsProcessingParameterNumber('day', 'Day', type=QgsProcessingParameterNumber.Integer, minValue=1, maxValue=31, defaultValue=21))
        self.addParameter(QgsProcessingParameterNumber('month', 'Month', type=QgsProcessingParameterNumber.Integer, minValue=1, maxValue=12, defaultValue=7))
        param = QgsProcessingParameterNumber('spatialaccuracy', 'Spatial accuracy', type=QgsProcessingParameterNumber.Double, minValue=0.1, maxValue=5, defaultValue=1)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
        results = {}
        outputs = {}
        ProjectPath=QgsProject.instance().absolutePath()
        FilePath=os.path.dirname(__file__)
        SCR = self.parameterAsVectorLayer(parameters, 'grounddescriptionlayer', context).crs().authid()
        
        existing_layers_paths = [layer.dataProvider().dataSourceUri().split('|')[0] for layer in QgsProject.instance().mapLayers().values()]
        for path in existing_layers_paths:
            if 'ComputedPoints.csv' in path:
                feedback.pushInfo('Result layer detected in your QGIS project, please remove it before launching any calculation')
                sys.exit('result layer already in QGIS project')
        
        feedback.pushInfo('Creation of points grid')
        # Initial grid
        alg_params = {
            'CRS': parameters['grounddescriptionlayer'],
            'EXTENT': parameters['grounddescriptionlayer'],
            'HOVERLAY': 0,
            'HSPACING': str(4/parameters['spatialaccuracy']),
            'TYPE': 0,  # Point
            'VOVERLAY': 0,
            'VSPACING': str(4/parameters['spatialaccuracy']),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['InitialGrid'] = processing.run('native:creategrid', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # Spatial_index_1
        alg_params = {
            'INPUT': outputs['InitialGrid']['OUTPUT']
        }
        if Qgis.QGIS_VERSION_INT>=31600:
            outputs['Spatial_index_1'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        else:
            outputs['Spatial_index_1'] = processing.run('qgis:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        
        feedback.pushInfo('')
        feedback.pushInfo('Retrieving of materials data')
        # Intersection
        alg_params = {
            'INPUT': outputs['Spatial_index_1']['OUTPUT'],
            'INPUT_FIELDS': ['id'],
            'OVERLAY': parameters['grounddescriptionlayer'],
            'OVERLAY_FIELDS': ['Material','alb','em','Cv','lambd','ep','kc','FixedTemp[degC]'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Intersection'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # Spatial_index_2
        alg_params = {
            'INPUT': outputs['Intersection']['OUTPUT']
        }
        if Qgis.QGIS_VERSION_INT>=31600:
            outputs['Spatial_index_2'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        else:
            outputs['Spatial_index_2'] = processing.run('qgis:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Extraire par localisation
        alg_params = {
            'INPUT': outputs['Spatial_index_2']['OUTPUT'],
            'INTERSECT': parameters['buildingslayer'],
            'PREDICATE': [2],  # est disjoint
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtraireParLocalisation'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # Compute x
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'x',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Flottant
            'FORMULA': 'x($geometry)',
            'INPUT': outputs['ExtraireParLocalisation']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        if Qgis.QGIS_VERSION_INT>=31600:
            outputs['ComputeX'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        else:
            outputs['ComputeX'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # Compute y
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'y',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Flottant
            'FORMULA': 'y($geometry)',
            'INPUT': outputs['ComputeX']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        if Qgis.QGIS_VERSION_INT>=31600:
            outputs['ComputeY'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        else:
            outputs['ComputeY'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # Spatial_index_3
        alg_params = {
            'INPUT': outputs['ComputeY']['OUTPUT']
        }
        if Qgis.QGIS_VERSION_INT>=31600:
            outputs['Spatial_index_3'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        else:
            outputs['Spatial_index_3'] = processing.run('qgis:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        
        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}
        
        feedback.pushInfo('')
        feedback.pushInfo('Retrieving shadow information from rasters')
        
        # Get shadow values for each hour
        Shadow_h=[]
        for file in os.scandir(os.path.join(ProjectPath,'Step_3')):
            if (file.path.endswith(".tif")) and 'fraction_on' not in os.path.basename(file.path):
                h=int(os.path.basename(file.path).split("_")[2][:2])
                Shadow_h.append(h)
                
                # Extract raster values
                last_saved=os.path.join(ProjectPath,'Step_4','Temp',str(h)+'.csv')
                alg_params = {
                    'COLUMN_PREFIX': 'Shadow',
                    'INPUT': outputs['Spatial_index_3']['OUTPUT'],
                    'RASTERCOPY': file.path,
                    'OUTPUT': os.path.join(ProjectPath,'Step_4','Temp',str(h)+'.csv')
                }
                if Qgis.QGIS_VERSION_INT>=31600:
                    outputs['PrleverDesValeursRasters'] = processing.run('native:rastersampling', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
                else:
                    outputs['PrleverDesValeursRasters'] = processing.run('qgis:rastersampling', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        other_hours=pd.read_csv(last_saved,sep=',')
        # Settings shadow during night, 0
        if Qgis.QGIS_VERSION_INT>=31600:
            other_hours["Shadow1"]=0
        else:
            other_hours["Shadow_1"]=0

        for h in range(24):
            if not(h+1 in Shadow_h):
                # Set shadow to 0 during night
                other_hours.to_csv(os.path.join(ProjectPath, 'Step_4', 'Temp',str(h+1)+'.csv'),index=False, mode='w', header=True, sep=',')
        
        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}
        
        feedback.pushInfo('')
        feedback.pushInfo('Preparing all data for temperature calculation...')
        # Group all csv files and save id_list
        for h in range (24):
            temp=pd.read_csv(os.path.join(ProjectPath,'Step_4','Temp',str(h+1)+'.csv'),sep=',')
            temp["hour"]=h+1
            if h==0:
                temp.to_csv(os.path.join(ProjectPath, 'Step_4', 'ComputedPoints.csv'),index=False, mode='w', header=True, sep=',')
            else:
                id_list=temp["id"].tolist()
                temp.to_csv(os.path.join(ProjectPath, 'Step_4', 'ComputedPoints.csv'), index=False, mode='a', header=False, sep=',')
            os.remove(os.path.join(ProjectPath,'Step_4','Temp',str(h+1)+'.csv'))
        del temp

        day=parameters['day']
        month=parameters['month']
        
        #ground temperature at 20cm
        Tint=35+273.15

        #import all points to process
        Pts_list=pd.read_csv(os.path.join(ProjectPath, 'Step_4', 'ComputedPoints.csv'), sep=',')
        if Qgis.QGIS_VERSION_INT<31600:
            Pts_list["Shadow1"]=Pts_list["Shadow_1"]

        #aggregate shadow information
        pts_matrix=Pts_list.sort_values(by=["hour"]).groupby(by=["id"]).agg({'id':'first','x':'first','y':'first','Material':'first','alb': 'first', 'em': 'first', 'Cv': 'first', 'lambd': 'first', 'ep': 'first', 'kc': 'first', 'FixedTemp[degC]': 'first', 'Shadow1':list})
        pts_matrix['Shadow1'] = pts_matrix['Shadow1'].apply(lambda x: tuple(x))
        pts_matrix['key']=pts_matrix.Material.astype(str)+'-'+pts_matrix.Shadow1.astype(str)

        feedback.pushInfo('')
        feedback.pushInfo('Simplification of the problem...')
        #Simplification of the problem
        simplified=pts_matrix.groupby(by=["key"]).agg({'key':'first', 'id':'first','alb': 'first', 'em': 'first', 'Cv': 'first', 'lambd': 'first', 'ep': 'first', 'kc': 'first', 'FixedTemp[degC]': 'first', 'Shadow1':'first'})

        #import ETP infos
        ETP=pd.read_csv(parameters['etpdata'],sep=';')
        ETP_unit=float(ETP.iloc[month-1]['ETP_project[mm/day]'].replace(',','.'))*2260000/3600
        # To normalize the ETP in the day (to avoid doing ETo/24 in 24h in the day) we use the following averaging values
        ETo_norm= (0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.03,0.06,0.09,0.1,0.11,0.11,0.11,0.09,0.07,0.04,0.03,0.02,0.01,0.01,0.01)
        Eto_norm= [round(x * ETP_unit,4) for x in ETo_norm] #ETo in W/m2.s
        simplified["ETO"]= [Eto_norm]* len(simplified)
        simplified["ETO"] = simplified["ETO"].apply(lambda x: tuple(x))

        #import weather data
        with open(str(parameters['weatherdataepw']), newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for i,row in enumerate(csvreader):
                if row[0].isdigit():
                    break
        first_row=i # Get first row of epw file
        names=['Year', 'month','day', 'hour','Minute','Data Source and Uncertainty Flags','Dry Bulb Temperature [DegC]','Dew Point Temperature','Relative Humidity','Atmospheric Station Pressure','Extraterrestrial Horizontal Radiation','Extraterrestrial Direct Normal Radiation','Horizontal Infrared Radiation Intensity','Global Horizontal Radiation [Wh/m2]','Direct Normal Radiation','Diffuse Horizontal Radiation','Global Horizontal Illuminance','Direct Normal Illuminance','Diffuse Horizontal Illuminance','Zenith Luminance','Wind Direction','Wind Speed','Total Sky Cover','Opaque Sky Cover','Visibility','Ceiling Height','Present Weather Observation','Present Weather Codes','Precipitable Water','Aerosol Optical Depth','Snow Depth','Days Since Last Snowfall','Albedo','Liquid Precipitation Depth','Liquid Precipitation Quantity']
        WeatherData=pd.read_csv(parameters['weatherdataepw'], skiprows=first_row, header=None, names=names)

        #Emprical Fuentes correlation (1987), to replace in future versions with better approximation
        WeatherData["Tsky"]=round((0.037536*(WeatherData["Dry Bulb Temperature [DegC]"]**1.5))+(0.32*WeatherData["Dry Bulb Temperature [DegC]"])+273.15,2)

        #Add weather data to simplified problem
        WeatherData["Dry Bulb Temperature [DegC]"]=WeatherData["Dry Bulb Temperature [DegC]"]+273.15
        AirTemp=tuple(WeatherData[(WeatherData["month"]==month) & (WeatherData["day"]==day)]["Dry Bulb Temperature [DegC]"])
        simplified["Tair"]= [AirTemp] * len(simplified)
        SolarRadiation=tuple(WeatherData[(WeatherData["month"]==month) & (WeatherData["day"]==day)]["Global Horizontal Radiation [Wh/m2]"])
        simplified["Gh"]= [SolarRadiation] * len(simplified)
        SkyTemp=tuple(WeatherData[(WeatherData["month"]==month) & (WeatherData["day"]==day)]["Tsky"])
        simplified["Tsky"]= [SkyTemp] * len(simplified)

        #Function to solve the thermal problem

        # We want to solve the equation for the balance of energy to get surface temperature
        # calc[m][h]= -Gh[h]*(1-alb[m]/100)+((em[m]/100)*sigma*((Tsurf[m][h]+273.15)**4-(Tskyb)**4))+hc*(Tsurf[m][h]-Tair[h])+(lambd[m]/ep[m])*(Tsurf[m][h]+273.15-Tint)+ Cv[m]*ep[m]*DTsdt+EVP
        # with DTsdt= (Tsurf-Tsurf0)/3600

        # Equation which can be simplified as A + BT + CT^4
        # This function returns the 3 parameters : A, B and C

        #thermal equilibrium equation
        def thermal_equation(x,A,B,C):
            return A + (B * x) + ( C * ((x) ** 4) )

        # Depending on :

        # Gh(solar incidence) and Tair (Temperature of the air at 10m) are array depending on the hour

        # Tint is a float and stands for the Temperature of the ground in K, which is consider constant
        # Tskyb is a float and stands for the Temperature of the sky in K , which is consider constant

        # alb (albedo), em (emissivity),lambd (thermique conductivity coef in W/m.K),ep (thickness in m),
        # Cv (thermal volumetric capacity of concrete in J/m3.K) are arrays depending on the material/point

        hc=5 # Wind coefficient W.m-2.K-1

        sigma = 5.67e-08 #Stefan - Boltzman constant in W.m-2.K-4

        simplified["B"]=hc+(simplified["lambd"]/simplified["ep"])+(simplified["Cv"]*simplified["ep"]/3600)
        simplified["C"]=simplified["em"]*sigma

        def compute_A(Shadow,Gh,alb,em,Tsky,Tair,lambd,ep,Cv,ETO,kc,T0):
            a0= -((0.8*Gh*Shadow*(1-alb))+(0.2*Gh))
            a1= (em*sigma) * -(Tsky)**4
            a2= -hc*Tair
            a3= -(lambd/ep)*Tint
            a4= -(Cv*ep/3600)*T0
            a5= ETO*kc
            result=( a0+a1+a2+a3+a4+a5 )
            return result

        # h int of hour of the day -1

        # x= Tsurf of the moment of calculation
        # T0 is the Ti-1, so the Temperature of surface in the time i-1

        threshold = 0.5 # Calculation threshold, default = 0.5 degree Celsius

        def compute_temp(id,FixedTemp, Shadow, B, C, Gh,alb,em,Tsky,Tair,lambd,ep,Cv,ETO,kc):
            Temp_DegC = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            if not (FixedTemp==0):
                for h in range(24):
                    Temp_DegC[h]=FixedTemp
            else:
                T0=28+273.15 #initial guess temp at midnight
                count=0
                equilibrium=False
                while equilibrium==False:
                    for h in range(24):
                        if h==0:
                            A = compute_A(Shadow[h], Gh[h], alb, em, Tsky[h], Tair[h],lambd, ep, Cv, ETO[h], kc, T0)
                            Temp_DegC[h] = optimize.root(thermal_equation, T0 - 0.5, (A, B, C)).x[0]
                        else:
                            A = compute_A(Shadow[h], Gh[h], alb, em, Tsky[h], Tair[h],lambd, ep, Cv, ETO[h], kc, Temp_DegC[h-1])
                            if Shadow[h]>0.4:
                                Temp_DegC[h] = optimize.root(thermal_equation, Temp_DegC[h-1] + 1.0, (A, B, C)).x[0]
                            else:
                                Temp_DegC[h] = optimize.root(thermal_equation, Temp_DegC[h-1] - 0.5, (A, B, C)).x[0]
                    count += 1
                    # At least 2 iterations, check convergence and stop after 25
                    if count >= 2:
                        error=abs(Temp_DegC[23]-T0)
                        if error < threshold:
                            equilibrium=True
                        elif count==25:
                            feedback.pushInfo('Equilibrium failed after 25 iterations for point :'+str(id))
                            equilibrium=True
                    T0=Temp_DegC[23]

                for h in range(24):
                    Temp_DegC[h] = round(Temp_DegC[h]-273.15,2)
            return Temp_DegC

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        feedback.pushInfo('')
        feedback.pushInfo('Calculation of the temperatures of all points for each hour...')
        #Apply function to the simplified problem(parallelized)
        simplified["Temp_DegC"]= simplified.apply(lambda row: compute_temp(row["id"],row["FixedTemp[degC]"],row["Shadow1"],row["B"],row["C"],row["Gh"],row["alb"],row["em"],row["Tsky"],row["Tair"],row["lambd"],row["ep"],row["Cv"],row["ETO"],row["kc"]),axis=1)
        simplified["min_DegC"]=simplified["Temp_DegC"].apply(min)
        simplified["mean_DegC"]=round(simplified["Temp_DegC"].apply(statistics.mean),2)
        simplified["max_DegC"]=simplified["Temp_DegC"].apply(max)

        output=pts_matrix.merge(simplified.set_index('id').filter(items=['key','Temp_DegC','min_DegC','mean_DegC','max_DegC']), how='left', on='key').filter(items=['id','x','y','Temp_DegC','min_DegC','mean_DegC','max_DegC'])
        output.to_csv(os.path.join(ProjectPath, 'Step_4', 'ComputedPoints.csv'),index=False, mode='w', header=True, sep=',')

        time.sleep(1)
        uri = 'file:///'+os.path.join(ProjectPath, 'Step_4', 'ComputedPoints.csv')+'?delimiter=,&xField=x&yField=y&crs='+SCR+'&spatialIndex=yes'
        result_layer=QgsVectorLayer(uri,"ground_points","delimitedtext")
        result_layer.loadNamedStyle(os.path.join(FilePath,'point_style.qml'))
        context.temporaryLayerStore().addMapLayer(result_layer)
        context.addLayerToLoadOnCompletion(result_layer.id(), QgsProcessingContext.LayerDetails("", QgsProject.instance(), ""))

        output_file=os.path.join(ProjectPath, 'Step_4', 'ComputedPoints.csv')

        return {'Output': output_file}

    def name(self):
        return 'Compute ground temperature (weather data as .epw)'

    def displayName(self):
        return 'Compute ground temperature (weather data as .epw)'

    def group(self):
        return 'Step_4'

    def groupId(self):
        return 'Step_4'

    def createInstance(self):
        return ComputeGroundTemperatureEPW()
