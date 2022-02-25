from glob import glob
from mqtt_client import MqttClient
import logging
import os
import time
import threading
import cv2
import queue
from distutils.util import strtobool

from turbojpeg import TurboJPEG, TJFLAG_FASTUPSAMPLE, TJFLAG_FASTDCT

jpeg = TurboJPEG()

def encode_image(image, quality=100):
    return jpeg.encode(image,
                       quality=quality,
                       flags=TJFLAG_FASTUPSAMPLE | TJFLAG_FASTDCT)

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

record_pub_out = 0
mqtt_client = MqttClient()
mqtt_client.initialize()

p = queue.Queue()

queryInterval = float(os.getenv("INTERVAL", default=None))

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

ECCI_PUB_TARGETS = {
    'mnv2_1': brokerid,
    'mnv2_2': brokerid,
    'mnv2_3': brokerid,
    scheduler: brokerid,
    'resnet': remote_brokerid
}


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

videos = os.getenv("VIDEOS", default="1min")
def nodename_to_video_path(nodename):
    video_paths = {
        "ec-a-1": '/videos/video01_{videos}.avi'.format(videos=videos),
        "ec-b-1": '/videos/video01_{videos}.avi'.format(videos=videos),
        "ec-c-1": '/videos/video01_{videos}.avi'.format(videos=videos),
        "ec-a-2": '/videos/video02_{videos}.avi'.format(videos=videos),
        "ec-b-2": '/videos/video02_{videos}.avi'.format(videos=videos),
        "ec-c-2": '/videos/video02_{videos}.avi'.format(videos=videos),
        "ec-a-3": '/videos/video03_{videos}.avi'.format(videos=videos),
        "ec-b-3": '/videos/video03_{videos}.avi'.format(videos=videos),
        "ec-c-3": '/videos/video03_{videos}.avi'.format(videos=videos),
    }
    return video_paths.get(nodename, None)

videopath = nodename_to_video_path(nodename)
videoname = os.path.basename(videopath)

for container_name in LOCAL_CONTAINERS:
    if container_name.startswith('mnv2_'):
        mnv2 = container_name
        target = container_name
if metric or scenario == "CI":
    target = "resnet"



if metric or scenario == "CI":
    initial_targets = ['resnet']
elif scenario == "ACE+":
    initial_targets = [mnv2, 'resnet']
else:
    initial_targets = [mnv2]

finished = False
def NotifyThread():
    global mnv2, mqtt_client,finished
    targets = [mnv2, 'resnet']
    event=threading.Event()
    while True:
        msg = {'type': 'cmd', 'contents': {'cmd': 'status', 'component': nodename+"/"+"detector" ,'finished':finished}}
        for tmp_target in targets:
            mqtt_client.publish(msg, tmp_target)
        event.wait(10)

def ObjectDetect(payload):
    global p
    i = payload[0]
    videoname = payload[1]
    frame1 = payload[2]
    frame2 = payload[3]
    frame3 = payload[4]
    start_time_frame = payload[5]
    detect_at = time.time()
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

    # print('Cnts: ', Cnts)

    Cnum = 0

    for c in Cnts:
        Cnum += 1
        x, y, w, h = c
        cropImg = frame3[y - 10:y + h + 10, x - 10:x + w + 10]
        if (h + 20) * (w + 20) > 300 * 300:
            cropImg = cv2.resize(cropImg, (224, 224))

        img_width, img_height = 224, 224

        try:
            if cropImg is not None:
                global initial_targets
                global target

                if len(initial_targets)>0:
                    tmp_target=initial_targets.pop()
                else:
                    tmp_target=target

                # print("Target: ",tmp_target)

                detect_on = nodename
                transfer_at = time.time()
                reprocessing = False

                if compressed and not metric and tmp_target=='resnet':
                    cropImg=encode_image(cropImg,quality=compressed_quality)
                payload = [
                    i, videoname, cropImg, Cnum, start_time_frame, detect_on,
                    detect_at, transfer_at, reprocessing
                ]
                msg = {'type': 'data', 'contents': payload}

                # print(f'-------------pub to {tmp_target}---------')
                p.put({'msg':msg,'target':tmp_target})
                global record_pub_out
                record_pub_out = record_pub_out + 1
                # print("Publised: ",str(record_pub_out))
        except Exception as e:
            print(e)

def PublishThread():
    global mqtt_client
    while True:
        item = p.get()
        mqtt_client.publish(item['msg'], item['target'])

def RetrieveThread():
    global finished
    start_time_video = time.time()
    videoPath = videopath
    # print(videoPath)
    camera = cv2.VideoCapture(videoPath, cv2.CAP_FFMPEG)
    # print('Video FPS: ', camera.get(cv2.CAP_PROP_FPS))
    fps = int(camera.get(cv2.CAP_PROP_FPS))

    num = fps * queryInterval
    i = -1

    initial = False
    event = threading.Event()

    start=0
    stop=0

    while camera.isOpened():
        i = i + 1
        if i % num == 0:
            start=time.time()

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
            t = float('%.2f' % (float(i - 3) / float(fps)))
            # print('Video Time: ', t)
            payload = [t, videoname, frame1, frame2, frame3, time.time()]
            # print('---------------target--------------')
            ObjectDetect(payload)
        # print('frame:', time.time()-st)
        if i % num == (num-1):
            stop=time.time()
            interval=stop-start
            diff=queryInterval-interval
            # print('diff: ',str(diff))
            if diff>0:
                event.wait(diff)
            # print('now:',str(time.time()))
        

    end_time_video = time.time()
    totalTime = end_time_video - start_time_video
    # print('Total Time: ' + str(totalTime) + 's')
    # print('--------------------stop----------------')
    finished=True



def wait_to_modify():
    while True:
        msg = mqtt_client.get_sub_cmd_payload_queue().get()
        topic = mqtt_client.get_sub_cmd_sender_queue().get()
        if 'cmd' not in msg:
            global target
            target = msg['target']

if __name__ == "__main__":
    mqtt_client.run()

    event = threading.Event()
    event.wait(5)

    retrieve = threading.Thread(target=RetrieveThread, daemon=True)
    notify = threading.Thread(target=NotifyThread,daemon=True)
    publish = threading.Thread(target=PublishThread,daemon=True)
    if scenario == "ACE+":
        thread_sub = threading.Thread(target=wait_to_modify, daemon=True)
        for t in [notify,publish,thread_sub, retrieve]:
            t.start()
    else:
        for t in [notify,publish,retrieve]:
            t.start()

    notify.join()