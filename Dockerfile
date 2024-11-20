FROM python:3.10-slim

WORKDIR /usr/src

# set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

ENV FLASK_APP=climbz

# copy run.py, code and DB
COPY ./climbz ./climbz
# COPY ./instance ./instance
COPY ./entrypoint.sh ./entrypoint.sh
COPY ./wsgi.py ./wsgi.py
COPY ./gunicorn_config.py ./gunicorn_config.py
RUN ["chmod", "+x", "./entrypoint.sh"]

# run the application
ENTRYPOINT ["/usr/src/entrypoint.sh"]