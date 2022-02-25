FROM wangluhui/tensorflow-lite:latest

COPY MobileNet_v2.py /
COPY weight.h5 /
COPY main.py /
COPY mqtt_client.py /

RUN pip3 install pandas

CMD ["python3","main.py"]
