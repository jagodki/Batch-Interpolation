from interpolation import Interpolation
import glob
from PyQt4.QtGui import QComboBox, QProgressBar, QTableWidget, QTableWidgetItem
from os import path

class Controller():
    
    def __init__(self):
        self.interpolation = Interpolation()
        self.layers = []
    
    def populate_layer_list(self, iface, combobox):
        #populate the instance variable
        self.layers = [""]
        self.layers = iface.legendInterface().layers()
        
        #populate the combobox
        for layer in self.layers:
            combobox.addItem(layer.name())
    
    def populate_attribute_list(self, layername, table):
        #clear the table
        table.clearSpans()
        
        #find the selected layer
        for layer in self.layers:
            if layer.name() == layername:
                #get all fields/attributes of the selected layer
                fields = layer.pendingFields()
                fieldnames = [field.name() for field in fields]
                
                #populate the table
                for fieldname in fieldnames:
                    current_row = self.table.rowCount()
                    table.insertRow(current_row)
                    table.setRowCount(current_row + 1)
                    table.setItem(current_row, 0, QTableWidgetItem(fieldname))
                
                break
    
    def start_batch_process(self, table, layer, attribute, interpolation_method, contour, out_dir, resolution, intervall, pb):
        #init the progressbar
        pb.setValue(0)
        if contour:
            pb.setMaximum(2 * len(table.selectionModel().selectedRows()))
        else:
            pb.setMaximum(len(table.selectionModel().selectedRows()))
        
        #iterate over the selected rows
        for row in table.selectionModel().selectedRows():
            #get the index of the attribute
            attr_index = 0
            for field in layer.pendingFields():
                if field == attribute:
                    break
                attr_index += 1
            
            #interpolate the layer with the current attribute
            self.interpolation.interpolation(layer, attr_index, attribute, interpolation_method, out_dir, resolution)
            pb.setValue(pb.getValue() + 1)
        
        #create contour lines
        if contour:
            for file in glob.glob(QDir.toNativeSeparators(out_dir + "/batch_interpolation/*.asc")):
                self.interpolation.contour(path.basename(file), attribute, intervall, file, out_dir)
                pb.setValue(pb.getValue() + 1)
