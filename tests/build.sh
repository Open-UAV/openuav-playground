#!/usr/bin/env bash
cd ./tests
docker-compose up --detach
cd ../
docker network ls
docker images
docker ps
pwd
docker run -it --net=tests_default --name=openuavapp_x${3:-`date +%s`} -v /tmp/.X11-unix:/tmp/.X11-unix -v /home/travis/build/harishanand95/openuav-playground/samples/leader-follower:/simulation -e DISPLAY=:0 --entrypoint "/home/setup.sh" dreamslab/openuavapp_openuav:latest
