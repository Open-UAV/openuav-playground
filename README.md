Project website: https://openuav.us

- install docker (https://www.docker.com/docker-ubuntu)
- git clone https://github.com/Open-UAV/openuav-playground
- cd openuav-playground/openuav-app
- mkdir dockerfiles/openuav_sample/lib
- cp -r /lib/modules/$(uname -r) dockerfiles/openuav_sample/lib
- xhost +local: # Do understand the implications of this command
- docker-compose up

