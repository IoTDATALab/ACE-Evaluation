#!/bin/sh
set -e -u

sudo tcset eth0 --delay ${EDGE_TO_CLOUD_DELAY} --rate ${EDGE_TO_CLOUD_BANDWIDTH} --network ${CLOUD_ECCI_BROKER_PUBLIC_IP} --port ${CLOUD_ECCI_BROKER_PUBLIC_PORT}

/opt/emqx/bin/emqx foreground