from mqtt_client import MqttClient
import logging
import os
import time
import numpy as np
import threading
import cv2
import queue
from distutils.util import strtobool
import glob
from concurrent.futures import ThreadPoolExecutor

from model import ResNet152
from keras.applications.imagenet_utils import decode_predictions
from keras.applications.imagenet_utils import preprocess_input

from turbojpeg import TurboJPEG, TJFLAG_FASTUPSAMPLE, TJFLAG_FASTDCT

jpeg = TurboJPEG()


def decode_image(image):
    return jpeg.decode(image, flags=TJFLAG_FASTUPSAMPLE | TJFLAG_FASTDCT)


logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

queryObject = os.getenv("QUERYOBJECT", default='moped')
nodename = os.getenv("NODE_NAME", default=None)
metric = bool(strtobool(os.getenv("METRIC", default="false")))

compressed = bool(strtobool(os.getenv("COMPRESSED", default="false")))
batch_size= int(os.getenv("BATCH_SIZE", default=1))

if metric:
    use_batch_size=16
else:
    use_batch_size=batch_size

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
    targets = ['result']
    event=threading.Event()
    while True:
        msg = {'type': 'cmd', 'contents': {'cmd': 'status', 'component': nodename+"/"+"resnet" ,'finished':finished}}
        for tmp_target in targets:
            data_mqtt_client.publish(msg, tmp_target)
        event.wait(10)


record_is_object = 0
record_is_not_object = 0

scheduler_list = {
    'scheduler_1': 'ec-a',
    'scheduler_2': 'ec-b',
    'scheduler_3': 'ec-c'
}


def load_image(img, img_width=224, img_height=224):
    x = cv2.resize(img, (img_width, img_height))
    x = preprocess_input(x)
    if x.ndim == 3:
        x = np.expand_dims(x, 0)
    return x


def loadRN152():
    #loading ResNet152 model
    start_time_RN152 = time.time()
    print('loading the ResNet152 model...')
    model_RN152 = ResNet152()
    print('done')
    print('loading time of ResNet152 model: ' +
          str(time.time() - start_time_RN152) + 's')
    return model_RN152


def RN152Refer(model_RN152, payloads, queryClass):
    global p

    '''parameter'''
    img_width, img_height = 224, 224

    with ThreadPoolExecutor(max_workers=8) as executor:
        '''data decode'''
        if compressed and not metric:
            images = list(executor.map(decode_image,[payload[2] for payload in payloads]))
        else:
            images = [payload[2] for payload in payloads]

        '''infer'''
        loaded_images = list(
            executor.map(load_image, images))
        images_preprocessed = np.vstack(loaded_images)

    y = model_RN152.predict(images_preprocessed,batch_size=use_batch_size)
    decode_results = decode_predictions(y, top=5)

    classify_at = time.time()
    classify_on = nodename

    for index, payload in enumerate(payloads):
        pred_title_list = [i[1] for i in decode_results[index]]
        payload_decoded = payload
        i = payload_decoded[0]
        videoname = payload_decoded[1]
        Cnum = payload_decoded[3]
        collect_at = payload_decoded[4]
        detect_on = payload_decoded[5]
        detect_at = payload_decoded[6]
        transfer_at = payload_decoded[7]
        reprocessing = payload_decoded[8]

        if queryClass in pred_title_list:
            global record_is_object
            record_is_object = record_is_object + 1
            # print('--------record_is_object--{}------'.format(record_is_object))
            # print("got a query object!")
            # print(str(videoname) + "f" + str(i) + 'Obj' + str(Cnum))
            label = True
        else:
            global record_is_not_object
            record_is_not_object = record_is_not_object + 1
            # print('--------record_is_not_object--{}------'.format(record_is_not_object))
            label = False
        image_name = str(videoname) + "_f" + str(i) + 'obj' + str(
            Cnum) + ".jpg"
        # 发到中心云进行存储
        if not metric:
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
        else:
            result = {
                "image_name": image_name,
                "detect_on": detect_on,
                "label": label
            }

        msg_result = {'type': 'data', 'contents': result}
        p.put({'msg':msg_result,'target':'result'})

    eil = np.mean([classify_at - payload[7] for payload in payloads])

    msg_eil = {
        'type': 'cmd',
        'contents': {
            'container_name': 'resnet',
            'cmd': 'eil',
            'eil': eil
        }
    }

    for scheduler_item in scheduler_list:
        p.put({'msg':msg_eil,'target':scheduler_item})
    return eil


def warmup(model_RN152):
    images = glob.glob("/images/*.jpg")
    for image_path in images:
        image = load_image(cv2.imread(image_path))
        model_RN152.predict(image)


def infer():
    queryClass = queryObject
    model_RN152 = loadRN152()

    warmup(model_RN152)

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

        msgs = [msg]

        try:
            while len(msgs) < use_batch_size:
                msgs.append((data_mqtt_client.get_sub_data_payload_queue().get(
                    block=False)))
                topic = data_mqtt_client.get_sub_data_sender_queue().get()
        except queue.Empty:
            pass

        # print("msgs: ", len(msgs))
        eil = RN152Refer(model_RN152, msgs, queryClass)
        # print("Mean eil: ", eil)

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

        if 'cmd' in msg:
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
    thread_infer = threading.Thread(target=infer, daemon=True)
    thread_modify = threading.Thread(target=wait_to_modify, daemon=True)
    thread_notify = threading.Thread(target=NotifyThread,daemon=True)
    thread_publish = threading.Thread(target=PublishThread,daemon=True)
    thread_notify.start()
    thread_publish.start()
    thread_modify.start()
    thread_infer.start()
    thread_notify.join()
