#!/usr/bin/env python3
"""
Author: Emmanuel Gonzalez
Purpose: Generate a triangular greeness index index (TGI) tif from an orthomosaic
"""
import rasterio
import numpy
import fire
import os

def tgi(ifile):
    # Load red and NIR bands - note all PlanetScope 4-band images have band order BGRN
    path_out = os.path.splitext(os.path.basename(ifile))[0]
    with rasterio.open(ifile) as src:
        r_band = src.read(1)
        g_band = src.read(2)
        b_band = src.read(3)
    
    # Calculate triangular greeness index: g - 0.39*r - 0.61*b
    tgi = (g_band.astype(float)-(0.39*r_band.astype(float))-(0.61*b_band.astype(float)))

    # Set spatial characteristics of the output object to mirror the input
    kwargs = src.meta
    kwargs.update(
        dtype=rasterio.float32,
        count = 1)

    # Create the file
    with rasterio.open(path_out + '_tgi.tif', 'w', **kwargs) as dst:
            dst.write_band(1, tgi.astype(rasterio.float32))

if __name__ == "__main__":
    fire.Fire(tgi)
