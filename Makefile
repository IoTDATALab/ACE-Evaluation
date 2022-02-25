# All nodes
NODES := cc ec-a ec-b ec-c ec-a-1 ec-a-2 ec-a-3 ec-b-1 ec-b-2 ec-b-3 ec-c-1 ec-c-2 ec-c-3

# Central Cloud
CC := cc
CC_IP := 192.168.0.114
CC_PUBSUB_PORT := 1883
CC_PUBSUB_MGT_HOST := 192.168.0.114
CC_PUBSUB_MGT_PORT := 8081
CC_PUBSUB_DASHBOARD_PORT := 18083

EMQX_MGT_HOST := xxx.xxx.xxx.xxx
EMQX_MGT_PORT := 40001

# Edge Clouds
EC_A := ec-a
EC_A_IP := 192.168.0.110
EC_A_PUBSUB_PORT := 1883 
EC_A_NODES := ec-a-1 ec-a-2 ec-a-3

EC_B := ec-b
EC_B_IP := 192.168.0.123
EC_B_PUBSUB_PORT := 1883 
EC_B_NODES := ec-b-1 ec-b-2 ec-b-3

EC_C := ec-c
EC_C_IP := 192.168.0.132
EC_C_PUBSUB_PORT := 1883 
EC_C_NODES := ec-c-1 ec-c-2 ec-c-3

EC_CLOUDS := ec-a ec-b ec-c

RPI_NODES := ec-a-1 ec-a-2 ec-a-3 ec-b-1 ec-b-2 ec-b-3 ec-c-1 ec-c-2 ec-c-3

EDGE_EMQX_BRIDGE__MQTT__AWS__ADDRESS := xxx.xxx.xxx.xxx:40000

CLOUD_ECCI_BROKER_PUBLIC_IP := xxx.xxx.xxx.xxx
CLOUD_ECCI_BROKER_PUBLIC_PORT := 40000

EDGE_TO_CLOUD_BANDWIDTH := 20Mbps
EDGE_TO_CLOUD_DELAY := 40ms

# CI,EI, ACE, ACE+
SCENARIO := ACE+

METRIC := false

INTERVAL := 0.1

COMPRESSED := false
COMPRESSED_QUALITY := 100

BATCH_SIZE := 1

VIDEOS := 5min

SYNC_CMD = rsync -avp -r -P -e 'ssh -F ./ssh/ssh_config -i ./ssh/ecci_id_rsa '
SSH_CMD = ssh -F ./ssh/ssh_config -i ./ssh/ecci_id_rsa 

ssh-public-key: ./ssh/ecci_id_rsa.pub

./ssh/ecci_id_rsa.pub: 
	@ssh-keygen -t rsa -P '' -f ./ssh/ecci_id_rsa;

net_config:	ssh-public-key
	@for server in $(NODES) ; do\
		echo "Make password free configuration in $$server";\
		cat ./ssh/ecci_id_rsa.pub | ${SSH_CMD} $$server "umask 077; mkdir -p .ssh ; cat >> .ssh/authorized_keys" ;\
	done

inst_rpi_docker: 
	@for server in $(RPI_NODES) ; do\
		echo "Install Docker and DockerCompose in $$server";\
		${SSH_CMD} $$server "sudo apt update;sudo apt install -y docker.io docker-compose" ;\
		${SSH_CMD} $$server "sudo usermod -aG docker pi; sudo systemctl enable docker; sudo systemctl start docker" ;\
		echo "Install rpi-bad-power in $$server";\
		${SSH_CMD} $$server "sudo apt install python3-pip -y;pip3 install rpi-bad-power" ;\
	done

send_broker_code:
	@echo "Transfer Broker source files to ${CC}"
	@${SYNC_CMD} ./broker ${CC}:~/
	@for server in $(EC_CLOUDS) ; do\
		echo "Transfer Broker source files to $$server";\
		${SYNC_CMD} ./broker $$server:~/ &\
	done
	@sleep 5

build_broker: send_broker_code 
	@${SSH_CMD} ${CC} bash -c "'pushd broker;make build-cloud-broker;popd'"
	@for server in $(EC_CLOUDS) ; do\
		${SSH_CMD} $$server bash -c "'pushd broker;make build-edge-broker;popd'"; \
	done

