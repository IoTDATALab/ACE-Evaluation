FROM --platform=$TARGETPLATFORM condaforge/miniforge3:4.10.3-9

ARG TARGETPLATFORM

ARG EXEC_ARM64="conda install -y -q --freeze-installed opencv \
    && wget 'https://raw.githubusercontent.com/PINTO0309/TensorflowLite-bin/main/2.7.0/download_tflite_runtime-2.7.0-cp39-none-linux_aarch64.whl.sh' \
    && chmod +x download_tflite_runtime-2.7.0-cp39-none-linux_aarch64.whl.sh \
    && ./download_tflite_runtime-2.7.0-cp39-none-linux_aarch64.whl.sh \
    && pip install --upgrade tflite_runtime-2.7.0-cp39-none-linux_aarch64.whl \
    && rm tflite_runtime-2.7.0-cp39-none-linux_aarch64.whl"
ARG EXEC_AMD64="conda install -y -q --freeze-installed -c fastai opencv-python-headless \
    && pip install --no-cache https://raw.githubusercontent.com/Frenz86/tflite_runtime/main/tflite_runtime-2.5.0.post1-cp39-cp39-linux_x86_64.whl"

RUN conda install -y -q --freeze-installed paho-mqtt numpy tinydb requests pyturbojpeg curl keras-preprocessing \
    && if [ "$TARGETPLATFORM" = "linux/arm64" ] ; then eval "${EXEC_ARM64}"; else eval "${EXEC_AMD64}"; fi \
    && conda clean -a