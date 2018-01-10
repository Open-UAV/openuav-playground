#!/bin/bash

#Django start server
python3 /django/manage.py makemigrations &> /dev/null
python3 /django/manage.py migrate &> /dev/null
python3 /django/manage.py runserver 0.0.0.0:31819 &> /dev/null &
#Django start server

#####################
#####################
## Run user script ##
#####################
#####################

/simulation/run_this.sh