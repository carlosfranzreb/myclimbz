#!/bin/bash

if [ "$CREATE_DB" -eq 1 ]; then
    if [ "$CLIMBZ_DB_URI" != "sqlite:///test_100.db" ]; then
        echo "Error: CLIMBZ_DB_URI must be set to 'sqlite:///test_100.db' when CREATE_DB is set to 1"
        exit 1
    fi
    python create_db.py --test
fi

if [ "$FLASK_DEBUG" -eq 0 ]; then
    DEBUGPY="-m debugpy --listen 0.0.0.0:5670"
else
    DEBUGPY=""
fi

python $DEBUGPY -m flask run --host=0.0.0.0 --port=5000