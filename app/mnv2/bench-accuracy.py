import numpy as np
import cv2
import time
import tflite_runtime.interpreter as tflite
from keras_preprocessing import image

import glob

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
                                     num_threads=20)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print('done')
    print('loading time of MNV2 model: ' + str(time.time()-start_time_MNv2) + 's')
    return interpreter

alpha=0.8

def infer(interpreter, image_path):
    input_data=load_image(cv2.imread(image_path))
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    st=time.time()
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    tflite_result = interpreter.get_tensor(output_details[0]['index'])[0][0]
    return tflite_result >= alpha

def judge(image,predicted):
    ground_truth= "moped" in image
    if ground_truth and predicted:
        return "tp"
    elif ground_truth and not predicted:
        return "fn"
    elif not ground_truth and predicted:
        return "fp"
    else:
        return "tn"

def bench():
    dataset_path="/dataset/"
    dirs=glob.glob(dataset_path+"*")
    images=[]
    for dir in dirs:
        images+=glob.glob(dir+"/"+"*.jpg")

    records=pd.DataFrame()
    records['image']=pd.DataFrame(images)
    interpreter=loadMNv2()
    results=[infer(interpreter,image) for image in images]
    records['predicted']=pd.DataFrame(results)
    results=list(map(judge,records['image'],records['predicted']))
    results=pd.DataFrame(results)
    statistics=results.value_counts()
    tp = (results == "tp").sum()
    fp = (results == "fp").sum()
    tn = (results == "tn").sum()
    fn = (results == "fn").sum()
    error_rate=(fp+fn)*1.0/(tp+fp+tn+fn)
    print("Error Rate (threshold={alpha}): {error_rate}".format(alpha=alpha,error_rate=error_rate))


if __name__ == "__main__":
    bench()
