FROM python

RUN apt-get update && \
    apt-get -y install ffmpeg

COPY ./OnyxVot/requirements.txt requirements.txt

RUN pip install --upgrade pip wheel setuptools \
 && pip install --upgrade -r requirements.txt

COPY OnyxVot ./OnyxVot
COPY TOKEN.json ./OnyxVot/TOKEN.json

WORKDIR ./OnyxVot

CMD ["python" , "./main.py"]