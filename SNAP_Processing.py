#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import sys
# sys.path.append('/gpfs/data1/cmongp/Rajesh/.conda/envs/sn/lib/python3.6/site-packages')
import os
import datetime
import gc
import glob
import snappy
from sentinelsat import SentinelAPI, geojson_to_wkt, read_geojson
from snappy import ProductIO
from snappy import WKTReader

import tqdm
import shapefile
import pygeoif



# Initialize snap

snappy.GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
# HashMap Key-Value pairs
HashMap = snappy.jpy.get_type('java.util.HashMap')


# Helper functions

def orbit_file(img):
    parameters = HashMap()
    parameters.put('Apply-Orbit-File', True)
    parameters.put('polyDegree','3')
    parameters.put('orbitType','Sentinel Precise (Auto Download)')
    parameters.put('continueOnFail', True)
    orbit_param = snappy.GPF.createProduct("Apply-Orbit-File", parameters, img)
    print("Done orbitting.")
    return orbit_param

def subset_file(img,r):
    g=[]
    for s in r.shapes():
        g.append(pygeoif.geometry.as_shape(s))
    m = pygeoif.MultiPoint(g)
    wkt = str(m.wkt).replace("MULTIPOINT", "POLYGON(") + ")"
    SubsetOp = snappy.jpy.get_type('org.esa.snap.core.gpf.common.SubsetOp')
    bounding_wkt = wkt
    geometry = WKTReader().read(bounding_wkt)
    parameters = HashMap()
    parameters.put('copyMetadata', True)
    parameters.put('geoRegion', geometry)
    product_subset = snappy.GPF.createProduct('Subset', parameters, img)
    return product_subset

def thermal_noise(img):
    parameters = HashMap()
    parameters.put('removeThermalNoise', True)
    parameters.put('reIntroduceThermalNoise', False)
    thermal = snappy.GPF.createProduct("ThermalNoiseRemoval", parameters, img)
    print("Done thermal noise.")
    return thermal

def calibration(img):
    parameters = HashMap()
    parameters.put('outputSigmaBand', True)
    parameters.put('outputGammaBand', False)
    parameters.put('outputBetaBand', False)
    parameters.put('sourceBands', 'Intensity_VH,Intensity_VV')
    parameters.put('selectedPolarisations', 'VH,VV')
    parameters.put('outputImageScaleInDb', False)
    output = snappy.GPF.createProduct("Calibration", parameters, img)
    print("Done caliberation")
    return output

def multilook(img):
    parameters = HashMap()
    parameters.put('sourceBands', 'Sigma0_VH,Sigma0_VV')
    parameters.put('grSquarePixel', True)
    parameters.put('nRgLooks', 3)
    parameters.put('nAzLooks', 3)
    parameters.put('outputIntensity', True)
    multi_param = snappy.GPF.createProduct("Multilook", parameters, img)
    print("Done Multilook.")
    return multi_param

def speckle_filter(img):
    parameters = HashMap()
    parameters.put('sourceBands', 'Sigma0_VH,Sigma0_VV')
    parameters.put('filter', 'Lee')
    parameters.put('filterSizeX', 5)
    parameters.put('filterSizeY', 5)
    parameters.put('dampingFactor', '2')
    parameters.put('estimateENL', 'true')
    parameters.put('enl', '1.0')
    parameters.put('numLooksStr', '1')
    parameters.put('targetWindowSizeStr', '3x3')
    parameters.put('sigmaStr', '0.9')
    parameters.put('anSize', '50')
    output = snappy.GPF.createProduct('Speckle-Filter', parameters, img)
    print("Done Speckle.")
    return output

def terrain_correction(img):
    parameters = HashMap()
    parameters.put('sourceBands', 'Sigma0_VH,Sigma0_VV')
    parameters.put('demName', 'SRTM 1Sec HGT')
    parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('pixelSpacingInMeter', '30.0')
    parameters.put('saveSelectedSourceBand', True)
    parameters.put('saveDEM', False)
    output = snappy.GPF.createProduct('Terrain-Correction', parameters, img)
    print("Done terrain.")
    return output

def linear_db(img):
    parameters = HashMap()
    parameters.put('sourceBands', 'Sigma0_VH,Sigma0_VV')
    lineartodb = snappy.GPF.createProduct('linearToFromdB', parameters, img)
    print("Done Linear2db.")
    return lineartodb

def AddElevationBand(img):
    parameters = HashMap()
    parameters.put('demName', 'SRTM 1Sec HGT')
    parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
    elevation = snappy.GPF.createProduct('AddElevation', parameters, img)
    print("Added elevation band")
    return elevation


# In[4]:

def main():
    # Create a dictionary to store raw_images by their name
    sentinel_images_dict = {}
    # Read shapefile
    shp = shapefile.Reader("shapefiles/NewStudy.shp")
    # Src and Dest path
    year = '2019'
    raw_img_path = "raw_images/"+year+"/"
    dest_path = "SNAP_processed/"+year+"/"
    # if dest_path does not exist, create it
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
        
    # Load images in decit
    for filepath in sorted(glob.iglob(raw_img_path + "*.zip"))[1000:]:
        sentinel_images_dict[str(os.path.split(filepath)[-1][:32])] = ProductIO.readProduct(filepath)
    # For every image
    for name,img in tqdm.tqdm(sentinel_images_dict.items()):
        print(name)
        a = datetime.datetime.now().replace(microsecond=0)
        # Download the orbit file
        orbit = orbit_file(img)
        # Cut the region to shape file
        subset = subset_file(orbit,shp)
        # Remove thermal noise
        thermal = thermal_noise(subset)
        # Do caliberation
        calib = calibration(thermal)
        # Multilook
        multi = multilook(calib)
        # Speckle filtering
        speckle = speckle_filter(multi)
        #Terrain correction
        terrain = terrain_correction(speckle)
        # convert to db
        db_img = linear_db(terrain)
        # add elevation band
        final = AddElevationBand(db_img)
        # Write to dest as geotiff
        ProductIO.writeProduct(final,dest_path+str(name), 'GeoTIFF')
        b = datetime.datetime.now().replace(microsecond=0)
        print(b-a)

if __name__ == "__main__":
    main()

