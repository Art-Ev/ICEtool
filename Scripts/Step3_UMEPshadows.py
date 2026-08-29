# -*- coding: utf-8 -*-
"""
 -----------------------------------------------------------------------------------------------------------
 Original Author:  UMEP
 Contributors:
 Last edited by: Arthur Evrard
 Repository:  https://github.com/Art-Ev/ICEtool
 Created:    2021-11-12
 Updated:   2026-07
 -----------------------------------------------------------------------------------------------------------
"""
import os

import numpy as np
from osgeo import gdal, osr

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterField,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterNumber,
    QgsProcessingParameterDateTime,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterFolderDestination,
    QgsProject,
    QgsProperty,
)
import processing

from .ShadowGenerator import dailyshading as dsh


class UMEP_shadows(QgsProcessingAlgorithm):

    DSM = 'DSM'
    USE_TREE = 'USE_TREE'
    TREE = 'TREE'
    TREE_RADIUS = 'TREE_RADIUS'
    TREE_ZMIN = 'TREE_ZMIN'
    TREE_ZMAX = 'TREE_ZMAX'
    TREE_PSI = 'TREE_PSI'
    TREE_PSI_DEF = 'TREE_PSI_DEF'
    USE_BLOCK = 'USE_BLOCK'
    BLOCK = 'BLOCK'
    BLOCK_ZMIN = 'BLOCK_ZMIN'
    BLOCK_ZMAX = 'BLOCK_ZMAX'
    BLOCK_PSI = 'BLOCK_PSI'
    BLOCK_PSI_DEF = 'BLOCK_PSI_DEF'
    DATETIME = 'DATETIME'
    ONETIME = 'ONETIME'
    UTC = 'UTC'
    DST = 'DST'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.DSM, 'Buildings and ground raster (DSM)', defaultValue='BuildingTerrain_raster'))

        # trees
        self.addParameter(QgsProcessingParameterBoolean(
            self.USE_TREE, 'Use trees', defaultValue=True))
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.TREE, 'Tree layer',
            [QgsProcessing.TypeVectorPoint], optional=True, defaultValue='Trees'))
        self.addParameter(QgsProcessingParameterField(
            self.TREE_RADIUS, 'Trees - foliage radius',
            parentLayerParameterName=self.TREE, type=QgsProcessingParameterField.Numeric,
            optional=True, defaultValue='Radius [m]'))
        self.addParameter(QgsProcessingParameterField(
            self.TREE_ZMAX, 'Trees - treetop',
            parentLayerParameterName=self.TREE, type=QgsProcessingParameterField.Numeric,
            optional=True, defaultValue='Height [m]'))
        self.addParameter(QgsProcessingParameterField(
            self.TREE_ZMIN, 'Trees - foliage underside',
            parentLayerParameterName=self.TREE, type=QgsProcessingParameterField.Numeric,
            optional=True, defaultValue='Foliage_underside [m]'))
        self.addParameter(QgsProcessingParameterField(
            self.TREE_PSI, 'Trees - foliage transparency',
            parentLayerParameterName=self.TREE, type=QgsProcessingParameterField.Numeric,
            optional=True, defaultValue='Foliage_transparency [%]'))
        self.addParameter(QgsProcessingParameterNumber(
            self.TREE_PSI_DEF, 'Trees - default foliage transparency (if no value)',
            QgsProcessingParameterNumber.Double, defaultValue=0.03, minValue=0.0, maxValue=1.0))

        # shading blocks
        params=[]
        params.append(QgsProcessingParameterBoolean(
            self.USE_BLOCK, 'Use shading blocks', defaultValue=False))
        params.append(QgsProcessingParameterVectorLayer(
            self.BLOCK, 'Shading blocks layer',
            [QgsProcessing.TypeVectorPolygon], optional=True, defaultValue='Shading_blocks'))
        params.append(QgsProcessingParameterField(
            self.BLOCK_ZMIN, 'Shading blocks - min height',
            parentLayerParameterName=self.BLOCK, type=QgsProcessingParameterField.Numeric,
            optional=True, defaultValue='h_min'))
        params.append(QgsProcessingParameterField(
            self.BLOCK_ZMAX, 'Shading blocks - max height',
            parentLayerParameterName=self.BLOCK, type=QgsProcessingParameterField.Numeric,
            optional=True, defaultValue='h_max'))
        params.append(QgsProcessingParameterField(
            self.BLOCK_PSI, 'Shading blocks - transparency',
            parentLayerParameterName=self.BLOCK, type=QgsProcessingParameterField.Numeric,
            optional=True, defaultValue='Transparency [%]'))
        params.append(QgsProcessingParameterNumber(
            self.BLOCK_PSI_DEF, 'Shading blocks - default transparency (if no value)',
            QgsProcessingParameterNumber.Double, defaultValue=0.0, minValue=0.0, maxValue=1.0))
        for param in params:
            param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(param)

        # time
        self.addParameter(QgsProcessingParameterDateTime(
            self.DATETIME, 'Date',
            type=QgsProcessingParameterDateTime.Date))
        self.addParameter(QgsProcessingParameterNumber(
            self.UTC, 'UTC offset', QgsProcessingParameterNumber.Integer, defaultValue=1))
        self.addParameter(QgsProcessingParameterBoolean(
            self.DST, 'Daylight Saving Time (DST)', defaultValue=True))

    def _read_raster(self, layer):
        ds = gdal.Open(layer.source())
        if ds is None:
            raise QgsProcessingException('Cannot open raster layer : ' + layer.source())
        arr = ds.ReadAsArray().astype(np.float64)
        nd = ds.GetRasterBand(1).GetNoDataValue()
        if nd is not None:
            arr[arr == nd] = 0.
        return ds, arr

    def _rasterize(self, vlayer, field, burn, extent_str, cols, rows, context, feedback):
        params = {
            'INPUT': vlayer,
            'FIELD': field if field else '',
            'BURN': 0.0 if field else float(burn),
            'UNITS': 0,
            'WIDTH': cols,
            'HEIGHT': rows,
            'EXTENT': extent_str,
            'NODATA': 0.0,
            'INIT': 0.0,
            'DATA_TYPE': 5,
            'INVERT': False,
            'OUTPUT': 'TEMPORARY_OUTPUT',
        }
        res = processing.run('gdal:rasterize', params, context=context,
                             feedback=feedback, is_child_algorithm=True)
        ds = gdal.Open(res['OUTPUT'])
        return ds.ReadAsArray().astype(np.float64)
        
    def _points_to_crowns(self, plyr, radius_field, context, feedback):
        distance = QgsProperty.fromExpression('"%s"' % radius_field)
        res = processing.run('native:buffer', {
            'INPUT': plyr,
            'DISTANCE': distance,
            'SEGMENTS': 12,
            'END_CAP_STYLE': 0,
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'DISSOLVE': False,
            'OUTPUT': 'TEMPORARY_OUTPUT',
        }, context=context, feedback=feedback, is_child_algorithm=True)
        return res['OUTPUT']

    def processAlgorithm(self, parameters, context, feedback):
        dsmlayer = self.parameterAsRasterLayer(parameters, self.DSM, context)
        if dsmlayer is None:
            raise QgsProcessingException('MNS invalide')

        gdal_dsm, dsm = self._read_raster(dsmlayer)
        sizex, sizey = dsm.shape[0], dsm.shape[1]

        # lon / lat / scale (WGS84)
        gt = gdal_dsm.GetGeoTransform()
        scale = 1. / gt[1]
        cols = gdal_dsm.RasterXSize
        rows = gdal_dsm.RasterYSize
        old_cs = osr.SpatialReference()
        old_cs.ImportFromWkt(dsmlayer.crs().toWkt())
        new_cs = osr.SpatialReference()
        new_cs.ImportFromEPSG(4326)
        tr = osr.CoordinateTransformation(old_cs, new_cs)
        minx = gt[0]
        miny = gt[3] + cols * gt[4] + rows * gt[5]
        lonlat = tr.TransformPoint(minx, miny)
        if float(gdal.__version__[0]) >= 3.:
            lon, lat = lonlat[1], lonlat[0]
        else:
            lon, lat = lonlat[0], lonlat[1]

        xmin = gt[0]
        ymax = gt[3]
        xmax = xmin + cols * gt[1]
        ymin = ymax + rows * gt[5]
        extent_str = '%f,%f,%f,%f [%s]' % (xmin, xmax, ymin, ymax, dsmlayer.crs().authid())

        zeros = np.zeros((sizex, sizey))

        # Trees
        usetree = 1 if self.parameterAsBool(parameters, self.USE_TREE, context) else 0
        tree_top = tree_bottom = tree_psi = zeros
        if usetree:
            tlayer = self.parameterAsVectorLayer(parameters, self.TREE, context)
            zmin_f = self.parameterAsString(parameters, self.TREE_ZMIN, context)
            zmax_f = self.parameterAsString(parameters, self.TREE_ZMAX, context)
            psi_f = self.parameterAsString(parameters, self.TREE_PSI, context)
            radius_f = self.parameterAsString(parameters, self.TREE_RADIUS, context)
            psi_def = self.parameterAsDouble(parameters, self.TREE_PSI_DEF, context)
            if tlayer is None or not zmax_f:
                raise QgsProcessingException('Couche arbres / champ sommet manquant')
            
            crowns = self._points_to_crowns(tlayer, radius_f, context, feedback)
            
            tree_top = self._rasterize(crowns, zmax_f, 0, extent_str, cols, rows, context, feedback)
            tree_bottom = self._rasterize(crowns, zmin_f, 0, extent_str, cols, rows, context, feedback) if zmin_f else np.zeros((sizex, sizey))
            tree_psi = self._rasterize(crowns, psi_f, psi_def, extent_str, cols, rows, context, feedback)
            tree_top = np.where(tree_top > 0, tree_top + dsm, 0.)
            tree_bottom = np.where(tree_bottom > 0, tree_bottom + dsm, 0.)
            tree_psi = np.where(tree_top > 0, tree_psi, 1.0)

        # Shading blocks
        useblock = 1 if self.parameterAsBool(parameters, self.USE_BLOCK, context) else 0
        block_top = block_bottom = block_psi = zeros
        if useblock:
            blayer = self.parameterAsVectorLayer(parameters, self.BLOCK, context)
            zmin_f = self.parameterAsString(parameters, self.BLOCK_ZMIN, context)
            zmax_f = self.parameterAsString(parameters, self.BLOCK_ZMAX, context)
            psi_f = self.parameterAsString(parameters, self.BLOCK_PSI, context)
            psi_def = self.parameterAsDouble(parameters, self.BLOCK_PSI_DEF, context)
            if blayer is None or not zmax_f or not zmin_f:
                raise QgsProcessingException('Couche blocs / champs zmin,zmax manquants')
            block_top = self._rasterize(blayer, zmax_f, 0, extent_str, cols, rows, context, feedback)
            block_bottom = self._rasterize(blayer, zmin_f, 0, extent_str, cols, rows, context, feedback)
            block_psi = self._rasterize(blayer, psi_f, psi_def, extent_str, cols, rows, context, feedback)
            block_top = np.where(block_top > 0, block_top + dsm, 0.)
            block_bottom = np.where(block_bottom > 0, block_bottom + dsm, 0.)
            block_psi = np.where(block_top > 0, block_psi, 1.0)

        # Walls (from UMEP, not used)
        wallsh = 0
        wheight = waspect = 0

        # time
        qdt = self.parameterAsDateTime(parameters, self.DATETIME, context)
        d = qdt.date()
        t = qdt.time()
        UTC = self.parameterAsInt(parameters, self.UTC, context)
        dst = 1 if self.parameterAsBool(parameters, self.DST, context) else 0
        interval = 60
        tv = [d.year(), d.month(), d.day(), 0, 0, 0]

        ProjectPath=QgsProject.instance().absolutePath()
        folder = os.path.join(ProjectPath,'Step_3')

        result = dsh.dailyshading(
            dsm, scale, lon, lat, sizex, sizey, tv, UTC, interval, 0,
            feedback, folder, gdal_dsm, dst, wallsh, wheight, waspect,
            usetree, tree_top, tree_bottom, tree_psi,
            useblock, block_top, block_bottom, block_psi)

        shfinal = result['shfinal']
        tvec = result['time_vector']
        outname = 'shadow_fraction_on_' + tvec.strftime('%Y%m%d') + '.tif'
        outpath = os.path.join(folder, outname)
        dsh.saveraster(gdal_dsm, outpath, shfinal)

        return {'Output': folder, 'RESULT': outpath}

    def name(self):
        return 'Compute shadows [UMEP]'

    def displayName(self):
        return 'Compute shadows [UMEP]'

    def group(self):
        return 'Step_3'

    def groupId(self):
        return 'Step_3'

    def shortHelpString(self):
        return ('Shadow calculation. The transparency of tree foliage is retrieved directly from the layer. '
                'Advanced settings: shadow blocks can be used to represent building eaves, solar panels, etc.')

    def createInstance(self):
        return UMEP_shadows()
