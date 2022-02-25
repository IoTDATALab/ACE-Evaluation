import logging
import os
import threading
import time
import queue

import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from keras_preprocessing import image
from distutils.util import strtobool
from mqtt_client import MqttClient

from turbojpeg import TurboJPEG, TJFLAG_FASTUPSAMPLE, TJFLAG_FASTDCT

jpeg = TurboJPEG()

def encode_image(image, quality=100):
    return jpeg.encode(image,
                       quality=quality,
                       flags=TJFLAG_FASTUPSAMPLE | TJFLAG_FASTDCT)

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

record_recv = 0

record_is_not_object = 0
record_is_object = 0
record_infer_again = 0

alpha_value = 0.8

nodename = os.getenv("NODE_NAME", default=None)
brokerid = os.getenv("ECCI_LOCAL_BROKER_ID", default=None)
remote_brokerid = os.getenv("ECCI_REMOTE_BROKER_ID", default=None)

scenario = os.getenv("SCENARIO", default="ACE+")
metric = bool(strtobool(os.getenv("METRIC", default="false")))

compressed = bool(strtobool(os.getenv("COMPRESSED", default="false")))
compressed_quality = int(os.getenv("COMPRESSED_QUALITY", default=100))

def brokerid_to_schedulerid(brokerid):
    schedulers = {
        "ec-a": "scheduler_1",
        "ec-b": "scheduler_2",
        "ec-c": "scheduler_3",
    }
    return schedulers.get(brokerid, None)


scheduler = brokerid_to_schedulerid(brokerid)


def nodename_to_local_containers(nodename):
    local_containers = {
        "ec-a-1": ['detector_1', 'mnv2_1'],
        "ec-b-1": ['detector_1', 'mnv2_1'],
        "ec-c-1": ['detector_1', 'mnv2_1'],
        "ec-a-2": ['detector_2', 'mnv2_2'],
        "ec-b-2": ['detector_2', 'mnv2_2'],
        "ec-c-2": ['detector_2', 'mnv2_2'],
        "ec-a-3": ['detector_3', 'mnv2_3'],
        "ec-b-3": ['detector_3', 'mnv2_3'],
        "ec-c-3": ['detector_3', 'mnv2_3'],
    }
    return local_containers.get(nodename, None)


LOCAL_CONTAINERS = nodename_to_local_containers(nodename)

nodename = os.getenv("NODE_NAME", default=None)


def nodename_to_containername(nodename):
    containernames = {
        "ec-a-1": "mnv2_1",
        "ec-b-1": "mnv2_1",
        "ec-c-1": "mnv2_1",
        "ec-a-2": "mnv2_2",
        "ec-b-2": "mnv2_2",
        "ec-c-2": "mnv2_2",
        "ec-a-3": "mnv2_3",
        "ec-b-3": "mnv2_3",
        "ec-c-3": "mnv2_3",
    }
    return containernames.get(nodename, None)


CONTAINER_NAME = nodename_to_containername(nodename)

container_name = CONTAINER_NAME

time_frame = list()

data_mqtt_client = MqttClient()
data_mqtt_client.initialize()
data_mqtt_client.run()

p = queue.Queue()

sources={}
activated=False

finished = False
def NotifyThread():
    global data_mqtt_client,finished
    targets = ['resnet', 'result']
    event=threading.Event()
    while True:
        msg = {'type': 'cmd', 'contents': {'cmd': 'status', 'component': nodename+"/"+"mnv2" ,'finished':finished}}
        for tmp_target in targets:
            data_mqtt_client.publish(msg, tmp_target)
        event.wait(10)

def load_image(img, img_width, img_height):
    img = cv2.resize(img, (img_width, img_height))
    img_tensor = image.img_to_array(img)  # (height, width, channels)
    img_tensor = np.expand_dims(
        img_tensor, axis=0
    )  # (1, height, width, channels), add a dimension because the model expects this shape: (batch_size, height, width, channels)
    img_tensor /= 255.  # imshow expects values in the range [0, 1]
    return img_tensor


