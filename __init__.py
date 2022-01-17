# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ICEtool
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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Arthur Evrard'
__date__ = '2021-11-12'
__copyright__ = '(C) 2021 by Arthur Evrard'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ICEtoolclass from file ICEtool.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .ICEtool import ICEtoolPlugin
    return ICEtoolPlugin()