start_broker: send_broker_code
	@${SSH_CMD} ${CC} bash -c "'pushd broker;\
		make CLOUD_ECCI_BROKER_IP=${CC_IP} CLOUD_ECCI_BROKER_PORT=${CC_PUBSUB_PORT} CLOUD_ECCI_BROKER_MGT_PORT=${CC_PUBSUB_MGT_PORT}  CLOUD_ECCI_BROKER_DASHBOARD_PORT=${CC_PUBSUB_DASHBOARD_PORT} start-cloud-broker;\
		popd'" 
	@${SSH_CMD} ${EC_A} bash -c "'pushd broker;\
		make EDGE_EMQX_BRIDGE__MQTT__AWS__ADDRESS=${EDGE_EMQX_BRIDGE__MQTT__AWS__ADDRESS} EDGE_EMQX_BRIDGE__MQTT__AWS__CLIENTID=${EC_A} EDGE_ECCI_BROKER_ID=${EC_A} EDGE_ECCI_BROKER_PORT=${EC_A_PUBSUB_PORT} CLOUD_ECCI_BROKER_ID=${CC} CLOUD_ECCI_BROKER_PUBLIC_IP=${CLOUD_ECCI_BROKER_PUBLIC_IP}  CLOUD_ECCI_BROKER_PUBLIC_PORT=${CLOUD_ECCI_BROKER_PUBLIC_PORT} EDGE_TO_CLOUD_BANDWIDTH=${EDGE_TO_CLOUD_BANDWIDTH} EDGE_TO_CLOUD_DELAY=${EDGE_TO_CLOUD_DELAY} start-edge-broker;\
		popd'" &
	@${SSH_CMD} ${EC_B} bash -c "'pushd broker;\
		make EDGE_EMQX_BRIDGE__MQTT__AWS__ADDRESS=${EDGE_EMQX_BRIDGE__MQTT__AWS__ADDRESS} EDGE_EMQX_BRIDGE__MQTT__AWS__CLIENTID=${EC_B} EDGE_ECCI_BROKER_ID=${EC_B} EDGE_ECCI_BROKER_PORT=${EC_B_PUBSUB_PORT} CLOUD_ECCI_BROKER_ID=${CC}  CLOUD_ECCI_BROKER_PUBLIC_IP=${CLOUD_ECCI_BROKER_PUBLIC_IP}  CLOUD_ECCI_BROKER_PUBLIC_PORT=${CLOUD_ECCI_BROKER_PUBLIC_PORT} EDGE_TO_CLOUD_BANDWIDTH=${EDGE_TO_CLOUD_BANDWIDTH} EDGE_TO_CLOUD_DELAY=${EDGE_TO_CLOUD_DELAY} start-edge-broker;\
		popd'" &
	@${SSH_CMD} ${EC_C} bash -c "'pushd broker;\
		make EDGE_EMQX_BRIDGE__MQTT__AWS__ADDRESS=${EDGE_EMQX_BRIDGE__MQTT__AWS__ADDRESS} EDGE_EMQX_BRIDGE__MQTT__AWS__CLIENTID=${EC_C} EDGE_ECCI_BROKER_ID=${EC_C} EDGE_ECCI_BROKER_PORT=${EC_C_PUBSUB_PORT} CLOUD_ECCI_BROKER_ID=${CC}  CLOUD_ECCI_BROKER_PUBLIC_IP=${CLOUD_ECCI_BROKER_PUBLIC_IP}  CLOUD_ECCI_BROKER_PUBLIC_PORT=${CLOUD_ECCI_BROKER_PUBLIC_PORT} EDGE_TO_CLOUD_BANDWIDTH=${EDGE_TO_CLOUD_BANDWIDTH} EDGE_TO_CLOUD_DELAY=${EDGE_TO_CLOUD_DELAY} start-edge-broker;\
		popd'" &
	@sleep 5

stop_broker:
	@${SSH_CMD} ${CC} bash -c "'pushd broker;make CLOUD_ECCI_BROKER_IP=${CC_IP} CLOUD_ECCI_BROKER_PORT=${CC_PUBSUB_PORT} CLOUD_ECCI_BROKER_MGT_PORT=${CC_PUBSUB_MGT_PORT}  CLOUD_ECCI_BROKER_DASHBOARD_PORT=${CC_PUBSUB_DASHBOARD_PORT} stop-cloud-broker;popd'" &
	@for server in $(EC_CLOUDS) ; do\
		${SSH_CMD} $$server bash -c "'pushd broker;make EDGE_EMQX_BRIDGE__MQTT__AWS__ADDRESS=${EDGE_EMQX_BRIDGE__MQTT__AWS__ADDRESS} EDGE_EMQX_BRIDGE__MQTT__AWS__CLIENTID=${EC_A} EDGE_ECCI_BROKER_ID=${EC_A} EDGE_ECCI_BROKER_PORT=${EC_A_PUBSUB_PORT} CLOUD_ECCI_BROKER_ID=${CC} stop-edge-broker;popd'" &\
	done

