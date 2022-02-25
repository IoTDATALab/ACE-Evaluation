import numpy as np
import tensorflow as tf

from MobileNet_v2 import MobileNetV2
from keras.layers.core import Activation
from keras.layers import Dense,GlobalAveragePooling2D
from keras.models import Model

import time

import cv2
from keras.preprocessing import image

def load_image(img,img_width=224,img_height=224):
    img = cv2.resize(img, (img_width, img_height))
    img_tensor = image.img_to_array(img)                    # (height, width, channels)
    img_tensor = np.expand_dims(img_tensor, axis=0)         # (1, height, width, channels), add a dimension because the model expects this shape: (batch_size, height, width, channels)
    img_tensor /= 255.                                      # imshow expects values in the range [0, 1]
    return img_tensor

# model = tf.keras.applications.MobileNetV2(
#     weights="imagenet", input_shape=(224, 224, 3))

weightPath = "./weight.h5"
alpha_MNv2 = 0.5
test_image = './images/videof11.1obj1.jpg'

def loadMNv2(weightPath,alpha_MNv2):
    '''loading MobileNet_v2 model'''
    start_time_load = time.time()
    print('loading the MobileNet_v2 model...')

    classNum = 2
    img_width, img_height = 224,224

    base_model = MobileNetV2(input_shape=(img_width, img_height,3),
                    alpha=alpha_MNv2,
                    include_top=False,
                    weights= None
                    )

    x=base_model.output
    x=GlobalAveragePooling2D()(x)
    x=Dense(1024,activation='relu')(x)
    x=Dense(1024,activation='relu')(x)
    x=Dense(512,activation='relu')(x)
    preds=Dense(classNum,activation='softmax')(x) #final layer with softmax activation
    model_MNv2=Model(inputs=base_model.input,outputs=preds)
    model_MNv2.load_weights(weightPath)
    print('done')
    end_time_load = time.time()
    print('loading time of MobileNet_v2 model: ' + str(end_time_load-start_time_load) + 's')
    return model_MNv2

model=loadMNv2(weightPath,alpha_MNv2)
model.save('mnv2.h5')

model2=tf.keras.models.load_model('mnv2.h5', compile=False)

converter = tf.lite.TFLiteConverter.from_keras_model(model2)
tflite_model = converter.convert()
open("converted_model.tflite", "wb").write(tflite_model)

interpreter = tf.lite.Interpreter(model_content=tflite_model)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# input_shape = input_details[0]['shape']
# input_data = np.array(np.random.random_sample(input_shape), dtype=np.float32)

input_data=load_image(cv2.imread(test_image))

tf_results = model.predict(input_data)
print(tf_results)

tf_results = model2(tf.constant(input_data))
print(tf_results)

interpreter.set_tensor(input_details[0]['index'], input_data)

interpreter.invoke()

tflite_results = interpreter.get_tensor(output_details[0]['index'])
print(tflite_results)

# for tf_result, tflite_result in zip(tf_results, tflite_results):
#   np.testing.assert_almost_equal(tf_result, tflite_result, decimal=5)