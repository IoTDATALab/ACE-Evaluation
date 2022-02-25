import numpy as np
import cv2
import time
import tflite_runtime.interpreter as tflite
from keras_preprocessing import image

import glob

from turbojpeg import TurboJPEG, TJFLAG_FASTUPSAMPLE, TJFLAG_FASTDCT

jpeg = TurboJPEG()

def encode_image(image, quality=100):
    return jpeg.encode(image,
                       quality=quality,
                       flags=TJFLAG_FASTUPSAMPLE | TJFLAG_FASTDCT)

def decode_image(image):
    return jpeg.decode(image, flags=TJFLAG_FASTUPSAMPLE | TJFLAG_FASTDCT)

def load_image(img,img_width=224,img_height=224):
    img = cv2.resize(img, (img_width, img_height))
    img_tensor = image.img_to_array(img)                    # (height, width, channels)
    img_tensor = np.expand_dims(img_tensor, axis=0)         # (1, height, width, channels), add a dimension because the model expects this shape: (batch_size, height, width, channels)
    img_tensor /= 255.                                      # imshow expects values in the range [0, 1]
    return img_tensor

def loadMNv2():
    start_time_MNv2 = time.time()
    print('loading the MNv2 model...')
    interpreter = tflite.Interpreter(model_path="/converted_model.tflite",
                                     num_threads=2)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print('done')
    print('loading time of MNV2 model: ' + str(time.time()-start_time_MNv2) + 's')
    return interpreter

def infer(interpreter, image_path):
    input_data=load_image(cv2.imread(image_path))
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    st=time.time()
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    tflite_result = interpreter.get_tensor(output_details[0]['index'])[0][0]
    if tflite_result >0.5:
        result=True
    else:
        result=False
    cost=time.time()-st
    return {"result":result,"cost":cost}

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
    images=glob.glob("/images/*.jpg")
    interpreter=loadMNv2()
    items=[infer(interpreter,image) for image in images]
    results= [item["result"] for item in items]
    costs=[item["cost"] for item in items]
    positive= results.count(True)
    recall=positive*1.0/len(results)
    print("Recall: ",recall)
    print("Mean InferTime: ",np.mean(costs))
    items=[codec(image) for image in images]
    print("Mean EncodeTime: ",np.mean([item[0] for item in items]))
    print("Mean DecodeTime: ",np.mean([item[1] for item in items]))
    

if __name__ == "__main__":
    bench()
