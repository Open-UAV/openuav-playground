#!/usr/bin/env bash
cd ./tests
docker-compose up --detach
cd ../
docker run -it --net=openuavapp_default --name=openuavapp_x${3:-`date +%s`} -v /tmp/.X11-unix:/tmp/.X11-unix -v /home/hanand/openuav-playground/samples/leader-follower:/simulation -e DISPLAY=:0 --entrypoint "/home/setup.sh" openuavapp_openuav
