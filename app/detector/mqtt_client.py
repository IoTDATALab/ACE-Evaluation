import paho.mqtt.client as mqtt
import threading
import os
import ast
import re
import _pickle as cPickle
from queue import Queue
import io
from urllib import request
import logging
import mimetypes
import uuid
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SUB_OBJECTS = os.getenv("ECCI_SUB_OBJECTS",default = None)

nodename=os.getenv("NODE_NAME", default=None)
brokerid=os.getenv("ECCI_LOCAL_BROKER_ID", default=None)
remote_brokerid=os.getenv("ECCI_REMOTE_BROKER_ID", default=None)

def brokerid_to_schedulerid(brokerid):
    schedulers = {
        "ec-a": "scheduler_1",
        "ec-b": "scheduler_2",
        "ec-c": "scheduler_3",
    }
    return schedulers.get(brokerid,None)

scheduler= brokerid_to_schedulerid(brokerid)

ECCI_PUB_TARGETS={
                    'mnv2_1':brokerid,
                    'mnv2_2':brokerid,
                    'mnv2_3':brokerid,
                    scheduler :brokerid,
                    'resnet':remote_brokerid
                }
PUB_TARGETS = ECCI_PUB_TARGETS

BROKER_IP = os.getenv("ECCI_LOCAL_BROKER_IP")
BROKER_PORT = int(os.getenv("ECCI_LOCAL_BROKER_PORT", default="1883"))
BROKER_ID = os.getenv("ECCI_LOCAL_BROKER_ID")
BROKER_USERNAME = os.getenv("ECCI_LOCAL_BROKER_USERNAME")
BROKER_PASSWORD = os.getenv("ECCI_LOCAL_BROKER_PASSWORD")

APP_ID = os.getenv("ECCI_APP_ID")

nodename=os.getenv("NODE_NAME", default=None)
def nodename_to_containername(nodename):
    containernames = {
        "ec-a-1": "detector_1",
        "ec-b-1": "detector_1",
        "ec-c-1": "detector_1",
        "ec-a-2": "detector_2",
        "ec-b-2": "detector_2",
        "ec-c-2": "detector_2",
        "ec-a-3": "detector_3",
        "ec-b-3": "detector_3",
        "ec-c-3": "detector_3",
    }
    return containernames.get(nodename,None)

CONTAINER_NAME = nodename_to_containername(nodename)

BRIDGE_MOUNTPOINTS = ast.literal_eval(os.getenv("ECCI_BRIDGE_MOUNTPOINTS",default="[]"))

# CONTAINER_TYPE = cloud/edge
CONTAINER_TYPE = os.getenv("ECCI_CONTAINER_TYPE")

# ECCI/(cmd/data/+)/cloud_broker_id/app_id/+/container_id
TOPIC_PREFIX = f"ECCI/{BROKER_ID}/{APP_ID}"

def gen_sub_topic(pub_dict):
    target,target_broker_ip = pub_dict
    return target,f'ECCI/{target_broker_ip}/{APP_ID}/app/{CONTAINER_NAME}/{target}'
    # return target,f'ECCI/{target_broker_ip}/{APP_ID}/{CONTAINER_NAME}/edgeai_{APP_ID}_{target}'
# PUB_TOPICS = dict(map(lambda key: (key, f"{TOPIC_PREFIX}/{CONTAINER_NAME}/{key}"), ast.literal_eval(PUB_TARGETS)))
if PUB_TARGETS:
    PUB_TOPICS = dict(map(gen_sub_topic,PUB_TARGETS.items()))

