# Tool used to print the dataset images for pictographic representation of data augmentation techniques
import matplotlib
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from keras.preprocessing.image import img_to_array
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.layers.core import Activation
from keras.layers.core import Flatten
from keras.layers.core import Dense
from keras import backend as K
import matplotlib.pyplot as plt
import numpy as np
import random
import cv2
# import Image
import os

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Control Variables
imageHeight = 3
imageWidth = 3


def load_image(pathToImage):
    # Load the image
    image = cv2.imread(pathToImage)
    # Resize the image
    image = cv2.resize(image, (imageHeight, imageWidth))
    # Convert image to array
    imageArray = img_to_array(image)
    return imageArray


def plot_image(imageArray, saveDirectory, newImageName):
    # DEBUG: Show image if you want
    plt.imshow(imageArray / 255)  # /255 to make image coloured again
    plt.show()
    # plt.savefig(saveDirectory + "/" + newImageName + ".png")


def alter_image(originalImageArray, augmentationFactor):
    # Convert array to a numpy array
    originalImageArray = np.array(originalImageArray)




########################################################
# Load image to display how array looks like
# img = mpimg.imread("C://Users//janie//PycharmProjects//Project-Turing//datasets//cats-dogs//dog//dog.1.jpg")
imagePath = "datasets/cats-dogs/dog/dog.24.jpg"
# img = mpimg.imread(imagePath)
# implot = plt.imshow(img)
# plt.show()
#
# rawImage = load_image(imagePath)
# plt.imshow(rawImage / 255)
# plt.show()
# plot_image(rawImage)

# Display image as an array first

imageArray = load_image(imagePath)
print(imageArray)
