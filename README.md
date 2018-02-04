# Cars-Detector-Cropper and Plate Recognition

An object recognition application using [Google's TensorFlow Object Detection API](https://github.com/tensorflow/models/tree/master/object_detection) and [OpenCV](http://opencv.org/).
Part of this code was inspired by Sentdex [Determining other vehicle distances and collision warning - Self Driving Cars in GTA](https://pythonprogramming.net/detecting-distances-self-driving-car/)
The part of plate recognition is made of by the use of OpenALPR API free tier in [Automatic License Plate Recognition library](https://github.com/openalpr/openalpr) . I'm working on my own deep learning implementation that removes the use of this api and replaces by this deeplearning model.

## Getting Started
1. `pip3 install -r requirements.txt`
2. `python3 main.py` 
    Optional arguments (default value a folder with todays date):
    * Folder to workon `-folder= <YOUR FOLDER of folders>'`

## Requirements
- [Python 3.5](https://www.continuum.io/downloads)
- [TensorFlow 1.2](https://www.tensorflow.org/)
- [OpenCV 3.0](http://opencv.org/) (just for write the plates in the image )
- [scypy] (for write the images into disk)

## Notes
- Work in progress...
## Copyright
See [LICENSE](LICENSE) for details.

Copyright (c) 2018 [stanlee321](http://deepmicrosystems.com/).
