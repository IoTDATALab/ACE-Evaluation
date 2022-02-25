# ACE-Evaluation
The implementation and experimental results of paper: `'ACE: Towards Application-Centric Edge-Cloud Collaborative Intelligence'`.
## Note!!!

- This repository doesn't include the full implemention of the `ACE platform`.

- For evaluation purpose, the `resource-level service` (i.e., `message service`) and the detailed `application logics` were modified to be `platform-agnostic`. 

- Video and model files related to the evaluation were stored in [OneDrive](https://stuxjtueducn-my.sharepoint.com/:f:/g/personal/wangluhui_stu_xjtu_edu_cn/EvwR4E5_wZZPqPlRNLXcbMIBwUw-cMISy-dnOg0NDhjd2Q?e=RkE2F8).

## How To Use in Real Testbed

### CI
```
make net_config
make inst_rpi_docker
make send_broker_code send_app_code
make build_app build_broker

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms start_broker send_app_code;\
make VIDEOS=5min SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min METRIC=true SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker send_app_code;\
make VIDEOS=5min SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min METRIC=true SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make reboot_rpi_nodes
```

### EI
```
make net_config
make inst_rpi_docker
make send_broker_code send_app_code
make build_app build_broker

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms start_broker send_app_code;\
make VIDEOS=5min SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min METRIC=true SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker send_app_code;\
make VIDEOS=5min SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min METRIC=true SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make reboot_rpi_nodes
```

### ACE
```
make net_config
make inst_rpi_docker
make send_broker_code send_app_code
make build_app build_broker

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms start_broker send_app_code;\
make VIDEOS=5min SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min METRIC=true SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker send_app_code;\
make VIDEOS=5min SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min METRIC=true SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make reboot_rpi_nodes
```

### ACE+
```
make net_config
make inst_rpi_docker
make send_broker_code send_app_code
make build_app build_broker

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms start_broker send_app_code;\
make VIDEOS=5min SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min METRIC=true SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker send_app_code;\
make VIDEOS=5min SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min METRIC=true SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make reboot_rpi_nodes
```


### Compressed Communications
```
make net_config
make inst_rpi_docker
make send_broker_code send_app_code
make build_app build_broker

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker send_app_code;\
make VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 METRIC=true SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker send_app_code;\
make VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 METRIC=true SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker send_app_code;\
make VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 METRIC=true SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker send_app_code;\
make VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 METRIC=true SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make reboot_rpi_nodes
```
### Batch Processing
```
make net_config
make inst_rpi_docker
make send_broker_code send_app_code
make build_app build_broker

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker send_app_code;\
make VIDEOS=5min BATCH_SIZE=16 SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min BATCH_SIZE=16 METRIC=true SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker send_app_code;\
make VIDEOS=5min BATCH_SIZE=16 SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min BATCH_SIZE=16 METRIC=true SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker send_app_code;\
make VIDEOS=5min BATCH_SIZE=16 SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min BATCH_SIZE=16 METRIC=true SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker send_app_code;\
make VIDEOS=5min BATCH_SIZE=16 SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make VIDEOS=5min BATCH_SIZE=16 METRIC=true SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make collect_results stop_broker stop_app

make reboot_rpi_nodes
```

## How To Use in Local Testbed

### CI
```
make -f Makefile.local build_app build_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms start_broker;\
make -f Makefile.local VIDEOS=5min SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min METRIC=true SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker;\
make -f Makefile.local VIDEOS=5min SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min METRIC=true SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker
```

### EI
```
make -f Makefile.local build_app build_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms start_broker;\
make -f Makefile.local VIDEOS=5min SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min METRIC=true SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker;\
make -f Makefile.local VIDEOS=5min SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min METRIC=true SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker
```

### ACE
```
make -f Makefile.local build_app build_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms start_broker;\
make -f Makefile.local VIDEOS=5min SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min METRIC=true SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker;\
make -f Makefile.local VIDEOS=5min SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min METRIC=true SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker
```

### ACE+
```
make -f Makefile.local build_app build_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms start_broker;\
make -f Makefile.local VIDEOS=5min SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min METRIC=true SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=50ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker;\
make -f Makefile.local VIDEOS=5min SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min METRIC=true SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker
```

### Compressed Communication

```
make -f Makefile.local build_app build_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker;\
make -f Makefile.local VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 METRIC=true SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker;\
make -f Makefile.local VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 METRIC=true SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker;\
make -f Makefile.local VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 METRIC=true SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker;\
make -f Makefile.local VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min COMPRESSED=true COMPRESSED_QUALITY=100 METRIC=true SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker
```

### Batch Processing
```
make -f Makefile.local build_app build_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker;\
make -f Makefile.local VIDEOS=5min BATCH_SIZE=16 SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min BATCH_SIZE=16 METRIC=true SCENARIO=CI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker;\
make -f Makefile.local VIDEOS=5min BATCH_SIZE=16 SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min BATCH_SIZE=16 METRIC=true SCENARIO=EI EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker;\
make -f Makefile.local VIDEOS=5min BATCH_SIZE=16 SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min BATCH_SIZE=16 METRIC=true SCENARIO=ACE EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker

make -f Makefile.local EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms start_broker;\
make -f Makefile.local VIDEOS=5min BATCH_SIZE=16 SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_app log_app stop_app;\
make -f Makefile.local VIDEOS=5min BATCH_SIZE=16 METRIC=true SCENARIO=ACE+ EDGE_TO_CLOUD_BANDWIDTH=20Mbps EDGE_TO_CLOUD_DELAY=0ms INTERVAL=0.3 start_metric log_metric stop_metric;\
make -f Makefile.local stop_broker
```