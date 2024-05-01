#!/bin/bash

DEBUG=${FLASK_DEBUG:-0}

if [ "$DEBUG" -eq 0 ]; then
    DEBUGPY="-m debugpy --listen 0.0.0.0:5670"
else
    DEBUGPY=""
fi

python $DEBUGPY -m flask run --host=0.0.0.0 --port=5000