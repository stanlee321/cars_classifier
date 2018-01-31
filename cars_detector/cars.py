import os
import argparse
import numpy as np
import tensorflow as tf
from PIL import Image
import scipy.misc
import cv2
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util



CWD_PATH = os.getcwd()

# Path to frozen detection graph. This is the actual model that is used for the object detection.
MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
PATH_TO_CKPT = os.path.join(CWD_PATH, 'object_detection', MODEL_NAME, 'frozen_inference_graph.pb')

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join(CWD_PATH, 'object_detection', 'data', 'mscoco_label_map.pbtxt')

NUM_CLASSES = 90

# Loading label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,use_display_name=True)
category_index = label_map_util.create_category_index(categories)

def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)


detection_graph = tf.Graph()

with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')



# For the sake of simplicity we will use only 2 images:
# If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
PATH_TO_TEST_IMAGES_DIR = 'test_images'
TEST_IMAGE_PATHS = [os.path.join(PATH_TO_TEST_IMAGES_DIR, 'image{}.jpg'.format(i)) for i in range(1, 7) ]

# Size, in inches, of the output images.
IMAGE_SIZE = (12, 8)
counter = 0

with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        for image_path in TEST_IMAGE_PATHS:
            print('IMAGE IS', image_path)
            image = Image.open(image_path)
            # the array based representation of the image will be used later in order to prepare the
            # result image with boxes and labels on it.
            image_np = load_image_into_numpy_array(image)
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            # Each box represents a part of the image where a particular object was detected.
            boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            scores = detection_graph.get_tensor_by_name('detection_scores:0')
            classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')
            # Actual detection.
            (boxes, scores, classes, num_detections) = sess.run([boxes, scores, classes, num_detections],feed_dict={image_tensor: image_np_expanded})

            areas = []
            bounding = []
            for i,b in enumerate(boxes[0]):
                #        person  1       car    3                bus   6               truck   8
                if classes[0][i] == 3 or classes[0][i] == 6 or classes[0][i] == 8:
                    if scores[0][i] >= 0.6:
    
                        x0 = int(boxes[0][i][3]*image_np.shape[1])
                        y0 = int(boxes[0][i][2]*image_np.shape[0])

                        x1 = int(boxes[0][i][1]*image_np.shape[1])
                        y1 = int(boxes[0][i][0]*image_np.shape[0])

                        #area
                        A = (x1 - x0) * (y1 - y0)
                        punto_1 = (x0,y0)
                        punto_2 = (x1,y1)
                        caja = [punto_1, punto_2]

                        areas.append(A)
                        bounding.append(caja)

            try:
                info = dict(zip(areas, bounding))
                max_key = max(info, key=info.get)

                cajita = info[max_key]
                punto_a, punto_b = cajita[0], cajita[1]
                
                x0 = punto_a[0]
                y0 = punto_a[1]

                x1 = punto_b[0]
                y1 = punto_b[1]

                imagen_cropped = image_np[y1:y0, x1:x0]

                counter +=1
                image_name = image_path.split('/')[-1][0:-4] + '_{}'.format(counter)
                imagen_path = PATH_TO_TEST_IMAGES_DIR+'/{}.jpg'.format(image_name)
                print('IMAGE path IS', imagen_path)
                scipy.misc.imsave(imagen_path, imagen_cropped)
                #cv2.imwrite(imagen_path, imagen_cropped)
            except:
                print('EMPTY IMAGE, passinng')