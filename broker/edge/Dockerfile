FROM emqx/emqx-edge:4.3.10

COPY update-start.sh /usr/bin/

RUN sudo apk add --no-cache iproute2 python3 py3-pip \
    && sudo pip3 install tcconfig \
    && sudo chmod +x /opt/emqx/bin/emqx \
    && sudo chmod +x /usr/bin/update-start.sh

CMD ["/usr/bin/update-start.sh"]