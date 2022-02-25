import logging
import os
import queue
import threading
import time

from distutils.util import strtobool
from tinydb import TinyDB, Query
import glob
from mqtt_client import MqttClient
import numpy as np

import requests

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

number = int(os.getenv("NUMBER", default=1))
interval = float(os.getenv("INTERVAL", default=None))
scenario = os.getenv("SCENARIO", default="ACE+")
bandwidth = os.getenv("EDGE_TO_CLOUD_BANDWIDTH", default="10Mbps")
delay = os.getenv("EDGE_TO_CLOUD_DELAY", default="100ms")

broker_mgt_host = os.getenv("EMQX_MGT_HOST", default="202.117.43.192")
broker_mgt_port = os.getenv("EMQX_MGT_PORT", default="40001")
broker_mgt_username = os.getenv("EMQX_MGT_USERNAME", default="admin")
broker_mgt_password = os.getenv("EMQX_MGT_PASSWORD", default="public")

metric = bool(strtobool(os.getenv("METRIC", default="false")))

compressed = bool(strtobool(os.getenv("COMPRESSED", default="false")))
compressed_quality = int(os.getenv("COMPRESSED_QUALITY", default=100))
batch_size = int(os.getenv("BATCH_SIZE", default=1))

videos = os.getenv("VIDEOS", default="1min")

labels_path = os.path.join("/results/labels",videos+"_"+str(interval) + ".json")

if metric:
    results_path = sorted(glob.glob("/results/*[0-9]*"))[-1]
else:
    results_path = os.path.join("/results/", str(round(time.time())))
    os.mkdir(results_path)

length = 0

time_frame = list()

data_mqtt_client = MqttClient()
data_mqtt_client.initialize()
data_mqtt_client.run()

sources={}
activated=False

def receive():
    number=0
    global activated,sources
    if metric:
        database = TinyDB(labels_path)
    else:
        database = TinyDB(os.path.join(results_path, "records.json"))
    results=[]
    while True:
        try:
            msg = data_mqtt_client.get_sub_data_payload_queue().get(
                timeout=0.01)
        except queue.Empty:
            if activated and len(sources.keys()) == 0:
                break
            continue

        topic = data_mqtt_client.get_sub_data_sender_queue().get()
        try:
            result = msg
            if not metric:
                transfer_at = result['transfer_at']
                classify_at = result['classify_at']
                result['eil'] = classify_at - transfer_at
                result["number"] = number        
                result["scenario"] = scenario
                result["delay"] = delay
                result["bandwidth"] = bandwidth
                result["compressed"] = compressed
                result["compressed_quality"] = compressed_quality
                result["batch_size"]=batch_size
            result["interval"] = interval
            result["videos"]=videos
            number+=1
            if number%100==0:
                logger.info({"number":number,"sources":sources,"result":result})
            results.append(result)
        except Exception as e:
            print(e)
    database.insert_multiple(results)


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

def broker_statistics():
    r = requests.get(
        f'http://{broker_mgt_host}:{broker_mgt_port}/api/v4/clients/?_like_clientid=ec-',
        auth=(broker_mgt_username, broker_mgt_password))
    ecs = r.json()['data']
    bandwidth = sum([ec['recv_oct'] for ec in ecs])
    return bandwidth


def predict_statistics():
    predicted = TinyDB(os.path.join(results_path, "records.json"))
    ground_truth = TinyDB(labels_path)
    eils = [record['eil'] for record in predicted.all()]

    def judge(record,ground_truths):
        predicted=record['label']
        image_name=record['image_name']
        detect_on = record['detect_on']
        if image_name+"-"+detect_on+"-"+str(predicted) in ground_truths:
            return "tp" if predicted else "tn" 
        else:
            return "fp" if predicted else "fn"

    ground_truths=frozenset([image['image_name']+"-"+image['detect_on']+"-"+str(image['label']) for image in ground_truth.all()])

    results=np.array([judge(record,ground_truths) for record in predicted.all()])

    tp = int((results == "tp").sum())
    fp = int((results == "fp").sum())
    tn = int((results == "tn").sum())
    fn = int((results == "fn").sum())

    precision = tp * 1.0 / (tp + fp)
    recall = tp * 1.0 / (tp + fn)
    f1_score = 2 * precision * recall / (precision + recall)
    f2_score = 5 * precision * recall / (4 * precision + recall)
    total = tp + fp + tn + fn
    tod = tp + fp

    result = dict(tp=tp,
                  fp=fp,
                  tn=tn,
                  fn=fn,
                  total=total,
                  tod=tod,
                  precision=precision,
                  recall=recall,
                  f1_score=f1_score,
                  f2_score=f2_score,
                  eils=eils)

    return result


if __name__ == "__main__":
    start=time.time()
    if metric:
        bandwidth_consumed = broker_statistics() / 1000
        print("bandwidth(kilobytes): ", bandwidth_consumed)
    
    if not os.path.exists(labels_path) or not metric:
        event = threading.Event()
        thread_receive = threading.Thread(target=receive, daemon=True)
        thread_modify = threading.Thread(target=wait_to_modify, daemon=True)
        thread_receive.start()
        thread_modify.start()
        thread_receive.join()
        event.wait(5)

    if metric:
        result = predict_statistics()
        result['bandwidth_consumed'] = bandwidth_consumed
        result['bpo'] = bandwidth_consumed / result['tod']
        result["number"] = number
        result["interval"] = interval
        result["scenario"] = scenario
        result["delay"] = delay
        result["bandwidth"] = bandwidth
        result["compressed"] = compressed
        result["compressed_quality"] = compressed_quality
        result["batch_size"]=batch_size
        result["videos"]=videos
        statistics = TinyDB(os.path.join(results_path, "statistics.json"))
        statistics.insert(result)
    end=time.time()
    print("Total Time (s): ",end-start)