# -*- coding: utf-8 -*-

"""
/***************************************************************************
 ICEtool
                                 A QGIS plugin
 Estimation of urban heat islands.
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

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon
import os

ICEtoolPath = os.path.dirname(__file__)

from .Scripts.Display_HELP_fr import DisplayHELPfr
from .Scripts.Display_HELP_en import DisplayHELPen
from .Scripts.SeeEXAMPLE import SeeEXAMPLE
from .Scripts.Create_Project import CreateProject
from .Scripts.Step2_TreePoints import CreateRastersTreePoints
from .Scripts.Step2_TreePoly import CreateRastersTreePoly
from .Scripts.Step4_ComputeTemperatureCSV import ComputeGroundTemperatureCSV
from .Scripts.Step4_ComputeTemperatureEPW import ComputeGroundTemperatureEPW


class ICEtoolProvider(QgsProcessingProvider):

    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def unload(self):
        pass

    def loadAlgorithms(self):
        self.addAlgorithm(DisplayHELPfr())
        self.addAlgorithm(DisplayHELPen())
        self.addAlgorithm(SeeEXAMPLE())
        self.addAlgorithm(CreateProject())
        self.addAlgorithm(CreateRastersTreePoints())
        self.addAlgorithm(CreateRastersTreePoly())
        self.addAlgorithm(ComputeGroundTemperatureCSV())
        self.addAlgorithm(ComputeGroundTemperatureEPW())


    def id(self):
        return 'ICEtool'

    def name(self):
        return self.tr('ICEtool')

    def icon(self):
        return QIcon(os.path.join(ICEtoolPath, "Icons","icon.png"))

    def longName(self):
        return self.name()
