FROM python:3

RUN mkdir -p /opt/src/store_migrations
WORKDIR /opt/src/store_migrations

COPY store/migrate.py ./migrate.py
COPY store/configuration.py ./configuration.py
COPY store/models.py ./models.py
COPY store/deamon/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./migrate.py"]