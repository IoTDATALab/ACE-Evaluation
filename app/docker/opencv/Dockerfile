FROM --platform=$TARGETPLATFORM condaforge/miniforge3:4.10.3-9

ARG TARGETPLATFORM

ARG EXEC_ARM64="conda install -y -q --freeze-installed opencv"
ARG EXEC_AMD64="conda install -y -q --freeze-installed -c fastai opencv-python-headless"

RUN conda install -y -q --freeze-installed paho-mqtt numpy tinydb requests pyturbojpeg \
    && if [ "${TARGETPLATFORM}" = "linux/arm64" ] ; then eval "${EXEC_ARM64}";  else eval "${EXEC_AMD64}"; fi \
    && conda clean -a 