send_app_code:
	@for server in $(RPI_NODES) ; do\
		echo "Transfer detector/mnv2 source files to $$server";\
		${SYNC_CMD} ./app/detector $$server:~/;\
		${SYNC_CMD} ./app/mnv2  $$server:~/ &\
	done
	@for server in $(EC_CLOUDS) ; do\
		echo "Transfer scheduler source files to $$server"; \
		${SYNC_CMD} ./app/scheduler $$server:~/ &\
	done
	@echo "Transfer resnet source files to ${CC}"
	@${SYNC_CMD} ./app/resnet ${CC}:~/
	@echo "Transfer result source files to ${CC}"
	@${SYNC_CMD} ./app/result ${CC}:~/


build_app: send_app_code
	@for server in $(RPI_NODES) ; do\
		echo "Build detector/mnv2 on $$server";\
		${SSH_CMD} $$server bash -c "'pushd detector;docker-compose -f docker-compose.yml build --pull;popd'";\
		${SSH_CMD} $$server bash -c "'pushd mnv2;docker-compose -f docker-compose.yml build --pull;popd'" ; \
	done
	@for server in $(EC_CLOUDS) ; do\
		echo "Build scheduler on $$server";\
		${SSH_CMD} $$server bash -c "'pushd scheduler;docker-compose -f docker-compose.yml build --pull;popd'" ;\
	done
	@echo "Build resnet on ${CC}"
	@${SSH_CMD} ${CC} bash -c "'pushd resnet;docker-compose -f docker-compose.gpu.yml build --pull;popd'"
	@echo "Build result on ${CC}"
	@${SSH_CMD} ${CC} bash -c "'pushd result;docker-compose -f docker-compose.yml build --pull;popd'"

start_app: 
	@echo "Start result on ${CC}"
	@${SSH_CMD} ${CC} bash -c  "'pushd result; \
		VIDEOS=${VIDEOS} BATCH_SIZE=${BATCH_SIZE} COMPRESSED=${COMPRESSED} COMPRESSED_QUALITY=${COMPRESSED_QUALITY} SCENARIO=${SCENARIO} INTERVAL=${INTERVAL} EDGE_TO_CLOUD_BANDWIDTH=${EDGE_TO_CLOUD_BANDWIDTH} EDGE_TO_CLOUD_DELAY=${EDGE_TO_CLOUD_DELAY} ECCI_LOCAL_BROKER_IP=${CC_IP} ECCI_LOCAL_BROKER_ID=${CC} NODE_NAME=${CC} docker-compose -f docker-compose.yml up -d;\
		popd'"	

ifneq (${SCENARIO},EI)
	@${SSH_CMD} ${CC} bash -c  "'pushd resnet; \
		BATCH_SIZE=${BATCH_SIZE} COMPRESSED=${COMPRESSED} ECCI_LOCAL_BROKER_IP=${CC_IP} ECCI_LOCAL_BROKER_ID=${CC} NODE_NAME=${CC} docker-compose -f docker-compose.gpu.yml up -d;\
		popd'"
	@sleep 40
	
endif

ifeq (${SCENARIO},ACE+)
	# EC-A
	@${SSH_CMD} ${EC_A} bash -c  "'pushd scheduler; \
		INTERVAL=${INTERVAL} ECCI_LOCAL_BROKER_IP=${EC_A_IP} ECCI_LOCAL_BROKER_ID=${EC_A} NODE_NAME=${EC_A} ECCI_REMOTE_BROKER_ID=${CC} docker-compose -f docker-compose.yml up -d;\
		popd'" &
	# EC-B
	@${SSH_CMD} ${EC_B} bash -c  "'pushd scheduler; \
		INTERVAL=${INTERVAL} ECCI_LOCAL_BROKER_IP=${EC_B_IP} ECCI_LOCAL_BROKER_ID=${EC_B} NODE_NAME=${EC_B} ECCI_REMOTE_BROKER_ID=${CC} docker-compose -f docker-compose.yml up -d;\
		popd'" &
	# EC-C
	@${SSH_CMD} ${EC_C} bash -c  "'pushd scheduler; \
		INTERVAL=${INTERVAL} ECCI_LOCAL_BROKER_IP=${EC_C_IP} ECCI_LOCAL_BROKER_ID=${EC_C} NODE_NAME=${EC_C} ECCI_REMOTE_BROKER_ID=${CC} docker-compose -f docker-compose.yml up -d;\
		popd'" &
endif

