import os
import argparse
import numpy as np
import tensorflow as tf
from PIL import Image
import scipy.misc
import glob
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util




class CarsCropper():
    def __init__(self):
        CWD_PATH        = os.getcwd()

        # Path to frozen detection graph. This is the actual model that is used for the object detection.
        MODEL_NAME      = 'ssd_mobilenet_v1_coco_11_06_2017'
        PATH_TO_CKPT    = os.path.join(CWD_PATH, 'object_detection', MODEL_NAME, 'frozen_inference_graph.pb')

        # List of the strings that is used to add correct label for each box.
        PATH_TO_LABELS  = os.path.join(CWD_PATH, 'object_detection', 'data', 'mscoco_label_map.pbtxt')

        NUM_CLASSES     = 90
        # Loading label map
        label_map       = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories      = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,use_display_name=True)
        category_index  = label_map_util.create_category_index(categories)

        self.detection_graph = tf.Graph()

        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

    @staticmethod
    def load_image_into_numpy_array(image):
        (im_width, im_height) = image.size
        return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)

    @staticmethod
    def check_folder(path_to_folders, extention):
        cv_img = []
        path = path_to_folders
        for img in glob.glob("{}/*.{}".format(path, extention)):
            cv_img.append(img)
        return cv_img

    def __call__(self, path_to_images_dir = 'test_images'):
        # If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
        PATH_TO_IMAGES_DIR      = path_to_images_dir
        TEST_IMAGE_PATHS        = CarsCropper.check_folder(PATH_TO_IMAGES_DIR, 'jpg') #[os.path.join(PATH_TO_TEST_IMAGES_DIR, 'image{}.jpg'.format(i)) for i in range(1, 7) ]
        counter                 = 0

        with self.detection_graph.as_default():
            with tf.Session(graph=self.detection_graph) as sess:
                for image_path in TEST_IMAGE_PATHS:
                    print('1.- Creaing Inference .... IMAGE to feed IS:', image_path)
                    image               = Image.open(image_path)
                    # the array based representation of the image will be used later in order to prepare the
                    # result image with boxes and labels on it.
                    image_np            = CarsCropper.load_image_into_numpy_array(image)
                    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                    image_np_expanded   = np.expand_dims(image_np, axis=0)
                    image_tensor        = self.detection_graph.get_tensor_by_name('image_tensor:0')
                    # Each box represents a part of the image where a particular object was detected.
                    boxes               = self.detection_graph.get_tensor_by_name('detection_boxes:0')
                    # Each score represent how level of confidence for each of the objects.
                    # Score is shown on the result image, together with the class label.
                    scores              = self.detection_graph.get_tensor_by_name('detection_scores:0')
                    classes             = self.detection_graph.get_tensor_by_name('detection_classes:0')
                    num_detections      = self.detection_graph.get_tensor_by_name('num_detections:0')
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
                                A       = (x1 - x0) * (y1 - y0)
                                punto_1 = (x0,y0)
                                punto_2 = (x1,y1)
                                caja    = [punto_1, punto_2]
                                if A > 80000:
                                    areas.append(A)
                                    bounding.append(caja)
                                else:
                                    pass
                    info = dict(zip(areas, bounding))
                    if len(info) > 0:
                        # Get the maximun area box
                        max_key = max(info, key=info.get)

                        cajita = info[max_key]
                        punto_a, punto_b = cajita[0], cajita[1]
                        
                        x0 = punto_a[0]
                        y0 = punto_a[1]

                        x1 = punto_b[0]
                        y1 = punto_b[1]

                        imagen_cropped  = image_np[y1:y0, x1:x0]

                        image_name      = image_path.split('/')[-1][-6:-4]
                        imagen_path     = PATH_TO_IMAGES_DIR+'/croped_from_{}.png'.format(image_name)
                        print('###### 2.- Saving image in....:', imagen_path)
                        scipy.misc.imsave(imagen_path, imagen_cropped)
                    else:
                        print('>>>>>> 3.- EMPTY IMAGE, passinng...')


class GetFolders():

    def __call__(self, work_in_folder):
        path_to_work_folder = os.getenv('HOME') + '/' + work_in_folder  + '/*'

        """
            Get a list of the clean folders (usefull)
            , folders with jpg's and avi in folder
        """
        folders_to_clean = []
        total_folders = []
        files = glob.glob(path_to_work_folder)
        for folder in files:
            total_folders.append(folder)
        return total_folders


if __name__ == '__main__':
    folders_caller  = GetFolders()
    cars_cropper    = CarsCropper()
    
    folders_to_work = folders_caller('red')
    for folder in folders_to_work:
        print(folder)
        cars_cropper(path_to_images_dir = folder)
