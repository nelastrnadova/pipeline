#!/usr/bin/env bash

#check yaml is supplied
#run setup py, which will create DB based on yaml
#run cron py, which will cron the db and see if it can run something
#run wsgi py, which will listen to HTTP requests and create a new pipeline instance/get pipeline output or state