ifneq (${SCENARIO},CI)
	# EC-A
	@for server in $(EC_A_NODES) ; do\
		${SSH_CMD} $$server bash -c "'pushd mnv2; \
				COMPRESSED=${COMPRESSED} SCENARIO=${SCENARIO} ECCI_LOCAL_BROKER_IP=${EC_A_IP} ECCI_LOCAL_BROKER_ID=${EC_A} NODE_NAME=$$server ECCI_REMOTE_BROKER_ID=${CC} docker-compose -f docker-compose.yml up -d;\
				popd'" &\
	done
	# EC-B
	@for server in $(EC_B_NODES) ; do\
		${SSH_CMD} $$server bash -c "'pushd mnv2; \
				COMPRESSED=${COMPRESSED} SCENARIO=${SCENARIO} ECCI_LOCAL_BROKER_IP=${EC_B_IP} ECCI_LOCAL_BROKER_ID=${EC_B} NODE_NAME=$$server ECCI_REMOTE_BROKER_ID=${CC} docker-compose -f docker-compose.yml up -d;\
				popd'" &\
	done
	# EC-C
	@for server in $(EC_C_NODES) ; do\
		${SSH_CMD} $$server bash -c "'pushd mnv2; \
				COMPRESSED=${COMPRESSED} SCENARIO=${SCENARIO} ECCI_LOCAL_BROKER_IP=${EC_C_IP} ECCI_LOCAL_BROKER_ID=${EC_C} NODE_NAME=$$server ECCI_REMOTE_BROKER_ID=${CC} docker-compose -f docker-compose.yml up -d;\
				popd'" &\
	done
	@sleep 10
endif

	# EC-A
	@for server in $(EC_A_NODES) ; do\
		${SSH_CMD} $$server bash -c "'pushd detector; \
				VIDEOS=${VIDEOS} COMPRESSED=${COMPRESSED} COMPRESSED_QUALITY=${COMPRESSED_QUALITY} METRIC=${METRIC} SCENARIO=${SCENARIO} INTERVAL=${INTERVAL} ECCI_LOCAL_BROKER_IP=${EC_A_IP} ECCI_LOCAL_BROKER_ID=${EC_A} NODE_NAME=$$server ECCI_REMOTE_BROKER_ID=${CC} docker-compose -f docker-compose.yml up -d;\
				popd'" &\
	done
	# EC-B
	@for server in $(EC_B_NODES) ; do\
		${SSH_CMD} $$server bash -c "'pushd detector; \
				VIDEOS=${VIDEOS} COMPRESSED=${COMPRESSED} COMPRESSED_QUALITY=${COMPRESSED_QUALITY} SCENARIO=${SCENARIO} INTERVAL=${INTERVAL} ECCI_LOCAL_BROKER_IP=${EC_B_IP} ECCI_LOCAL_BROKER_ID=${EC_B} NODE_NAME=$$server ECCI_REMOTE_BROKER_ID=${CC} docker-compose -f docker-compose.yml up -d;\
				popd'" &\
	done
	# EC-C
	@for server in $(EC_C_NODES) ; do\
		${SSH_CMD} $$server bash -c "'pushd detector; \
				VIDEOS=${VIDEOS} COMPRESSED=${COMPRESSED} COMPRESSED_QUALITY=${COMPRESSED_QUALITY} SCENARIO=${SCENARIO} INTERVAL=${INTERVAL} ECCI_LOCAL_BROKER_IP=${EC_C_IP} ECCI_LOCAL_BROKER_ID=${EC_C} NODE_NAME=$$server ECCI_REMOTE_BROKER_ID=${CC} docker-compose -f docker-compose.yml up -d;\
				popd'" &\
	done

log_app:
	@echo "Result logs on ${CC}"
	@${SSH_CMD} ${CC} bash -c  "'pushd result;docker-compose -f docker-compose.yml logs -f;popd'"

stop_app:
	@for server in $(RPI_NODES) ; do\
		${SSH_CMD} $$server bash -c "'pushd detector;docker-compose -f docker-compose.yml down;popd'" &\
	done

ifneq (${SCENARIO},CI)
	@for server in $(RPI_NODES) ; do\
		${SSH_CMD} $$server bash -c "'pushd mnv2;docker-compose -f docker-compose.yml down;popd'" &\
	done
endif

ifeq (${SCENARIO},ACE+)
	@for server in $(EC_CLOUDS) ; do\
		${SSH_CMD} $$server bash -c "'pushd scheduler;docker-compose -f docker-compose.yml down;popd'" &\
	done
endif

ifneq (${SCENARIO},EI)
	@${SSH_CMD} ${CC} bash -c "'pushd resnet;docker-compose -f docker-compose.gpu.yml down;popd'"
