FROM python:3.10-slim

WORKDIR /usr/src

# set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/requirements.txt
RUN pip install -r requirements.txt

# copy run.py, code and DB
COPY ./run.py /usr/src/run.py
COPY ./climbz /usr/src/climbz
COPY ./instance /usr/src/instance

# run the application
CMD ["python", "run.py"]