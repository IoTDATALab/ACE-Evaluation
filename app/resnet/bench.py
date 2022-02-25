import os, sys
import time
import numpy as np
import cv2
from model import ResNet152
from keras.applications.imagenet_utils import decode_predictions
from keras.applications.imagenet_utils import preprocess_input
import glob

from turbojpeg import TurboJPEG, TJFLAG_FASTUPSAMPLE, TJFLAG_FASTDCT

jpeg = TurboJPEG()

def encode_image(image, quality=100):
    return jpeg.encode(image,
                       quality=quality,
                       flags=TJFLAG_FASTUPSAMPLE | TJFLAG_FASTDCT)

def decode_image(image):
    return jpeg.decode(image, flags=TJFLAG_FASTUPSAMPLE | TJFLAG_FASTDCT)

queryObject = os.getenv("QUERYOBJECT", default='moped')


def load_image(img, img_width=224, img_height=224):
    x = cv2.resize(img, (img_width, img_height))
    x = preprocess_input(x)
    if x.ndim == 3:
        x = np.expand_dims(x, 0)
    return x


# test_image = '/images/videof2.7obj1.jpg'
# # test_image = '/images/videof12.6obj4.jpg'
# # test_image = '/images/videof11.1obj1.jpg'


def loadRN152():
    #loading ResNet152 model
    start_time_RN152 = time.time()
    print('loading the ResNet152 model...')
    model_RN152 = ResNet152()
    print('done')
    print('loading time of ResNet152 model: ' +
          str(time.time() - start_time_RN152) + 's')
    return model_RN152


def infer(model_RN152, image_path_list, img_width=224, img_height=224):
    results = []
    images = np.vstack(
        [load_image(cv2.imread(image_path)) for image_path in image_path_list])
    st = time.time()
    y = model_RN152.predict(images)
    print(decode_predictions(y, top=5))
    return results

def codec(image_path):
    input_data=load_image(cv2.imread(image_path))
    
    encode_times=[]
    decode_times=[]

    for _ in range(10):
        start=time.time()
        encoded=encode_image(input_data)
        end=time.time()
        encode_time=end-start
        encode_times.append(encode_time)
    for _ in range(10):
        start=time.time()
        decoded=decode_image(encoded)
        end=time.time()
        decode_time=end-start
        decode_times.append(decode_time)
    return np.mean(encode_times),np.mean(decode_times)

def bench():
    images = glob.glob("/images/*.jpg")
    interpreter = loadRN152()
    results = []
    costs = []
    # start = time.time()
    for _ in range(10):
        for image in images:
            start = time.time()
            items = infer(interpreter, [image])
            end = time.time()
            print(1, "image (batch:32) : ", end - start)

    for _ in range(10):
        start = time.time()
        items = infer(interpreter, images)
        end = time.time()
        print(len(images), "images (batch:32) : ", end-start)
        print("Mean InferTime: ", (end-start)*1.0/len(images))

    items=[codec(image) for image in images]
    print("Mean EncodeTime: ",np.mean([item[0] for item in items]))
    print("Mean DecodeTime: ",np.mean([item[1] for item in items]))
    


if __name__ == "__main__":
    bench()