endif

	@echo "Stop result on ${CC}"
	@${SSH_CMD} ${CC} bash -c  "'pushd result;docker-compose -f docker-compose.yml down;popd'"

start_metric:
	@echo "Start result on ${CC}"
	@${SSH_CMD} ${CC} bash -c  "'pushd result; \
		VIDEOS=${VIDEOS} BATCH_SIZE=${BATCH_SIZE} COMPRESSED=${COMPRESSED} COMPRESSED_QUALITY=${COMPRESSED_QUALITY} METRIC=${METRIC} SCENARIO=${SCENARIO} INTERVAL=${INTERVAL} EDGE_TO_CLOUD_BANDWIDTH=${EDGE_TO_CLOUD_BANDWIDTH} EDGE_TO_CLOUD_DELAY=${EDGE_TO_CLOUD_DELAY} ECCI_LOCAL_BROKER_IP=${CC_IP} ECCI_LOCAL_BROKER_ID=${CC} NODE_NAME=${CC} docker-compose -f docker-compose.yml up -d;\
		popd'"	

	@${SSH_CMD} ${CC} bash -c  "'pushd resnet; \
		BATCH_SIZE=${BATCH_SIZE} METRIC=${METRIC} ECCI_LOCAL_BROKER_IP=${CC_IP} ECCI_LOCAL_BROKER_ID=${CC} NODE_NAME=${CC} docker-compose -f docker-compose.gpu.yml up -d;\
		popd'"	
	@sleep 40

	# EC-A
	@for server in $(EC_A_NODES) ; do\
		${SSH_CMD} $$server bash -c "'pushd detector; \
				VIDEOS=${VIDEOS} METRIC=${METRIC} SCENARIO=${SCENARIO} INTERVAL=${INTERVAL} ECCI_LOCAL_BROKER_IP=${EC_A_IP} ECCI_LOCAL_BROKER_ID=${EC_A} NODE_NAME=$$server ECCI_REMOTE_BROKER_ID=${CC} docker-compose -f docker-compose.yml up -d;\
				popd'"&\
	done
	# EC-B
	@for server in $(EC_B_NODES) ; do\
		${SSH_CMD} $$server bash -c "'pushd detector; \
				VIDEOS=${VIDEOS} METRIC=${METRIC} SCENARIO=${SCENARIO} INTERVAL=${INTERVAL} ECCI_LOCAL_BROKER_IP=${EC_B_IP} ECCI_LOCAL_BROKER_ID=${EC_B} NODE_NAME=$$server ECCI_REMOTE_BROKER_ID=${CC} docker-compose -f docker-compose.yml up -d;\
				popd'"&\
	done
	# EC-C
	@for server in $(EC_C_NODES) ; do\
		${SSH_CMD} $$server bash -c "'pushd detector; \
				VIDEOS=${VIDEOS} METRIC=${METRIC} SCENARIO=${SCENARIO} INTERVAL=${INTERVAL} ECCI_LOCAL_BROKER_IP=${EC_C_IP} ECCI_LOCAL_BROKER_ID=${EC_C} NODE_NAME=$$server ECCI_REMOTE_BROKER_ID=${CC} docker-compose -f docker-compose.yml up -d;\
				popd'"&\
	done

log_metric:
	@echo "Result logs on ${CC}"
	@${SSH_CMD} ${CC} bash -c  "'pushd result;docker-compose -f docker-compose.yml logs -f;popd'"


stop_metric:
	@for server in $(RPI_NODES) ; do\
		${SSH_CMD} $$server bash -c "'pushd detector;docker-compose -f docker-compose.yml down;popd'" &\
	done

	@${SSH_CMD} ${CC} bash -c "'pushd resnet;docker-compose -f docker-compose.gpu.yml down;popd'"

	@echo "Stop result on ${CC}"
	@${SSH_CMD} ${CC} bash -c  "'pushd result;docker-compose -f docker-compose.yml down;popd'"

collect_results:
	@echo "Collect results on ${CC}"
	@${SYNC_CMD} ${CC}:~/result/results/ ./results


reboot_rpi_nodes:
	@-for server in $(RPI_NODES) ; do\
		echo "Reboot!";\
		${SSH_CMD} $$server "sudo reboot" &\
	done

rpi_status:
	@-for server in $(RPI_NODES) ; do\
		script="from rpi_bad_power import new_under_voltage;under_voltage = new_under_voltage();print(under_voltage.get())";\
		echo $$server;\
		echo "System: ";\
		${SSH_CMD} $$server "echo 'normal!'" ;\
		echo "Bad Power: ";\
		${SSH_CMD} $$server "python -c '$$script'" ;\
	done