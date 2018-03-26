# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BatchInterpolation
                                 A QGIS plugin
 create a batch process for the QGIS Raster Interpolation
                             -------------------
        begin                : 2018-03-21
        copyright            : (C) 2018 by Christoph Jung
        email                : jagodki.cj@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load BatchInterpolation class from file BatchInterpolation.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .batch_interpolation import BatchInterpolation
    return BatchInterpolation(iface)
