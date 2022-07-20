FROM python:3

RUN mkdir -p /opt/src/deamon
WORKDIR /opt/src/deamon

COPY store/deamon/app.py ./app.py
COPY store/deamon/configuration.py ./configuration.py
COPY store/deamon/models.py ./models.py
COPY store/deamon/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./app.py"]