class MqttClient:

    def __init__(self):
        self._broker_ip = BROKER_IP
        self._broker_port = BROKER_PORT

        self._sub_data_sender_queue = Queue()
        self._sub_data_payload_queue = Queue()
        self._sub_cmd_sender_queue = Queue()
        self._sub_cmd_payload_queue = Queue()
        self._mqtt_client = None

    def get_sub_data_sender_queue(self):
        return self._sub_data_sender_queue
    
    def get_sub_data_payload_queue(self):
        return self._sub_data_payload_queue

    def get_sub_cmd_sender_queue(self):
        return self._sub_cmd_sender_queue
    
    def get_sub_cmd_payload_queue(self):
        return self._sub_cmd_payload_queue


    def _on_client_connect(self, mqtt_client, userdata, flags, rc):
        logging.info("Connected with result code "+str(rc))

        if PUB_TARGETS:
            # logger.debug("PUB_TARGETS existed")
            # logger.debug("PUB_TOPICS = "+ str(PUB_TOPICS))
            pass
        
        if BRIDGE_MOUNTPOINTS:
            for mountpoint in BRIDGE_MOUNTPOINTS:
                sub_prefix = f"{mountpoint}{TOPIC_PREFIX}"
                # logger.debug("SUB_BRIDGE_MOUNTPOINTS_TOPICS = "+ str(f"{sub_prefix}/app and plugin/+/{CONTAINER_NAME}"))
                self._mqtt_client.subscribe(f"{sub_prefix}/app/+/{CONTAINER_NAME}", qos=2)
                self._mqtt_client.subscribe(f"{sub_prefix}/plugin/+/{CONTAINER_NAME}", qos=2)
        
        # logger.debug("SUB_SELF = "+ str(f"{TOPIC_PREFIX}/app and plugin/+/{CONTAINER_NAME}"))
        self._mqtt_client.subscribe(f"{TOPIC_PREFIX}/app/+/{CONTAINER_NAME}", qos=2)
        self._mqtt_client.subscribe(f"{TOPIC_PREFIX}/plugin/+/{CONTAINER_NAME}", qos=2)
        # self._mqtt_client.subscribe(f"/{sub_prefix}/+/{CONTAINER_NAME}", qos=2)

        if SUB_OBJECTS != None:
            sub_objects = ast.literal_eval(SUB_OBJECTS)
            for sub_object  in sub_objects:
                self._mqtt_client.subscribe(f"{TOPIC_PREFIX}/app/+/{sub_object}", qos=2)
                self._mqtt_client.subscribe(f"{TOPIC_PREFIX}/plugin/+/{sub_object}", qos=2)


    def _on_client_message(self, mqtt_client, userdata, msg):
        # self.subscribe_msg.set()
        # logger.debug("the topic of received msg is "+msg.topic)
        rev_msg = cPickle.loads(msg.payload)
        # logger.debug("the payload of received msg is "+str(rev_msg))
        sender = self._topic_parse(msg.topic)
        # logger.debug("the sender of received msg is "+str(sender))
        if rev_msg['type'] == "cmd":
            self._sub_cmd_sender_queue.put(sender)
            self._sub_cmd_payload_queue.put(rev_msg['contents'])

        elif rev_msg['type'] == "data":
            self._sub_data_sender_queue.put(sender)
            self._sub_data_payload_queue.put(rev_msg['contents'])
    
    def _on_client_publish(self, mqtt_client, userdata, mid):
        # logger.debug("publish success")
        pass

    def find_target(self, targets):
        target_list=[]
        if isinstance(targets,str):
            for pub_target in list(PUB_TARGETS.keys()):
                if pub_target.startswith(targets):
                    target_list.append(pub_target)
        elif isinstance(targets,list):
            for target in targets:
                for pub_target in list(PUB_TARGETS.keys()):
                    if pub_target.startswith(target):
                        target_list.append(pub_target)
        # logger.debug(f"{targets} match {str(target_list)}")
        return target_list

    def publish(self, message, targets=None, retain=False):
        no_match = True
        try:
            if targets == None:
                for topic in list(PUB_TOPICS.values()):
                    self._mqtt_client.publish(topic=topic, payload=cPickle.dumps(message), qos=2, retain=retain)
                no_match = False
            elif isinstance(targets,str) or isinstance(targets,list):
                target_list = self.find_target(targets)
                if len(target_list) != 0:
                    no_match = False
                for target_item in target_list:
                    self._mqtt_client.publish(topic=PUB_TOPICS[target_item], payload=cPickle.dumps(message), qos=2, retain=retain)
            else:
                logger.critical(f"Illegal targets format which is {str(type(targets))}")
            if no_match:
                logger.critical(f"refused publish, {targets} does not exist in the {PUB_TOPICS}")
        except Exception as e:
            logger.error(e)

    def _topic_parse(self, topic):
        if BRIDGE_MOUNTPOINTS:
            for mountpoint in BRIDGE_MOUNTPOINTS:
                pattern = f"^{mountpoint}"
                if re.match(pattern,topic):
                    sender = re.findall(r'^(?:'+mountpoint+')?/?ECCI/.*/.*/.*/(.*)/.*',topic)[0]
        # it = [m.start() for m in re.finditer(r"_", container_name)]
        # sender = container_name[(it[1]+1):]
                    # sender_target = re.findall(r"^edgeai_.*?_(.*)", sender)[0]
                    return sender
        else:
            sender = re.findall(r'^ECCI/.*/.*/.*/(.*)/.*',topic)[0]
            # sender_target = re.findall(r"^edgeai_.*?_(.*)", sender)[0]
            return sender
        
    
    def initialize(self):
        
        try:
            self._mqtt_client = mqtt.Client()
            self._mqtt_client.on_message = self._on_client_message
            self._mqtt_client.on_connect = self._on_client_connect
            self._mqtt_client.on_publish = self._on_client_publish
        except TypeError:
            logger.error('Connect to mqtt broker error')
            return

    def run(self):
        try:
            # logger.debug(self._broker_ip+str(self._broker_port))
            if BROKER_USERNAME and BROKER_PASSWORD:
                self._mqtt_client.username_pw_set(BROKER_USERNAME,BROKER_PASSWORD)
            self._mqtt_client.connect(self._broker_ip, self._broker_port)
            self._mqtt_client.loop_start()
        except Exception as e:
            logger.error('Error occurred in event handler: {}'.format(e))
