FROM python:3.6
RUN apt-get update && apt-get install -f -y postgresql-client
COPY vobla/ /vobla/
COPY tests/ /tests/
COPY alembic/ /alembic/
COPY manage.py requirements.txt alembic.ini /
WORKDIR .
RUN pip install -r requirements.txt
