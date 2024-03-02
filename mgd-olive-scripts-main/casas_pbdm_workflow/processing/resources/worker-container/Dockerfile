FROM scratch

ADD sbin/apk.static /sbin/
ADD etc/apk/repositories /etc/apk/
RUN [ "/sbin/apk.static", "--allow-untrusted", "-U", \
      "add", "--initdb", \
      "alpine-keys" ]

RUN ["/sbin/apk.static", "add", "--update", "alpine-base", "xvfb", "wine", "wget", "py-pip"]
ADD winetricks.sh /
RUN chmod +x winetricks.sh && mv winetricks.sh /usr/bin/winetricks

ENV WINEARCH win32
ENV DISPLAY :0
ENV REGION eu-west-1

COPY pbdm /

RUN \
    echo "**** install Python ****" && \
    apk add --no-cache python3 py3-pip && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    pip3 install --upgrade pip && \
	mkdir -p /aws && \
	apk -Uuv add groff less python3 py-pip 

RUN \
	pip3 install --upgrade boto3==1.23.10 

RUN python3 --version

RUN \
    apk -Uuv add groff less python3 py-pip && \
    pip install six \
    pip install awscli && \
    rm /var/cache/apk/*

RUN \	
    echo "**** install Build-Base ****" && \
	apk add build-base && \
    # apk add --no-cache aws-cli && \
	apk add python3-dev && \
	apk add libffi && \
	apk add libffi-dev && \
	apk add openssl-dev

RUN \
    apk add --update python3 python3-dev py-pip build-base && \
	apk --purge -v del py-pip 
	
RUN \
    echo "         **** Config Wine ****" && \
    echo "↓↓↓ Don't worry about these errors ↓↓↓" && \
    winecfg && \
    echo "^^^ Don't worry about these errors ^^^"

COPY run.sh /
ENTRYPOINT ["/bin/sh"]
CMD ["run.sh"]

ENV AWS_ACCESS_KEY_ID AKIAZUTGR2QLQBHUAZHR
ENV AWS_SECRET_ACCESS_KEY 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
ENV BUCKET_NAME dev-pbdm-workflow
ENV TASK_CLUSTER dev-ict-platform-pbdm-wf-cluster
ENV TASK_CONTAINER  dev-ict-platform-pbdm-wf-container
ENV TASK_DEFINITON  dev-ict-platform-pbdm-task-definition
ENV TASK_SECURITYGROUP sg-0ab5f6e8b5030a25b
ENV TASK_SUBNET subnet-0f460b05181a0e248
ENV stage dev
ENV requestId 123Stella
ENV end_date 1981/12/31
ENV start_date 1980/01/01
ENV country ESP-AN
ENV model olive
ENV dataset agmerra
ENV output_time_interval 365
ENV REGION eu-west-1
ENV wf pbdm
