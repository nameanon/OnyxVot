FROM python

COPY OnyxVot ./OnyxVot

RUN apt-get update && \
    apt-get -y install ffmpeg

RUN pip install --upgrade pip wheel setuptools \
&& pip install --upgrade -r ./OnyxVot/requirements.txt


COPY TOKEN.json ./OnyxVot/TOKEN.json

WORKDIR ./OnyxVot

CMD ["python" , "./main.py"]
