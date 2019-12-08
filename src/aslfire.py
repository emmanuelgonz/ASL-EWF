import fire
import keras 
from skimage.io import imread, imsave
from skimage.color import rgb2grey
from skimage.transform import resize, rescale, pyramid_expand
from ModifyImageColors import fix_noise
from keras.models import load_model
from whole_field_test import extract_region, evaluate_whole_field, draw_boxes
import os
import numpy as np
from PIL import Image, ImageTk
from create_individual_lettuce_train_data import get_channel_with_greatest_intensity
from contours_test import create_quadrant_image
from size_calculator import calculate_sizes, create_for_contours
import matplotlib.pyplot as plt
from threading import Thread
import cv2
from test_model import sliding_window_count_simple, non_max_suppression_fast, draw_boxes, sliding_window_count_vectorised
from skimage.color import grey2rgb

def fix_noise(img):
    ndvi_channel = get_channel_with_greatest_intensity(img)
    # create single channel image (gray) from NDVI channel
    img = img[:, :, ndvi_channel]
    h, w = img.shape[:2]
    inverted_img = cv2.bitwise_not(img)
    ret1, th = cv2.threshold(inverted_img, 180, 255, cv2.THRESH_BINARY)
    _, contours, _ = cv2.findContours(th.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = []
    for contour in contours:
        if cv2.contourArea(contour) < 200:
            rect = cv2.minAreaRect(contour)
            _, (cw, ch), angle = rect
            if cw > 0 and ch > 0:
                aspect_ratio = float(cw) / float(ch)
                aspect_diff = abs(1.0 - aspect_ratio)
                if aspect_diff <= 0.5:
                    filtered_contours.append(contour)

    clahe = cv2.createCLAHE(clipLimit=5, tileGridSize=(11, 11))

    if len(filtered_contours) >= 5 or len(contours) >= 5:
        mask = np.zeros((h, w), np.uint8)
        cv2.drawContours(mask, filtered_contours, -1, (255), -1)
        shift = get_percentile_intensity_in_mask_img(img, mask, 99.9) * 1.2
        shifted_img = (img - shift) % 255
        shifted_img = shifted_img.astype(np.uint8)
        return gray_2_rgb(clahe.apply(shifted_img))
    return gray_2_rgb(clahe.apply(img))


def fix_noise_vetcorised(img):
    #ndvi_channel = get_channel_with_greatest_intensity(img)
    ndvi_channel = Image.open(img)
    # create single channel image (gray) from NDVI channel
    #img = img[:, :, ndvi_channel]
    img = img[:, :, 0]
    #h, w = img.shape[:2]
    h, w = img.shape[2]
    inverted_img = cv2.bitwise_not(img)
    ret1, th = cv2.threshold(inverted_img, 180, 255, cv2.THRESH_BINARY)
    #_, contours, _ = cv2.findContours(th.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours, _ = cv2.findContours(th.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_areas = np.array([cv2.contourArea(contour) for contour in contours])
    filtered_contours = [contours[idx[0]] for idx in np.argwhere(contour_areas < 180)] #not ideal. but converting to a numpy array breaks cv2
    contour_rects = np.array([cv2.minAreaRect(contour)[1] for contour in filtered_contours], dtype=np.float32)
    aspect_diff = np.abs(np.ones(contour_rects[:,0].shape) - contour_rects[:,0] / contour_rects[:,1])
    filtered_contours = [filtered_contours[idx[0]] for idx in np.argwhere(aspect_diff <= 0.5)] #not ideal. but converting to a numpy array breaks cv2
    clahe = cv2.createCLAHE(clipLimit=5, tileGridSize=(5, 5))

    if len(filtered_contours) >= 5 or len(contours) >= 5:
        mask = np.zeros((h, w), np.uint8)
        cv2.drawContours(mask, filtered_contours, -1, 255, -1)
        shift = get_percentile_intensity_in_mask_img(img, mask, 99.9) * 1.2
        shifted_img = (img - shift) % 255
        shifted_img = shifted_img.astype(np.uint8)
        return gray_2_rgb(clahe.apply(shifted_img))
    return gray_2_rgb(clahe.apply(img))


def evaluate_whole_field(output_dir, field, model, l=250, stride=5, prune=True):
    #img = Image.open(str(field))
    #run through the image cutting off 1k squres.
    box_length = 20
    h, w = field.shape[:2]
    #h, w = img.shape[:2]

    ##load the main three variables.
    start = np.array([0,0])
    if os.path.exists(output_dir+"loop_vars.npy"):
        start = np.load(output_dir+"loop_vars.npy")

    boxes = None
    if os.path.exists(output_dir+"boxes.npy"):
       boxes = np.load(output_dir+"boxes.npy")
    else:
        boxes = np.zeros((1, 4))

    probs = None
    if os.path.exists(output_dir+"probs.npy"):
        probs = np.load(output_dir+"probs.npy")
    else:
        probs = np.zeros((1))

    #we take off box length in case of an overlap.
    for x in range(start[0], h, l-box_length):
        for y in range(start[1], w, l-box_length):
            print("%d, %d" % (x,y))

            # Prevent doing all this work for all black squares
            #if np.max(img[x:x+l,y:y+l]) == 0:
            if np.max(field[x:x+l,y:y+l]) == 0:
                continue

            np.save(output_dir+"loop_vars.npy", np.array([x, y]))

            #box, prob = extract_region(img, model, x, y, l, box_length, stride, threshold=0.90, prune=prune)
            box, prob = extract_region(field, model, x, y, l, box_length, stride, threshold=0.90, prune=prune)

            if len(box) is not 0:
                boxes = np.vstack((boxes,box))
                probs = np.hstack((probs,prob))

            #save the values for loading.
            np.save(output_dir+"boxes.npy", boxes)
            np.save(output_dir+"probs.npy", probs)

        start = np.array([x, 0])
        np.save(output_dir+"loop_vars.npy", start)

    #set the loop vars to done.
    np.save(output_dir + "loop_vars.npy", np.array([h, w]))

    ##prune the overlapping boxes.
    if not prune:
        boxes, probs = non_max_suppression_fast(boxes, probs, 0.18)
        np.save(output_dir + "pruned_boxes.npy", boxes)
        np.save(output_dir + "pruned_probs.npy", probs)
        print(boxes.shape)
    #imsave(name+"_lettuce_count_" + str(boxes.shape[0]) + ".png", draw_boxes(grey2rgb(img), boxes, color=(255,0,0)))
    imsave(name+"_lettuce_count_" + str(boxes.shape[0]) + ".png", draw_boxes(grey2rgb(field), boxes, color=(255,0,0)))


if __name__ == '__main__':
    fire.Fire()


    




