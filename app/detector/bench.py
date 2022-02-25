import numpy as np
import cv2
import time
import glob

from yolov5_tflite_inference import yolov5_tflite
from PIL import Image, ImageOps
from utils import letterbox_image, scale_coords
import tflite_runtime.interpreter as tflite

def detect_image(image_url,weights='yolov5s-fp16.tflite',img_size=416,conf_thres=0.25,iou_thres=0.45):
    
    yolov5_tflite_obj = yolov5_tflite(weights,img_size,conf_thres,iou_thres)

    yolov5_tflite_obj.interpreter = tflite.Interpreter(yolov5_tflite_obj.weights,num_threads=2)
    yolov5_tflite_obj.interpreter.allocate_tensors()
    yolov5_tflite_obj.input_details = yolov5_tflite_obj.interpreter.get_input_details()
    yolov5_tflite_obj.output_details = yolov5_tflite_obj.interpreter.get_output_details()


    #image = cv2.imread(image_url)
    image = Image.open(image_url)

    start_time = time.time()
    original_size = image.size[:2]
    size = (img_size,img_size)
    image_resized = letterbox_image(image,size)
    img = np.asarray(image)
    
    #image = ImageOps.fit(image, size, Image.ANTIALIAS)
    image_array = np.asarray(image_resized)

    normalized_image_array = image_array.astype(np.float32) / 255.0

    result_boxes, result_scores, result_class_names = yolov5_tflite_obj.detect(normalized_image_array)

    if len(result_boxes) > 0:
        result_boxes = scale_coords(size,np.array(result_boxes),(original_size[1],original_size[0]))
        font = cv2.FONT_HERSHEY_SIMPLEX 
        
        # org 
        org = (20, 40) 
            
        # fontScale 
        fontScale = 0.5
            
        # Blue color in BGR 
        color = (0, 255, 0) 
            
        # Line thickness of 1 px 
        thickness = 1

        for i,r in enumerate(result_boxes):

            org = (int(r[0]),int(r[1]))
            cv2.rectangle(img, (int(r[0]),int(r[1])), (int(r[2]),int(r[3])), (255,0,0), 1)
            cv2.putText(img, str(int(100*result_scores[i])) + '%  ' + str(result_class_names[i]), org, font,  
                        fontScale, color, thickness, cv2.LINE_AA)

        # save_result_filepath = image_url.split('/')[-1].split('.')[0] + 'yolov5_output.jpg'
        # cv2.imwrite(save_result_filepath,img[:,:,::-1])

    end_time = time.time()
    print('Cnts: ', len(result_boxes))
    print("Yolov5s: ", end_time-start_time)


def frame_differencing(images):
    frame1 = cv2.imread(images[0])
    frame2 = cv2.imread(images[1])
    frame3 = cv2.imread(images[2])
    start = time.time()
    frameDelta1 = cv2.absdiff(frame1, frame2)
    frameDelta2 = cv2.absdiff(frame2, frame3)

    thresh = cv2.bitwise_and(frameDelta1, frameDelta2)
    thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(thresh, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=3)
    thresh = cv2.erode(thresh, None, iterations=1)
    cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
    Cnts = []

    for c in cnts:
        if cv2.contourArea(c) > 1024 * 4:
            (x, y, w, h) = cv2.boundingRect(c)
            if (w + 8) < (h + 16) * 2:
                Cnts.append([x, y, w, h])
    end=time.time()

    Cnum = 0

    prefix="/images/cropped_image"
    suffix=".jpg"

    for c in Cnts:
        Cnum += 1
        x, y, w, h = c
        cropImg = frame3[y - 10:y + h + 10, x - 10:x + w + 10]
        if (h + 20) * (w + 20) > 300 * 300:
            cropImg = cv2.resize(cropImg, (224, 224))
            cv2.imwrite(prefix+str(Cnum)+suffix,cropImg)

    print('Cnts: ', len(Cnts))
    print("Frame Differencing: ", end-start)


def bench():
    images=glob.glob("/images/image*.jpg")
    frame_differencing(images)
    for image in images:
        detect_image(image_url=image)

def frame_differencing_video(images,frame_number):
    frame1 = images[0]
    frame2 = images[1]
    frame3 = images[2]
    start = time.time()
    frameDelta1 = cv2.absdiff(frame1, frame2)
    frameDelta2 = cv2.absdiff(frame2, frame3)

    thresh = cv2.bitwise_and(frameDelta1, frameDelta2)
    thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(thresh, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=3)
    thresh = cv2.erode(thresh, None, iterations=1)
    cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
    Cnts = []

    for c in cnts:
        if cv2.contourArea(c) > 1024 * 4:
            (x, y, w, h) = cv2.boundingRect(c)
            if (w + 8) < (h + 16) * 2:
                Cnts.append([x, y, w, h])
    end=time.time()

    Cnum = 0

    prefix_image="/images/frame"
    prefix="/images/cropped_image"
    suffix=".jpg"

    for c in Cnts:
        Cnum += 1
        x, y, w, h = c
        cropImg = frame3[y - 10:y + h + 10, x - 10:x + w + 10]
        if (h + 20) * (w + 20) > 300 * 300:
            cropImg = cv2.resize(cropImg, (224, 224))
        cv2.imwrite(prefix+str(frame_number)+"_"+str(Cnum)+suffix,cropImg)
    if len(Cnts)>0:
        cv2.imwrite(prefix_image+str(frame_number)+suffix,frame3)
    print('Cnts: ', len(Cnts))
    print("Frame Differencing: ", end-start)

def bench_video():
    videoPath = "/videos/video01_5min.avi"
    camera = cv2.VideoCapture(videoPath, cv2.CAP_FFMPEG)
    fps = int(camera.get(cv2.CAP_PROP_FPS))
    queryInterval=0.3
    num = fps * queryInterval
    i = -1
    initial = False

    while camera.isOpened():
            i = i + 1

            if not initial:
                while True:
                    ret = camera.grab()
                    if ret:
                        initial=True
                        break
            else:
                ret = camera.grab()

            if not ret:
                break

            if i % num == 0:
                _, frame1 = camera.retrieve()

            if i % num == 1:
                _, frame2 = camera.retrieve()

            if i % num == 2:
                _, frame3 = camera.retrieve()
                frame_differencing_video(images=[frame1,frame2,frame3],frame_number=i)

if __name__ == "__main__":
    bench()
    
