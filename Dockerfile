FROM python:3.8.5

RUN export http_proxy="http://192.168.2.110:1081" && https_proxy="http://192.168.2.110:1081" && \
    apt-get update -y && apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info -y

ADD requirements.txt /root/

RUN pip3 install --no-cache-dir -r /root/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    rm /root/requirements.txt

ADD simsun.ttc /usr/share/fonts/simsun.ttc
ADD simsun.ttc ~/.fonts/simsun.ttc

ENV LC_ALL=zh_CN.utf8
ENV LANG=zh_CN.utf8
ENV LANGUAGE=zh_CN.utf8

CMD ["python", "/usr/src/app/run.py"]
