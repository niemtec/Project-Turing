# An attempt at using Transfer Learning to approach the Cancer Identification Problem

from keras import applications
from keras.preprocessing.image import ImageDataGenerator
from keras import optimizers
from keras.models import Sequential, Model
from keras.layers import Dropout, Flatten, Dense, GlobalAveragePooling2D
from keras import backend as k
from keras.callbacks import ModelCheckpoint, LearningRateScheduler, TensorBoard, EarlyStopping

img_width = 256
img_height = 256
train_data_dir = 'padded-dataset/train'
validation_data_dir = 'padded-dataset/validation'
nb_train_samples = 512
nb_validation_samples = 512
batch_size = 16
epochs = 50

model = applications.VGG19(
    weights = 'imagenet',
    include_top = False,
    input_shape = (img_width, img_height, 3))

# Freeze the layers which you don't want to train
for layer in model.layers[:5]:
    layer.trainable = False

# Adding custom layers
x = model.output
x = Flatten()(x)
x = Dense(1024, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(1024, activation='relu')(x)
predictions = Dense(16, activation='softmax')(x)

# Creating the final model
