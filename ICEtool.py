# -*- coding: utf-8 -*-

"""
/***************************************************************************
 ICEtool
                                 A QGIS plugin
 Estimation of urban heat island.
                              -------------------
        begin                : 2021-11-12
        copyright            : (C) 2021 by Arthur Evrard
        email                : arthur.evrard.pro@orange.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Arthur Evrard'
__date__ = '2021-11-12'
__copyright__ = '(C) 2021 by Arthur Evrard'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import sys
import inspect

from qgis.core import QgsProcessingAlgorithm, QgsApplication
from .ICEtool_provider import ICEtoolProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class ICEtoolPlugin(object):

    def __init__(self):
        self.provider = None

    def initProcessing(self):
        self.provider = ICEtoolProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
