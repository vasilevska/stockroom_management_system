FROM python:3

RUN mkdir -p /opt/src/auth
WORKDIR /opt/src/auth

COPY auth/app.py ./app.py
COPY auth/configuration.py ./configuration.py
COPY auth/models.py ./models.py
COPY auth/requirements.txt ./requirements.txt
COPY auth/permissions.py ./permissions.py

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./app.py"]