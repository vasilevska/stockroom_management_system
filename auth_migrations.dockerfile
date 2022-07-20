FROM python:3

RUN mkdir -p /opt/src/auth_migrations
WORKDIR /opt/src/auth_migrations

COPY auth/migrate.py ./migrate.py
COPY auth/configuration.py ./conffiguration.py
COPY auth/models.py ./models.py
COPY auth/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./migrate.py"]