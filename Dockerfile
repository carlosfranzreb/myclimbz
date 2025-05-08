FROM python:3.10-slim

WORKDIR /usr/src

# set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install dependencies
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --upgrade pip
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

ENV FLASK_APP=myclimbz

# copy code
COPY ./myclimbz ./myclimbz
COPY ./entrypoint.sh ./entrypoint.sh
COPY ./wsgi.py ./wsgi.py
COPY ./gunicorn_config.py ./gunicorn_config.py
RUN ["chmod", "+x", "./entrypoint.sh"]

# run the application
ENTRYPOINT ["/usr/src/entrypoint.sh"]