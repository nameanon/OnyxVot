FROM python

COPY OnyxVot ./OnyxVot

RUN apt-get update && \
    apt-get -y install ffmpeg

RUN pip install -U pip wheel setuptools \
&& pip install -r ./OnyxVot/requirements.txt


COPY TOKEN.txt ./OnyxVot/TOKEN.txt

WORKDIR ./OnyxVot

CMD ["python" , "./main.py"]
