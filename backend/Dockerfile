FROM python:3.6
RUN apt-get update && apt-get install -f -y postgresql-client
RUN apt-get install -y imagemagick
COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY alembic.ini manage.py vobla tests alembic /
WORKDIR .
