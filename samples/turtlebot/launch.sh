#launch the patrol sim
#!/bin/bash
nvidia-docker run -it --net=openuavapp_default --name=openuavapp_TURTLE${3:-`date +%s`} -v /tmp/.X11-unix:/tmp/.X11-unix -v /home/junk/openuav_modified/openuav-playground/samples/turtlebot/:/simulation -e DISPLAY=:0 --entrypoint "/home/setup.sh" openuavapp_openuav_turtlebot

docker ps


