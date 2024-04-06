#!/bin/bash

echo "FLASK_DEBUG: $FLASK_DEBUG"

if [ "$FLASK_DEBUG" -eq 0 ]; then
    DEBUGPY="-m debugpy --listen 0.0.0.0:5670"
else
    DEBUGPY=""
fi

python $DEBUGPY -m flask run --host=0.0.0.0 --port=5000