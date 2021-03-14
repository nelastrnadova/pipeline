#!/usr/bin/env bash

#check yaml is supplied
#convert yaml to json
python3 setup.py
python3 import_json.py "$1"
python3 cron.py &
python3 wsgi.py &