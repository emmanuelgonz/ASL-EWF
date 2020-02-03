#!/usr/bin/env python3

import fire
from skimage.io import imread, imsave, imshow, show
from skimage.color import grey2rgb
from skimage.transform import resize, rescale, pyramid_expand
import keras
from PIL import Image
from keras.models import load_model
from whole_field_test import evaluate_whole_field, draw_boxes
import numpy as np
from create_individual_lettuce_train_data import fix_noise_vetcorised
from contours_test import create_quadrant_image
from size_calculator import calculate_sizes, create_for_contours
import matplotlib.pyplot as plt
from threading import Thread
import time
#from construct_quadrant_file import create_quadrant_file
from aslsizefile import create_quadrant_file
import os
#os.environ['KMP_DUPLICATE_LIB_OK'] ='True' # This prevents a crash from improperly loading a GPU library, but prevents using it I think. Comment out to see if it will work on your machine
from zipfile import ZipFile
import _thread
from shutil import copy2
import imageio
import io
import tensorflow as tf
import sys
import timeit
#from crop_raster import crop
#from tgi_new import tgi

tf.config.optimizer.set_jit(True)
start = timeit.default_timer()

def run_pipeline(filename):
    #image = Image.open(filename)
    #filename = image.resize((200,200), Image.ANTIALIAS)
    lat = float(33.076486)
    long = float(-111.975091)
    rot = float(0.0)

    name = os.path.splitext(os.path.basename(filename))[0] + "_m1"
    print("Filename: " + name)
    output_dir = "../data/" + name + "/"
    print("Output directory: " + output_dir)
    Image.MAX_IMAGE_PIXELS = None
    output_name = output_dir + "grey_conversion.png"
    print("Output file:" + output_name)
    
    """
    # Load image  
    if os.path.isfile(filename):
        src_image = imread(filename).astype(np.uint8)
        img_width = src_image.shape[1]
        img_height = src_image.shape[0]
        print(src_image.shape) 
        if len(src_image.shape) == 2:
            src_image = grey2rgb(src_image)
        else:
            src_image = src_image[:,:,:3]
    """
    if not os.path.exists(output_name):
        img1 = imread(filename)
        img_width = img1.shape[1]
        img_height = img1.shape[0]
        #img1 = fix_noise_vetcorised(src_image)

        # create dir.
        if not os.path.exists("../data"):
            os.mkdir("../data")

        if not os.path.exists("../data/" + name):
            os.mkdir("../data/" + name)
        imsave(output_name, img1)
    else:
        img1 = imread(output_name)#.astype(np.uint8)[:,:,3]

    #Evaluates field for lettuce
    print("Evaluating Field")
    keras.backend.clear_session()
    model = "../model/trained_model_new.h5"
    loaded_model = load_model(model)
    evaluate_whole_field(output_dir, img1, loaded_model)
    boxes = np.load(output_dir + "boxes.npy").astype("int")
    im = draw_boxes(grey2rgb(img1.copy()), boxes, color=(255, 0, 0))
    imsave(output_dir + "counts.png", im)

    #Calculates sizes of identified lettuces
    print("Calculating Sizes")
    labels, size_labels = calculate_sizes(boxes, img1)
    label_ouput= np.array([size_labels[label] for label in labels])
    np.save(output_dir + "size_labels.npy", label_ouput)
    RGB_tuples = [[0, 0, 255], [0, 255, 0], [255, 0, 0]]
    color_field = create_for_contours(name, img1, boxes, labels, size_labels, RGB_tuples=RGB_tuples)
    imsave(output_dir + "sizes.png", color_field)

    # create quadrant harvest region image.
    output_field = create_quadrant_image(name, color_field)
    im = Image.fromarray(output_field.astype(np.uint8), mode="RGB")
    im = im.resize((img_width, img_height))
    im = np.array(im.getdata(), np.uint8).reshape(img_height, img_width,3)
    imsave(output_dir + "harvest_regions.png", im)

    #make the csv file.
    #name = 'grey_conversion'
    #create_quadrant_file(output_dir, name, img_height, img_width, boxes, label_ouput, lat, long, rot, region_size=230)
    output_dir = '../data/' + name + '/'
    name2 = os.path.splitext(os.path.basename(output_name))[0]
    create_quadrant_file(output_dir, name2, name)
    #pipeline_thread = None
    
    #Time the process
    stop = timeit.default_timer()
    total_time = stop - start 
    mins, secs = divmod(total_time, 60)
    hours, mins = divmod(mins, 60)
    sys.stdout.write("Processing complete. Total running time: %d:%d:%d.\n" % (hours, mins, secs))
    #print("Process Complete. Pipeline analysis has completed.")

if __name__ == '__main__':
    fire.Fire(run_pipeline)
