FROM python:3

RUN mkdir -p /opt/src/customer
WORKDIR /opt/src/customer

COPY store/customer/app.py ./app.py
COPY store/customer/permissions.py ./permissions.py
COPY store/customer/configuration.py ./configuration.py
COPY store/customer/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./app.py"]