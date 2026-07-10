# -*- coding: utf-8 -*-
"""
 -----------------------------------------------------------------------------------------------------------
 Original Author:  Arthur Evrard
 Contributors:
 Last edited by: Arthur Evrard
 Repository:  https://github.com/Art-Ev/ICEtool
 Created:    2021-11-12 (Arthur Evrard)
 Updated:   2026-07
 -----------------------------------------------------------------------------------------------------------
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterDefinition
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProcessingParameterDateTime
from qgis.core import QgsProcessingContext
from qgis.core import QgsProcessingParameterEnum
from qgis.core import QgsProcessingUtils
from qgis.core import QgsProject
from qgis.core import Qgis
from qgis.core import QgsVectorLayer
from osgeo import gdal
import processing
import time
import sys
import glob, os
import statistics
import pandas as pd
from scipy import optimize
import csv
import numpy as np

class ComputeGroundTemperatureEPW(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('grounddescriptionlayer', 'Ground description layer', types=[QgsProcessing.TypeVectorPolygon], defaultValue='Ground'))
        self.addParameter(QgsProcessingParameterVectorLayer('buildingslayer', 'Buildings layer', types=[QgsProcessing.TypeVectorPolygon], defaultValue='Buildings'))
        self.addParameter(QgsProcessingParameterFile('weatherdataepw', 'Weather data (epw)', behavior=QgsProcessingParameterFile.File, fileFilter='EPW (*.epw)', defaultValue=os.path.join(QgsProject.instance().absolutePath(), 'Step_1', 'WeatherData.epw')))
        self.addParameter(QgsProcessingParameterDateTime('Date', 'Date', type=QgsProcessingParameterDateTime.Date))
        self.addParameter(QgsProcessingParameterEnum('fuseau','Time zone', options=['UTC 0 Greenwich London, Lisbon, Abidjan','UTC -1 Azores, Cabo Verde','UTC -2','UTC-3 Greenland, Brasilia, Buenos Aires','UTC-4 Santiago, Caracas, La Paz','UTC-5 Montreal, New York, Lima, Havana','UTC-6 Chicago, Mexico, Dallas','UTC-7 Denver, Edmonton','UTC-8 Los Angeles, Vancouver',
                                                     'UTC-9 Alaska','UTC-10 French Polynesia, Hawai','UTC-11 Tonga','UTC-12 _ + 12 Auckland, Fiji, Marchall Islands','UTC + 11 New Caledonia, Solomon Island','UTC +10 Sydney, Melbourne','UTC + 9 Tokyo, Seoul, Center Australia','UTC +8 Beijing, Hong Kong, West Australia','UTC + 7 Thailand, Vietnam','UTC + 6 Nur-Sultan, Bangladesh','UTC + 5 Ouzbekistan, Pakistan, New Dehli','UTC + 4 Teheran, Oman','UTC + 3 Moscou, Istanbul, Nairobi','UTC + 2 Kiev, Le Caire, Le Cap','UTC + 1 Berlin, Paris, Madrid, Alger'], allowMultiple=False, defaultValue=23))
        param = QgsProcessingParameterNumber('altitude', 'Altitude (meters)', type=QgsProcessingParameterNumber.Integer, minValue=0, maxValue=10000, defaultValue=100)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
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
        
        day=parameters['Date'].day()
        month=parameters['Date'].month()
        alt=parameters['altitude']
        fuseau=parameters['fuseau']
        fuseau_list=pd.read_csv(os.path.join(FilePath,'Fuseaux_horaires.csv'), sep=';')
        longz=fuseau_list.iloc[fuseau]['Longitude']
        
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
            'HSPACING': str(2/parameters['spatialaccuracy']),
            'TYPE': 0,  # Point
            'VOVERLAY': 0,
            'VSPACING': str(2/parameters['spatialaccuracy']),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['InitialGrid'] = processing.run('native:creategrid', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        feedback.pushInfo('Spatial Index1')
        
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
            'JOIN': parameters['grounddescriptionlayer'],
            'JOIN_FIELDS': ['Material','alb','em','Cv','lambd','ep','kc','FixedTemp[degC]'],
            'PREDICATE': [0],
            'METHOD': 1,
            'DISCARD_NONMATCHING': True,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Intersection'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

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

        # Extract by location
        alg_params = {
            'INPUT': outputs['Spatial_index_2']['OUTPUT'],
            'INTERSECT': parameters['buildingslayer'],
            'PREDICATE': [2],  # est disjoint
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtraireParLocalisation'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # Spatial_index_3
        alg_params = {
            'INPUT': outputs['ExtraireParLocalisation']['OUTPUT']
        }
        if Qgis.QGIS_VERSION_INT>=31600:
            outputs['Spatial_index_3'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        else:
            outputs['Spatial_index_3'] = processing.run('qgis:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        # Compute x, y, long, lat
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'coords',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,
            'FORMULA': f"x($geometry)||';'||y($geometry)||';'||x(transform($geometry,'{SCR}','EPSG:4326'))||';'||y(transform($geometry,'{SCR}','EPSG:4326'))",
            'INPUT': outputs['ExtraireParLocalisation']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        if Qgis.QGIS_VERSION_INT>=31600:
            outputs['ComputeCoords'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        else:
            outputs['ComputeCoords'] = processing.run('qgis:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)


        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}
        
        feedback.pushInfo('')
        feedback.pushInfo('Retrieving shadow information from rasters')
        
        # Get shadow values for each hour
        pts_layer = QgsProcessingUtils.mapLayerFromString(outputs['ComputeCoords']['OUTPUT'], context)
        base_fields = ['id', 'Material', 'alb', 'em', 'Cv',
                       'lambd', 'ep', 'kc', 'FixedTemp[degC]', 'coords']
        records = [[feat[f] for f in base_fields] for feat in pts_layer.getFeatures()]
        pts_matrix = pd.DataFrame(records, columns=base_fields)
        pts_matrix = pts_matrix.drop_duplicates(subset='id', keep='first')
        
        numeric_fields = ['alb', 'em', 'Cv', 'lambd', 'ep', 'kc', 'FixedTemp[degC]']
        pts_matrix[numeric_fields] = pts_matrix[numeric_fields].apply(pd.to_numeric, errors='coerce')
        pts_matrix['FixedTemp[degC]'] = pts_matrix['FixedTemp[degC]'].fillna(0)
        pts_matrix['id'] = pd.to_numeric(pts_matrix['id'], errors='coerce').astype(int)
        
        pts_matrix['coords'] = pts_matrix['coords'].str.split(';')
        pts_matrix[['x', 'y', 'Long', 'Lat']] = pd.DataFrame(pts_matrix['coords'].tolist(), index=pts_matrix.index)
        pts_matrix["x"] = pts_matrix.x.astype(float)
        pts_matrix["y"] = pts_matrix.y.astype(float)
        pts_matrix["Long"] = pts_matrix.Long.astype(float)
        pts_matrix["Lat"] = pts_matrix.Lat.astype(float)

        xs = np.asarray(pts_matrix['x'].to_numpy(dtype=float), dtype=float)
        ys = np.asarray(pts_matrix['y'].to_numpy(dtype=float), dtype=float)
        n_pts = len(pts_matrix)

        shadow_dir = os.path.join(ProjectPath, 'Step_3')
        tif_files = sorted(
            os.path.join(shadow_dir, f) for f in os.listdir(shadow_dir)
            if f.endswith('.tif') and 'fraction_on' not in f
        )
        
        shadow_by_hour = {}
        for tif in tif_files:
            h = int(os.path.basename(tif).split('_')[2][:2])
            ds = gdal.Open(tif)
            band = ds.GetRasterBand(1)
            arr = band.ReadAsArray()
            nodata = band.GetNoDataValue()

            inv_gt = gdal.InvGeoTransform(ds.GetGeoTransform())
            cols = np.floor(inv_gt[0] + inv_gt[1] * xs + inv_gt[2] * ys).astype(int)
            rows = np.floor(inv_gt[3] + inv_gt[4] * xs + inv_gt[5] * ys).astype(int)
            inside = ((cols >= 0) & (cols < ds.RasterXSize) &
                      (rows >= 0) & (rows < ds.RasterYSize))

            vals = np.zeros(n_pts, dtype=float)
            vals[inside] = arr[rows[inside], cols[inside]]
            if nodata is not None:
                vals[vals == nodata] = 0.0         
            shadow_by_hour[h] = vals
            ds = None
            
        zero = np.zeros(n_pts, dtype=float)
        shadow_matrix = np.column_stack(
            [shadow_by_hour.get(hh, zero) for hh in range(1, 25)])
        pts_matrix['Shadow1'] = [tuple(float(v) for v in row) for row in shadow_matrix]
        
        pts_matrix['key']=pts_matrix.Material.astype(str)+'-'+pts_matrix.Shadow1.astype(str)
        pts_matrix = pts_matrix.set_index('id', drop=False)

        feedback.pushInfo('')
        feedback.pushInfo('Simplification of the problem...')
        
        #Simplification of the problem
        simplified=pts_matrix.groupby(by=["key"]).agg({'key':'first', 'id':'first','alb': 'first', 'em': 'first', 'Cv': 'first', 'lambd': 'first', 'ep': 'first', 'kc': 'first', 'FixedTemp[degC]': 'first', 'Long': 'first', 'Lat': 'first', 'Shadow1':'first'})

        #import weather data
        with open(str(parameters['weatherdataepw']), newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for i,row in enumerate(csvreader):
                if row[0].isdigit():
                    break
        first_row=i # Get first row of epw file
        names=['Year', 'month','day', 'hour','Minute','Data Source and Uncertainty Flags','Dry Bulb Temperature [DegC]','Dew Point Temperature','Relative Humidity','Atmospheric Station Pressure','Extraterrestrial Horizontal Radiation','Extraterrestrial Direct Normal Radiation','Horizontal Infrared Radiation Intensity','Global Horizontal Radiation [Wh/m2]','Direct Normal Radiation','Diffuse Horizontal Radiation','Global Horizontal Illuminance','Direct Normal Illuminance','Diffuse Horizontal Illuminance','Zenith Luminance','Wind Direction','Wind Speed','Total Sky Cover','Opaque Sky Cover','Visibility','Ceiling Height','Present Weather Observation','Present Weather Codes','Precipitable Water','Aerosol Optical Depth','Snow Depth','Days Since Last Snowfall','Albedo','Liquid Precipitation Depth','Liquid Precipitation Quantity']
        WeatherData=pd.read_csv(parameters['weatherdataepw'], skiprows=first_row, header=None, names=names)

        #Empirical Fuentes correlation (1987), to replace in future versions with better approximation
        WeatherData["Tsky"]=round((0.037536*(WeatherData["Dry Bulb Temperature [DegC]"]**1.5))+(0.32*WeatherData["Dry Bulb Temperature [DegC]"])+273.15,2)

        #Add weather data to simplified problem
        WeatherData["Dry Bulb Temperature [DegC]"]=WeatherData["Dry Bulb Temperature [DegC]"]+273.15
        AirTemp=tuple(WeatherData[(WeatherData["month"]==month) & (WeatherData["day"]==day)]["Dry Bulb Temperature [DegC]"])
        simplified["Tair"]= [AirTemp] * len(simplified)
        SolarRadiation=tuple(WeatherData[(WeatherData["month"]==month) & (WeatherData["day"]==day)]["Global Horizontal Radiation [Wh/m2]"])
        simplified["Gh"]= [SolarRadiation] * len(simplified)
        SkyTemp=tuple(WeatherData[(WeatherData["month"]==month) & (WeatherData["day"]==day)]["Tsky"])
        simplified["Tsky"]= [SkyTemp] * len(simplified)
        Humidity=tuple(WeatherData[(WeatherData["month"]==month) & (WeatherData["day"]==day)]["Relative Humidity"])
        simplified["Ha"]=[Humidity]* len(simplified)
        
        #Function to solve the thermal problem

        # We want to solve the equation for the balance of energy to get surface temperature
        # calc[m][h]= -Gh[h]*(1-alb[m]/100)+((em[m]/100)*sigma*((Tsurf[m][h]+273.15)**4-(Tskyb)**4))+hc*(Tsurf[m][h]-Tair[h])+(lambd[m]/ep[m])*(Tsurf[m][h]+273.15-Tint)+ Cv[m]*ep[m]*DTsdt+EVP
        # with DTsdt= (Tsurf-Tsurf0)/3600

        # Equation which can be simplified as A + BT + CT^4
        # This function returns the 3 parameters : A, B and C

        #Ground temperature at 20cm / Cableizer
        list_month=[31,28,31,30,31,30,31,31,30,31,30,31]
        del list_month[month-1:len(list_month)]
        t=0
        for i in list_month :
            t=t+i    
        t=t+day
        
        # Annual Average Temperature (for each hour)
        provisoire=[]
        for i in range(1,25):
            Temp_avg_hour=np.mean(tuple(WeatherData[(WeatherData["hour"]==i)]["Dry Bulb Temperature [DegC]"]))
            provisoire.append(Temp_avg_hour)
        Tyear=tuple(provisoire) 
        simplified["Tyear"]=[Tyear]* len(simplified)
              
        #Maximum annual temperature variation from average
        provisoire2=[]
        for i in provisoire:
            deltaT_hour=max(max(WeatherData["Dry Bulb Temperature [DegC]"])-i,i-min(WeatherData["Dry Bulb Temperature [DegC]"]))
            provisoire2.append(deltaT_hour)
        deltaT=tuple(provisoire2)
        simplified["deltaT"]=[deltaT]* len(simplified)
        
        # Thermal Diffusivity of Soil
        simplified["Dh"]=(simplified["lambd"]/simplified["Cv"])*86400
        
        Z=0.2 #Depth of burial
        w=2*np.pi/365

        def Tint(Tyear, deltaT, Dh): 
            Tsol=[]
            Zo= np.sqrt(2*Dh/w)
            for i in range(0,24):
                Tint=Tyear[i]-deltaT[i]*np.e**(-Z/Zo)*np.cos(w*t-Z/Zo)
                Tsol.append(Tint)
            return Tsol
                   
        simplified["Tint"]= simplified.apply(lambda row: Tint(row["Tyear"],row["deltaT"],row["Dh"]),axis=1)
          
        #Evapotranspiration - Penman-Monteith method
  
        #Coordonate
        longm=pts_matrix["Long"].mean() #exact coordonate

        if longz>170 and longm<0 : 
            longz=longz*-1

        l=(longz-longm)*-1
        
        #Parameters
        sigma_h=2.043*10**-10 #Stefan-Boltzman hour
        Vvent=0.27*(4.87/np.log(67.8*2-5.42))  #Wind speed=1km/h
        Pa=101.3*((293-0.0065*alt)/293)**5.26 #Atmospheric pressure
        gamma=0.000665*Pa # Psychrometric constant
        dr=1+0.033*np.cos((2*np.pi/(365))*t) #Inverse relative distance Earth-Sun
        d=0.409*np.sin((2*np.pi/365)*t-1.39) #Solar declinaison

        def Evapo(Tair,Gh,Ha, lat, alb, shadow ):
            ETO=[]
            th=[0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,13.5,14.5,15.5,16.5,17.5,18.5,19.5,20.5,21.5,22.5,23.5]
            phi=(np.pi/180)*lat # Conversion of latitude in degrees to radian
            b=2*np.pi*(t-81)/364
            Sc= 0.1645*np.sin(2*b)-0.1255*np.cos(b)-0.025*np.sin(b)
            for i in range(0,24):
                Tmean=Tair[i]-273.15
                Rs=Gh[i]*shadow[i]*0.0036
                Rns=(1-alb)*Rs
                delta=4098*(0.6108*np.e**(17.27*Tmean/(Tmean+237.3)))/(Tmean+237.3)**2
                DTjour=delta/(delta+gamma*(1+0.24*Vvent))
                DTnuit=delta/(delta+gamma*(1+0.96*Vvent))
                PTjour=gamma/(delta+gamma*(1+0.24*Vvent))
                PTnuit=gamma/(delta+gamma*(1+0.96*Vvent))
                TT=(37/(Tmean+273.15))*Vvent
                
                es=0.6108*np.e**((17.27*Tmean)/(Tmean+237.3)) 
                Hum=Ha[i]
                ea=es*(Hum/100)
                
                w=(np.pi/12)*((th[i]+0.06667*(l)+Sc)-12)
                ws=np.arccos(-np.tan(phi)*np.tan(d))
                w1=w-np.pi/24
                w2=w+np.pi/24
                if w>-ws and w<ws : #day/night difference
        
                    Ra=(12*(60)/np.pi)*0.0820*dr*((w2-w1)*np.sin(phi)*np.sin(d) + np.cos(phi)*np.cos(d)*(np.sin(w2)-np.sin(w1))) #extraterrestrial radiation
                    Rso=(0.75+(2*10**(-5))*alt)*Ra #Clear sky solar radiation (Rso)
                    Rnl=sigma_h*( (Tmean+273.15)**(4) ) * (0.34 - 0.14 * np.sqrt(ea))*(1.35*(Rs/Rso)-0.35)
                    Rn=Rns-Rnl
                    G=0.1*Rn
                    Rng=0.408*Rn-G
                    ETrad=DTjour*Rng
                    ETwind=PTjour*TT*(es-ea)
                else:
                    Ra=0
                    Rso=(0.75+(2*10**(-5))*alt)*Ra #Clear sky solar radiation (Rso)
                    Rnl=sigma_h*( (Tmean+273.15)**(4) ) * (0.34 - 0.14 * np.sqrt(ea))*(1.35*0.8-0.35)
                    Rn=Rns-Rnl
                    G=0.5*Rn
                    Rng=0.408*Rn-G
                    ETrad=DTnuit*Rng
                    ETwind=PTnuit*TT*(es-ea)
                
        
                ET0=(ETwind+ETrad)*2260000/3600
                if ET0<0:
                        ET0=0
                ETO.append(ET0)
                 
            return ETO
        
        simplified["ETO"]= simplified.apply(lambda row: Evapo(row["Tair"],row["Gh"],row["Ha"], row["Lat"], row["alb"], row["Shadow1"]),axis=1)

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
        alb_f=0.3

        simplified["B"]=hc+(simplified["lambd"]/simplified["ep"])+(simplified["Cv"]*simplified["ep"]/3600)
        simplified["C"]=simplified["em"]*sigma 

        def compute_A(Shadow,Gh,alb,em,Tsky,Tair,lambd,ep,Cv,ET0,kc,Tint, T0):
            a0= -((0.8*Gh*Shadow*(1-alb))+(0.2*Gh*(1-alb)))
            a1= (em*sigma) * -(Tsky)**(4) 
            a2= -hc*Tair
            a3= -(lambd/ep)*Tint
            a4= -(Cv*ep/3600)*T0
            a5= ET0*kc
            result=( a0+a1+a2+a3+a4+a5 )
            return result

        # h int of hour of the day -1

        # x= Tsurf of the moment of calculation
        # T0 is the Ti-1, so the Temperature of surface in the time i-1

        threshold = 0.5 # Calculation threshold, default = 0.5 degree Celsius

        def compute_temp(id, FixedTemp, Shadow, B, C,  Gh, alb, em, Tsky, Tair, lambd, ep, Cv, ET0, Tint, kc):
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
                            A = compute_A(Shadow[h], Gh[h], alb, em, Tsky[h], Tair[h],lambd, ep, Cv, ET0[h], kc, Tint[h], T0)
                            Temp_DegC[h] = optimize.root(thermal_equation, T0 - 0.5, (A, B, C)).x[0]
                        else:
                            A = compute_A(Shadow[h], Gh[h], alb, em, Tsky[h], Tair[h],lambd, ep, Cv, ET0[h], kc, Tint[h], Temp_DegC[h-1])
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
        simplified["Temp_DegC"]= simplified.apply(lambda row: compute_temp(row["id"],row["FixedTemp[degC]"],row["Shadow1"],row["B"],row["C"], row["Gh"],row["alb"],row["em"],row["Tsky"],row["Tair"],row["lambd"],row["ep"], row["Cv"],row["ETO"],row["Tint"],row["kc"]),axis=1)
        simplified["min_DegC"]=simplified["Temp_DegC"].apply(min)
        simplified["mean_DegC"]=round(simplified["Temp_DegC"].apply(statistics.mean),2)
        simplified["max_DegC"]=simplified["Temp_DegC"].apply(max)

        output=pts_matrix.merge(simplified.set_index('id').filter(items=['key','Temp_DegC','min_DegC','mean_DegC','max_DegC']), how='left', on='key').filter(items=['id','x','y','Temp_DegC','min_DegC','mean_DegC','max_DegC'])
        output.to_csv(os.path.join(ProjectPath, 'Step_4', 'ComputedPoints.csv'),index=False, mode='w', header=True, sep=',')

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
