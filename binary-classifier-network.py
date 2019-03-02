import datetime
import sys
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
import os

# BINARY CLASSIFIER NETWORK BASED ON THE LENET MODEL BUILT FOR IMAGE CLASSIFICATION TASKS
# PART OF 'PROJECT TURING' - JAKUB ADRIAN NIEMIEC (@niemtec)
# THIS MODEL IS USED AS A TOOL FOR INVESTIGATING THE PHENOMENA OF OVERFITTING IN CONVOLUTIONAL NEURAL NETWORKS
# Set the matplotlib backend so figures can be saved in the background
matplotlib.use("Agg")

# Control Variables
home = os.environ['HOME']
experimentVariantDatasetName = 'control'
resultsFileName = 'cancer-noise-010-results'
modelName = 'cancer-noise-010-' + experimentVariantDatasetName
datasetPath = home + '/home/Downloads/Project-Turing/datasets/image-corruption-dataset/cancer-noise-010'
resultsPath = home + '/home/Downloads/Project-Turing/results/noise-experiments/'
plotName = modelName
graphSize = (15, 10)  # Size of result plots
noEpochs = 100
initialLearningRate = 1e-5
batchSize = 32
decayRate = initialLearningRate / noEpochs
numberOfClasses = 2
categoryOne = 'benign'
categoryTwo = 'malignant'
validationDatasetSize = 0.25  # Using 75% of the data for training and the remaining 25% for testing
randomSeed = 42  # For repeatability
imageHeight = 64
imageWidth = 64
imageDepth = 3


# Determine whether given file is an image or not
def file_is_image(path_to_file):
    filename, extension = os.path.splitext(path_to_file)
    if extension != '.jpg':
        return False
    else:
        return True


# Prints current timestamp, to be used in print statements
def stamp():
    time = "[" + str(datetime.datetime.now().time()) + "]   "
    return time


# Save final model performance
def save_network_stats(resultsPath, modelName, history, fileName):
    # Extract data from history dictionary
    historyLoss = history.history['loss']
    historyLoss = str(historyLoss[-1])  # Get last value from loss
    historyAcc = history.history['acc']
    historyAcc = str(historyAcc[-1])  # Get last value from accuracy
    historyValLoss = history.history['val_loss']
    historyValLoss = str(historyValLoss[-1])  # Get last value from validated loss
    historyValAcc = history.history['val_acc']
    historyValAcc = str(historyValAcc[-1])  # Get last value from validated accuracy

    with open(resultsPath + '/' + fileName + ".txt", "a") as history_log:
        history_log.write(
            modelName + "," + historyLoss + "," + historyAcc + "," + historyValLoss + "," + historyValAcc + "," + str(
                noEpochs) + "," + str(initialLearningRate) + "\n")
    history_log.close()

    print(stamp() + "Keras Log Saved")


# Build the network structure
def build_network_model(width, height, depth, classes):
    # Initialise the model
    model = Sequential()
    inputShape = (height, width, depth)

    # If 'channel first' is being used, update the input shape
    if K.image_data_format() == 'channel_first':
        inputShape = (depth, height, width)

    # Model Structure
    # First layer | CONV > RELU > POOL
    model.add(
        Conv2D(20, (5, 5), padding = "same", input_shape = inputShape))  # Learning 20 (5 x 5) convolution filters
    model.add(Activation("relu"))
    model.add(MaxPooling2D(pool_size = (2, 2), strides = (2, 2)))

    # Second layer | CONV > RELU > POOL
    model.add(Conv2D(50, (5, 5), padding = "same"))
    model.add(Activation("relu"))
    model.add(MaxPooling2D(pool_size = (2, 2), strides = (2, 2)))

    # Third layer | flattening out into fully-connected layers
    model.add(Flatten())
    model.add(Dense(50))  # 500 nodes
    model.add(Activation("relu"))

    # Softmax classifier
    model.add(Dense(classes))  # number of nodes = number of classes
    model.add(Activation("softmax"))  # yields probability for each class

    # Return the model
    return model


