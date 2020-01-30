#!/usr/bin/env python3
"""
Author: Emmanuel Gonzalez
References: Earth Data Science 
Purpose: Use shapefile to crop a tif image
"""
import fire
import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio.plot import plotting_extent
from rasterio.mask import mask
from shapely.geometry import mapping
import geopandas as gpd
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep
import seaborn as sns
#sns.set(font_scale=1.5)

def crop(sf, tf):
    # Prettier plotting with seaborn
    sns.set(font_scale=1.5)
    path_out = os.path.splitext(os.path.basename(tf))[0] + "_cropped.tif"
    # Set working directory
    #os.chdir('~')

    # Open crop extent (your study area extent boundary)
    crop_extent = gpd.read_file(sf)
    print('Crop extent CRS: ', crop_extent.crs)
   
    #Crop the file 
    with rio.open(tf) as tf:
        print('Tif crs: ', tf.crs)
        tf_crop, tf_crop_meta = es.crop_image(tf, crop_extent)

    tf_crop_affine = tf_crop_meta["transform"]

    # Create spatial plotting extent for the cropped layer
    tf_extent = plotting_extent(tf_crop[0], tf_crop_affine)
    
    # Update with the new cropped affine info and the new width and height
    tf_crop_meta.update({'transform': tf_crop_affine,
                         'height': tf_crop.shape[1],
                         'width': tf_crop.shape[2]})
                         #'nodata':0})
    tf_crop_meta
    print(tf_crop_meta)

    # Write data
    with rio.open(path_out, 'w', **tf_crop_meta) as ff:
        ff.write(tf_crop[0], 1)

if __name__ == "__main__":
    fire.Fire(crop)