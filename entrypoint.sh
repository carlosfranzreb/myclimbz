#!/bin/bash

if [ "$FLASK_DEBUG" -eq 0 ]; then
    echo "Running in production mode"
    DEBUGPY="-m debugpy --listen 0.0.0.0:5670"
else
    echo "Running in debug mode"
    DEBUGPY=""
fi

python $DEBUGPY -m flask run --host=0.0.0.0 --port=5000