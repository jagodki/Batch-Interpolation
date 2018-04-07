import qgis.core
from qgis.analysis import QgsInterpolator, QgsTINInterpolator, QgsIDWInterpolator, QgsGridFileWriter
from PyQt4.QtCore import QDir
import os

class Interpolation():
    
    def __ini__(self):
        self.test = test
    
    def interpolation(self, layer, attribute_for_interpolation, attribute_name, method, output_dir, resolution):
        #create interpolation-object
        layer_data = QgsInterpolator.LayerData()
        
        #add the given layer to the interpolation-object
        layer_data.vectorLayer = layer
        
        #use the given attribute instead of the z coordinate for interpolation
        layer_data.zCoordInterpolation=False
        layer_data.interpolationAttribute = attribute_for_interpolation
        print(attribute_for_interpolation)
        layer_data.mInputType = 1
        
        #interpolate the layer
        interpolator = None
        if method == "TIN":
            interpolator = QgsTINInterpolator([layer_data])
        else:
            interpolator = QgsIDWInterpolator([layer_data])
        
        #create the resulting raster
        rect = layer.extent()
        ncol = int((rect.xMaximum() - rect.xMinimum()) / resolution)
        nrows = int((rect.yMaximum() - rect.yMinimum()) / resolution)
        
        #create outut directory
        export_folder = QDir.toNativeSeparators(output_dir + "/batch_interpolation/")
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)
        
        #write raster to file system
        export_path = QDir.toNativeSeparators(export_folder + layer.name() + "_" + attribute_name + ".asc")
        output = QgsGridFileWriter(interpolator, export_path, rect, ncol, nrows, resolution, resolution)
        output.writeFile(True)
    
    def contour(self, filename, attr_name, intervall, input, output):
        #create output directoy
        export_folder = QDir.toNativeSeparators(output_dir + "/batch_contour/")
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)
        
        export_path = QDir.toNativeSeparators(export_folder + filename + ".shp")
        command = "gdal_contour -a " + attr_name + " -i " + intervall + " " + input + " " + output
        os.system(command)
    
