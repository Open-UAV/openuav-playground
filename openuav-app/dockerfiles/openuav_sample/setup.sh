#!/bin/bash

#Django start server
python3 /django/manage.py makemigrations &> /dev/null
python3 /django/manage.py migrate &> /dev/null
python3 /django/manage.py runserver 0.0.0.0:31819 &> /dev/null &
#Django start server

cd /wetty/wetty
node app.js -p 3000 &> /dev/null &
cd

## Previous clean-up
rm -rf /root/src/Firmware/Tools/sitl_gazebo/models/f450-tmp-*
rm -f /root/src/Firmware/posix-configs/SITL/init/lpe/f450-tmp-*
rm -f /root/src/Firmware/launch/posix_sitl_multi_tmp.launch

#####################
#####################
## Run user script ##
#####################
#####################

su term
/simulation/run_this.sh