def load_dataset_subfolder(datasetSubfolderName):
    print(stamp() + "Classifying Dataset Subfolder for: " + datasetSubfolderName)

    imageArray = []
    labelArray = []

    datasetSubfolderPath = datasetPath + '/' + experimentVariantDatasetName + '/' + datasetSubfolderName + '/'
    for datasetCategory in os.listdir(datasetSubfolderPath):
        datasetCategoryPath = datasetSubfolderName + datasetCategory

        for imageSample in os.listdir(datasetCategoryPath):
            if file_is_image(datasetCategoryPath + '/' + imageSample):
                # Load the image
                image = cv2.imread(datasetCategoryPath + '/' + imageSample)
                # Convert image to array
                image = img_to_array(image)
                # Save image to list
                imageArray.append(image)

                # Decide on binary label
                if datasetCategory == categoryOne:
                    label = 1
                else:
                    label = 0

                labelArray.append(label)
    return imageArray, labelArray


# Initialize the data and labels arrays
trainingDatasetImages = []
trainingDatasetLabels = []
validationDatasetImages = []
validationDatasetLabels = []

(trainingDatasetImages, trainingDatasetLabels) = load_dataset_subfolder('train')
(validationDatasetImages, validationDatasetLabels) = load_dataset_subfolder('validation')

trainingCombined = list(zip(trainingDatasetImages, trainingDatasetLabels))
random.shuffle(trainingCombined)
trainingDatasetImages[:], trainingDatasetLabels[:] = zip(*trainingCombined)

validationCombined = list(zip(validationDatasetImages, validationDatasetLabels))
random.shuffle(validationCombined)
validationDatasetImages[:], validationDatasetLabels[:] = zip(*validationCombined)

# Join validation and training datasets together (75% - 25% split)
combinedDatasetImages = trainingDatasetImages + validationDatasetImages
combinedDatasetLabels = trainingDatasetLabels + validationDatasetLabels
combinedDatasetImages = np.array(combinedDatasetImages, dtype = 'float') / 255.0
combinedDatasetLabels = np.array(combinedDatasetLabels)

print(stamp() + 'Training Set Size: ' + str(len(trainingDatasetLabels)))
print(stamp() + 'Validation Set Size: ' + str(len(validationDatasetLabels)))
print(stamp() + 'Total Dataset Size: ' + str(len(combinedDatasetLabels)))

# Safety stop for incorect dataset sizes
# if ((len(trainingDatasetLabels) > trainingSize) or (len(validationDatasetLabels) > validationSize)):
#     print(stamp() + 'Incorrect Dataset Size')
#     sys.exit()
# Partition the data into training and testing splits
(trainX, testX, trainY, testY) = train_test_split(combinedDatasetImages, combinedDatasetLabels,
                                                  test_size = validationDatasetSize, random_state = randomSeed)

# Convert the labels from integers to vectors
trainY = to_categorical(trainY, numberOfClasses)
testY = to_categorical(testY, numberOfClasses)

# Construct the image generator for data augmentation
aug = ImageDataGenerator(
    # rotation_range = 25
    # vertical_flip = True
    # horizontal_flip= True
    # zoom_range = 1.0
    # width_shift_range = 0.1
    # height_shift_range = 0.1,
    # shear_range = 0.2,
    # fill_mode = "nearest"
)

# Initialize the model
print(stamp() + "Compiling Network Model")
model = build_network_model(width = imageWidth, height = imageHeight, depth = imageDepth, classes = numberOfClasses)
opt = Adam(lr = initialLearningRate, decay = decayRate)
model.compile(loss = "binary_crossentropy", optimizer = opt, metrics = ["accuracy"])

# Train the network
print(stamp() + "Training Network Model")
history = model.fit_generator(aug.flow(trainX, trainY, batch_size = batchSize), validation_data = (testX, testY),
                              steps_per_epoch = len(trainX) // batchSize, epochs = noEpochs, verbose = 1)

# Save the model to disk
print(stamp() + "Saving Network Model")
model_json = model.to_json()
with open(resultsPath + '/' + modelName + ".json", "w") as json_file:
    json_file.write(model_json)

# Save the final scores
save_network_stats(resultsPath, modelName, history, resultsFileName)

# Summarize history for accuracy
plt.figure(figsize = graphSize, dpi = 75)
plt.grid(True, which = 'both')
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('Model Accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc = 'upper left')
plt.suptitle(modelName)
plt.savefig(resultsPath + '/' + modelName + "-accuracy.png")
plt.close()

# Summarize history for loss
plt.figure(figsize = graphSize, dpi = 75)
plt.grid(True, which = 'both')
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc = 'upper left')
plt.suptitle(modelName)
plt.savefig(resultsPath + '/' + modelName + "-loss.png")
plt.close()
