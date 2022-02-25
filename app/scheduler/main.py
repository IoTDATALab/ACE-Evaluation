from mqtt_client import MqttClient
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

num_resv = 0

mqtt_client = MqttClient()
mqtt_client.initialize()
mqtt_client.run()

interval=float(os.getenv("INTERVAL", default=None))

mnv2_detector= {
    'mnv2_1':'detector_1','mnv2_2':'detector_2','mnv2_3':'detector_3',
}

remote_target = 'resnet'

values = {'resnet': {'eil':0}}

mnv2_list = ['mnv2_1','mnv2_2','mnv2_3']
for mnv2_item in mnv2_list:
    values[mnv2_item] = {'eil':0}

upper_alpha = 0.8
lower_alpha = 0.5

alpha = 0.8

expected_time=0.3
# expected_time=interval


gamma1 = 0.01
rate = 0.2

policy_list = {
    'detector_1':{'target':'mnv2_1'},
    'detector_2':{'target':'mnv2_2'},
    'detector_3':{'target':'mnv2_3'},
    'mnv2_1':{'alpha': alpha},
    'mnv2_2':{'alpha': alpha},
    'mnv2_3':{'alpha': alpha}
}

def scheduler():
    global policy_list
    while True:

        msg = mqtt_client.get_sub_cmd_payload_queue().get()
        topic = mqtt_client.get_sub_cmd_sender_queue().get()
        if msg['cmd'] == 'eil':
            values[msg['container_name']]['eil'] = msg['eil']*rate+ values[msg['container_name']]['eil']* (1 - rate)
            for item in set(values.keys())-set([msg['container_name']]):
                values[item]['eil'] = 0*rate+ values[msg['container_name']]['eil']* (1 - rate)
        else:
            continue

        remote_time = values['resnet']['eil']

        for item in policy_list:
            if 'mnv2' in item:
                temp_time = values[item]['eil']
                # print('---------'+item+'-----'+str(temp_time)+'-----------')
                if  temp_time <= remote_time:
                    target = item
                    min_time = temp_time
                else:
                    target = remote_target
                    min_time = remote_time
                detector=mnv2_detector[item]
                detector_policy=policy_list[detector]
                mnv2_policy=policy_list[item]
                old_alpha=mnv2_policy['alpha']
                old_target=detector_policy['target']
                alpha= max(min(upper_alpha,old_alpha-gamma1*(0.5*(temp_time-expected_time)+0.5*(remote_time-expected_time))),lower_alpha)
                # print("Node: {node}, Alpha: {alpha}".format(node=item,alpha=alpha))
                if alpha != old_alpha:
                    msg_alpha = {'type':'cmd','contents':{'alpha':alpha}}
                    mqtt_client.publish(msg_alpha,item)
                    policy_list.update({item:{'alpha':alpha}})
                if target != old_target:
                    msg_target = {'type':'cmd','contents':{'target':target}}
                    mqtt_client.publish(msg_target,detector)
                    policy_list.update({detector:{'target':target}})
            # print(policy_list)
        # print(values)


if __name__ == "__main__":
    scheduler()