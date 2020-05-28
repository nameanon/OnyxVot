FROM python

COPY OnyxVot ./OnyxVot

RUN pip install -U pip wheel setuptools \
&& pip install -r ./OnyxVot/requirements.txt


COPY TOKEN.txt ./OnyxVot/TOKEN.txt

WORKDIR ./OnyxVot

CMD ["python" , "./main.py"]
