import fire
import glob
import os
import cv2
import numpy as np
from scipy import ndimage
from skimage.io import imread, imsave
from skimage.measure import label, regionprops
from skimage.transform import resize
from PIL import Image

def get_percentile_intensity_in_mask_img(img, mask, percentile, max_intensity=220):
    values = img[np.nonzero(mask)]
    values = values[values <= max_intensity]
    mean = np.mean(values)
    std = np.std(values)
    values = values[abs(values - mean) < 4 * std]
    if len(values) > 0:
        return np.percentile(values, percentile)
    return 0.0

def get_channel_with_greatest_intensity(img):
    # flatten each channel to a single dimension and get the maximum value in each
    c0 = max(img[:, :, 0].flatten())
    #c0 = max(img[0, 0, 0].flatten())
    c1 = max(img[:, :, 1].flatten())
    #c1 = max(img[0, 0, 1].flatten())
    c2 = max(img[:, :,2].flatten())
    #c2 = max(img[0, 0, 2].flatten())
    # if the first channel has the greatest pixel value then return channel 0
    if c0 > c1 and c0 > c2:
        return 0
    # if the second channel has the greatest pixel value then return channel 1
    if c1 > c0 and c1 > c2:
        return 1
    # if the third channel has the greatest pixel value then return channel 2
    if c2 > c0 and c2 > c1:
        return 2
    # otherwise no one channel contain the greatest pixel value: return -1 to represent this
    return -1

def gray_2_rgb(gray_img):
    # copy the image
    channel = gray_img.copy()
    # get the image dimensions
    h, w = gray_img.shape[:2]
    # create new 3 channel image that of same width and height
    img = np.zeros((h, w, 3), np.uint8)
    # copy gray information to each channel of the new image
    img[:, :, 0] = channel
    img[:, :, 1] = channel
    img[:, :, 2] = channel
    # return the 3 channel image
    return img

def fix_noise_vetcorised(img):
    ndvi_channel = get_channel_with_greatest_intensity(img)
    #ndvi_channel = Image.open(img)
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

if __name__ == '__main__':
    fire.Fire()


    




