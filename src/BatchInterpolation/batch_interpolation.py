# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BatchInterpolation
                                 A QGIS plugin
 create a batch process for the QGIS Raster Interpolation
                              -------------------
        begin                : 2018-03-21
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Christoph Jung
        email                : jagodki.cj@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from qgis.gui import QgsMessageBar
from qgis.core import QgsMessageLog
from batch_interpolation_dialog import BatchInterpolationDialog
import os.path
import sys, traceback, time
from processing.controller import Controller


class BatchInterpolation:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'BatchInterpolation_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = BatchInterpolationDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Batch Interpolation')
        self.controller = Controller()
        
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'BatchInterpolation')
        self.toolbar.setObjectName(u'BatchInterpolation')
        
        #connect signals and slots
        self.dlg.checkBox_contourLines.clicked.connect(self.enable_contour_lines)
        self.dlg.pushButton_output.clicked.connect(self.choose_output_directory)
        self.dlg.pushButton_gdal_contour.clicked.connect(self.choose_gdal_contour_directory)
        self.dlg.comboBox_layers.currentIndexChanged.connect(self.insert_attributes_into_table)
        self.dlg.pushButton_start.clicked.connect(self.start_interpolation)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('BatchInterpolation', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        #self.dlg = BatchInterpolationDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/BatchInterpolation/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Batch-Interpolation'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&Batch-Interpolation'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        #clean up all widgets
        self.dlg.comboBox_layers.clear()
        self.dlg.tableWidget_attributes.setRowCount(0)
        self.dlg.lineEdit_output.setText("")
        self.dlg.lineEdit_gdal_contour.setText(QSettings().value("qgis_batch-interpolation_gdal_contour", ""))
        self.dlg.spinBox_pixelSize.setValue(0)
        self.dlg.doubleSpinBox_contourLines.setValue(0.0)
        self.dlg.checkBox_contourLines.setChecked(False)
        self.dlg.label_contourLines.setEnabled(False)
        self.dlg.lineEdit_gdal_contour.setEnabled(False)
        self.dlg.pushButton_gdal_contour.setEnabled(False)
        self.dlg.label_gdal_contour.setEnabled(False)
        self.dlg.doubleSpinBox_contourLines.setEnabled(False)
        
        #populate the combobox with all layers
        self.insert_layers_into_combobox()
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    #own code starts here
    def start_interpolation(self):
        """Start the interpolation."""
        #store infomration in the settings
        s = QSettings()
        s.setValue("qgis_batch-interpolation_output", self.dlg.lineEdit_output.text())
        s.setValue("qgis_batch-interpolation_gdal_contour", self.dlg.lineEdit_gdal_contour.text())
        
        #evaluate the group of radio buttons
        interpolation_method = ""
        if self.dlg.radioButton_idw.isChecked():
            interpolation_method = "IDW"
        elif self.dlg.radioButton_tin.isChecked():
            interpolation_method = "TIN"
        if interpolation_method == "":
            self.iface.messageBar().pushMessage("Info", "Please choose an interpolation method.", level=QgsMessageBar.INFO, duration=10)
            return True
        
        #check whether an output path is inserted
        if self.dlg.lineEdit_output.text() == "":
            self.iface.messageBar().pushMessage("Info", "No directory choosed for storing the output.", level=QgsMessageBar.INFO, duration=10)
            return True
        
        #check whether the pixel size is unequal 0
        if self.dlg.spinBox_pixelSize.value() == 0:
            self.iface.messageBar().pushMessage("Info", "The pixel size of the resulting raster layer has to be unequal 0.", level=QgsMessageBar.INFO, duration=10)
            return True
        
        #check that the path to gdal_contur is not empty
        if self.dlg.lineEdit_gdal_contour.text() == "" and self.dlg.checkBox_contourLines.isChecked():
            self.iface.messageBar().pushMessage("Info", "Please insert the path to gdal_contour.", level=QgsMessageBar.INFO, duration=10)
            return True
        
        #check whether the distance between contour lines is unequal 0
        if self.dlg.doubleSpinBox_contourLines.value() == 0.0 and self.dlg.checkBox_contourLines.isChecked():
            self.iface.messageBar().pushMessage("Info", "The distance between contour lines has to be unequal 0.", level=QgsMessageBar.INFO, duration=10)
            return True
        
        #call the start-method
        try:
            self.controller.start_batch_process(self.dlg.tableWidget_attributes,
                                                self.dlg.comboBox_layers.currentText(),
                                                interpolation_method,
                                                self.dlg.checkBox_contourLines.isChecked(),
                                                self.dlg.lineEdit_output.text(),
                                                self.dlg.spinBox_pixelSize.value(),
                                                str(self.dlg.doubleSpinBox_contourLines.value()),
                                                self.dlg.progressBar,
                                                self.dlg.lineEdit_gdal_contour.text())
        except:
            self.iface.messageBar().pushMessage("Error", "Interpolation failed. Look into the QGIS-Log and/or the python-window for the stack trace.", level=QgsMessageBar.CRITICAL)
            QgsMessageLog.logMessage(traceback.print_exc(), level=QgsMessageLog.CRITICAL)
    
    def choose_output_directory(self):
        """Opens a file dialog to choose a directory for storing the output of this plugin."""
        #load settings
        s = QSettings()
        output_from_settings = str(s.value("qgis_batch-interpolation_output", ""))
        
        #open file dialog and store the selected path in the settings
        filename = QFileDialog.getExistingDirectory(self.dlg, "Select Output Directory", output_from_settings, QFileDialog.ShowDirsOnly)
        self.dlg.lineEdit_output.setText(filename)
        s.setValue("qgis_batch-interpolation_output", filename)
    
    def choose_gdal_contour_directory(self):
        """Opens a file dialog to choose the absolute path of gdal_contour."""
        #load settings
        s = QSettings()
        gdal_contour_from_settings = str(s.value("qgis_batch-interpolation_gdal_contour", ""))
        
        #open file dialog and store the selected path in the settings
        filename = QFileDialog.getOpenFileName(self.dlg, "Select gdal_contour", gdal_contour_from_settings, "*")
        self.dlg.lineEdit_gdal_contour.setText(filename)
        s.setValue("qgis_batch-interpolation_gdal_contour", filename)
    
    def insert_layers_into_combobox(self):
        """Populate the layer-combobox during start of the plugin."""
        self.controller.populate_layer_list(self.iface, self.dlg.comboBox_layers)
    
    def insert_attributes_into_table(self):
        """Populate the table with the attributes of the selected layer."""
        self.dlg.tableWidget_attributes.setRowCount(0)
        self.controller.populate_attribute_list(self.dlg.comboBox_layers.currentText(), self.dlg.tableWidget_attributes)
        
    def enable_contour_lines(self):
        """Enabling and disabling of GUI elements depending on the status of a checkbox."""
        if self.dlg.checkBox_contourLines.isChecked():
            self.dlg.label_contourLines.setEnabled(True)
            self.dlg.doubleSpinBox_contourLines.setEnabled(True)
            self.dlg.label_gdal_contour.setEnabled(True)
            self.dlg.lineEdit_gdal_contour.setEnabled(True)
            self.dlg.pushButton_gdal_contour.setEnabled(True)
        else:
            self.dlg.label_contourLines.setEnabled(False)
            self.dlg.doubleSpinBox_contourLines.setEnabled(False)
            self.dlg.label_gdal_contour.setEnabled(False)
            self.dlg.lineEdit_gdal_contour.setEnabled(False)
            self.dlg.pushButton_gdal_contour.setEnabled(False)
