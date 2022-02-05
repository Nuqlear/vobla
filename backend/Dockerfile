FROM python:3.8

RUN apt-get update && apt-get install -f -y postgresql-client
RUN apt-get install -y imagemagick

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY alembic.ini manage.py /
COPY vobla /vobla
COPY tests /tests
COPY alembic /alembic

WORKDIR /
