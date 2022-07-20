FROM python:3

RUN mkdir -p /opt/src/admin
WORKDIR /opt/src/admin

COPY store/warehouse/app.py ./app.py
COPY store/warehouse/permissions.py ./permissions.py
COPY store/warehouse/configuration.py ./configuration.py
COPY store/admin/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./app.py"]