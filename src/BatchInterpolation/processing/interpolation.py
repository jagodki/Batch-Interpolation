import qgis.core
from qgis.analysis import QgsInterpolator, QgsTINInterpolator, QgsIDWInterpolator, QgsGridFileWriter
from PyQt4.QtCore import QDir
import os
import subprocess

class Interpolation():
    
    def __ini__(self):
        self.test = test
    
    def interpolation(self, iface, layer, attribute_for_interpolation, attribute_name, method, output_dir, resolution, clip, path_to_gdalwarp, mask_layer):
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
        
        #clip the raster
        if clip:
            #get the layer using he layer name
            mask = ""
            for layer in iface.legendInterface().layers():
                if layer.name() == mask_layer:
                    mask = layer
            
            clipped_path = QDir.toNativeSeparators(export_folder + layer.name() + "_" + attribute_name + "_clipped" + ".tiff")
            command = [path_to_gdalwarp, "-ot", "Float32", "-q", "-of", "GTiff", "-cutline", mask.dataProvider().dataSourceUri(), "-co", "COMPRESS=DEFLATE", "-co", "PREDICTOR=1", "-co", "ZLEVEL=6", "-wo", "OPTIMIZE_SIZE=TRUE", export_path, clipped_path]
            subprocess.call(command)
    
    def contour(self, gdal_contour_dir, filename, attr_name, intervall, input, output):
        #create output directoy
        export_folder = QDir.toNativeSeparators(output + "/batch_contour/")
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)
        
        export_path = QDir.toNativeSeparators(export_folder + filename + ".geojson")
        command = [gdal_contour_dir, "-a", attr_name, "-i", str(intervall), "-f", "GeoJSON", input, export_path]
        subprocess.call(command)
    
