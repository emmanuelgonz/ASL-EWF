import fire
from skimage.io import imread, imsave
from skimage.color import grey2rgb,rgb2grey
from ModifyImageColors import fix_noise
from keras.models import load_model
from whole_field_test import evaluate_whole_field, draw_boxes
import os
import numpy as np
from PIL import Image
from create_individual_lettuce_train_data import fix_noise_vetcorised
from contours_test import create_quadrant_image
from size_calculator import calculate_sizes, create_for_contours
import matplotlib.pyplot as plt

def whole_pipe(dir1, name):
    #img_dir = /home/emmanuelgonzalez/AirSurf-Lettuce/testing_images/medium_grey_conv.png
    #dir1 = 'Z:/1 - Projects/AirSurf/Gs_Growers/'
    #dir1 = '/home/emmanuelgonzalez/AirSurf-Lettuce/testing_images/'
    #name = 'normans_cropped'
    #name = 'medium_grey_conv'
    #name = 'peacock_cropped'
    #name = 'bottom_field_cropped'
    #name = 'top_field_cropped'
    Image.MAX_IMAGE_PIXELS = None
    output_name = 'data/'+ name +'.png'
    if not os.path.exists(output_name):
        img = imread(dir1 + name + '.png')
        #img1 = fix_noise_vetcorised(img)
        img1 = img
        imsave(output_name, img1)
    else:
        img1 = imread(output_name)

    plt.imshow(img1)
    plt.show()

    loaded_model = load_model('../model/trained_model_new2.h5')

    #create dir.
    if not os.path.exists(name):
        os.mkdir(name)
    else:
        boxes = np.load(name + "/boxes.npy")
        imsave(name + "_lettuce_count_" + str(boxes.shape[0]) + ".png",draw_boxes(grey2rgb(img1), boxes, color=(255, 0, 0)))

    print("evaluating field")

    evaluate_whole_field(name, img1, loaded_model)
    boxes = np.load(name + "/boxes.npy").astype("int")

    print("calculating sizes")

    labels, size_labels = calculate_sizes(boxes, img1)

    label_output = []
    for label in labels:
        label_output.append(size_labels[label])

    np.save(name+"/size_labels.npy",np.array(label_output))

    import colorsys
    def hsv2rgb(h, s, v):
        return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

    unique_elements, count_elements = np.unique(labels, return_counts=True)
    N = unique_elements.shape[0]
    #HSV_tuples = [(x * 1.0 / N, 0.5, 0.5) for x in range(N - 1, -1, -1)]  # blue,green,red
    #RGB_tuples = np.array(list(map(lambda x: hsv2rgb(*x), HSV_tuples)))
    RGB_tuples = [[0,0,255],[0,255,0],[255,0,0]]
    color_field = create_for_contours(name, img1, boxes, labels, size_labels, RGB_tuples=RGB_tuples)

    #create the output file.


    #create quadrant harvest region image.
    create_quadrant_image(name, color_field)

if __name__ == '__main__':
    fire.Fire()