def MNv2ReferLite(interpreter, payload, alpha):
    global scenario,p
    '''parameter'''
    flag = 0
    img_width, img_height = 224, 224

    beta = (1 - alpha) * 0.5
    start_time_infer = time.time()
    '''data decode'''
    payload_decoded = payload
    i = payload_decoded[0]
    videoname = payload_decoded[1]
    ContourPic = payload_decoded[2]
    Cnum = payload_decoded[3]
    start_time_frame = payload_decoded[4]

    collect_at = payload_decoded[4]
    detect_on = payload_decoded[5]
    detect_at = payload_decoded[6]
    transfer_at = payload_decoded[7]
    reprocessing = payload_decoded[8]
    '''infer'''
    Image_preprocessed = load_image(ContourPic, img_width, img_height)

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    input_data = Image_preprocessed

    start=time.time()

    interpreter.set_tensor(input_details[0]['index'], input_data)

    interpreter.invoke()

    # The function `get_tensor()` returns a copy of the tensor data.
    # Use `tensor()` in order to get a pointer to the tensor.
    output_data = interpreter.get_tensor(output_details[0]['index'])

    end=time.time()
    # print("MNv2 Inner (s): ",str(end-start))

    classify_at = time.time()
    classify_on = nodename

    MNv2ConfidenceValue = output_data[0][0]

    stop_time = time.time()

    label=None

    msg_eil = {
        'type': 'cmd',
        'contents': {
            'container_name': container_name,
            'cmd': 'eil',
            'eil': classify_at-transfer_at
        }
    }
    p.put({'msg':msg_eil,'target':scheduler})

    # print(f'---------this frame stop time---{time.time()}-------')
    if MNv2ConfidenceValue > alpha:
        global record_is_object
        record_is_object = record_is_object + 1
        # print(f'--------record_is_object--{record_is_object}------')
        # print("got a query object!")
        # print(str(videoname) + "f" + str(i) + 'Obj' + str(Cnum))
        label=True
    elif scenario != "EI" and MNv2ConfidenceValue <= alpha and MNv2ConfidenceValue > beta:
        global record_infer_again
        record_infer_again = record_infer_again + 1
        # print(f'--------record_infer_again--{record_infer_again}------')
        flag = 1
        reprocessing = True
        payload_decoded[8] = reprocessing
        if compressed and not metric:
            ContourPic =encode_image(ContourPic,quality=compressed_quality)
        payload_decoded[2]=ContourPic 
        msg_resnet = {'type': 'data', 'contents': payload_decoded}
        p.put({'msg':msg_resnet,'target': 'resnet'})
    else:
        global record_is_not_object
        record_is_not_object = record_is_not_object + 1
        # print(f'--------record_is_not_object--{record_is_not_object}------')
        label=False

    if label is not None:
        image_name = str(videoname) + "_f" + str(i) + 'obj' + str(
            Cnum) + ".jpg"
        result = {
            "image_name": image_name,
            "detect_on": detect_on,
            "collect_at": collect_at,
            "detect_at": detect_at,
            "transfer_at": transfer_at,
            "classify_at": classify_at,
            "classify_on": classify_on,
            "reprocessing": reprocessing,
            "label": label
        }
        msg_result = {'type': 'data', 'contents': result}
        p.put({'msg':msg_result,'target':'result'})

    return start_time_frame, flag


def infer():
    interpreter = tflite.Interpreter(model_path="/converted_model.tflite",num_threads=2)
    interpreter.allocate_tensors()

    while True:
        try:
            msg = data_mqtt_client.get_sub_data_payload_queue().get(
                timeout=0.01)
        except queue.Empty:
            global activated,sources,finished
            if activated and len(sources.keys()) == 0:
                finished=True
                break
            continue

        topic = data_mqtt_client.get_sub_data_sender_queue().get()

        global record_recv
        record_recv = record_recv + 1
        # print(f'--------record_recv--{record_recv}------')
        queuePic_size = data_mqtt_client.get_sub_data_sender_queue().qsize()
        # print(f'--------queue_size--{queuePic_size}--------')

        ContourPic = msg[2]
        try:
            if ContourPic is not None:
                start=time.time()
                start_time_frame, flag = MNv2ReferLite(interpreter, msg,
                                                       alpha_value)
                end=time.time()
                # print("MNv2(s): ",str(end-start))
                if flag == 0:
                    time_frame.append(time.time() - float(start_time_frame))
        except Exception as e:
            print(e)

def PublishThread():
    global data_mqtt_client
    while True:
        item = p.get()
        data_mqtt_client.publish(item['msg'], item['target'])
        p.task_done()

def wait_to_modify():
    global sources,activated
    while True:
        msg = data_mqtt_client.get_sub_cmd_payload_queue().get()
        topic = data_mqtt_client.get_sub_cmd_sender_queue().get()
        if 'cmd' not in msg:
            global alpha_value
            alpha_value = msg['alpha']
        else:
            cmd = msg['cmd']
            if cmd == "status":
                if not activated:
                    activated=True
                component = msg['component']
                component_finished = msg['finished']
                if  component_finished:
                    if component in sources.keys():
                        sources.pop(component)
                else:
                    sources[component]=component_finished

if __name__ == "__main__":
    thread_infer = threading.Thread(target=infer,daemon=True)
    thread_modify = threading.Thread(target=wait_to_modify, daemon=True)
    thread_notify = threading.Thread(target=NotifyThread,daemon=True)
    thread_publish = threading.Thread(target=PublishThread,daemon=True)
    thread_notify.start()
    thread_publish.start()
    thread_infer.start()
    thread_modify.start()
    thread_notify.join()
    