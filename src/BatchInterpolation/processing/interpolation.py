import qgis.core
import qgis.analysis
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
        layer_data.mInputType = 1
        
        #interpolate the layer
        interpolator = None
        if method == "TIN":
            interpolator = QgsTINInterpolator([layer_data])
        else:
            interpolator = QgsIDWInterpolator([layer_data])
        
        #create the resulting raster
        export_path = QDir.toNativeSeparators(output_dir + "/batch_interpolation/" + layer.name() + "_" + attribute_name + ".asc")
        rect = layer.extent()
        ncol = int((rect.xMaximum() - rect.xMinimum()) / resolution)
        nrows = int((rect.yMaximum() - rect.yMinimum()) / resolution)
        
        #write raster to file system
        output = QgsGridFileWriter(interpolator, export_path, rect, ncol, nrows, res, res)
        output.writeFile(True)
    
    def contour(self, filename, attr_name, intervall, input, output):
        export_path = QDir.toNativeSeparators(output_dir + "/batch_contour/" + filename + ".shp")
        command = "gdal_contour -a " + attr_name + " -i " + intervall + " " + input + " " + output
        os.system(command)
    
