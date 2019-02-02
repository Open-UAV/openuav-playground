Project website: https://openuav.us

Here are the instructions for installing the simulation testbed on an Ubuntu 16.04 machine with an NVIDIA graphics card. Our test box is a Lenovo C730 with an NVIDIA GeForce RTX 2070 graphics card. Ensure that you have correct drivers installed by searching for and running the appropriate binary. For us, it was NVIDIA-Linux-x86_64-410.93.run found at https://www.nvidia.com/Download/index.aspx?lang=en-us . 


- curl -sSL https://get.docker.com/ | sh
- sudo usermod -aG $USER docker
- sudo systemctl start docker
- sudo apt-get install docker-compose 
- git clone https://github.com/Open-UAV/openuav-playground
- xhost +local:  

Do understand the implications of sharing xserver. 
- 
- curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
- sudo apt-get update
- sudo apt-get install -y nvidia-docker
- pip install nvidia-docker-compose
- cd ~/openuav-playground/openuavapp  
- nvidia-docker-compose build 

This will take a while. 

Once the build is complete, you will be able to run simulations and see it by running gzclient and rqt in the simulaiton container. 
Example: 
- nvidia-docker run -dit --net=openuavapp_default --name=openuavapp_x${3:-`date +%s`} -v /tmp/.X11-unix:/tmp/.X11-unix -v /home/jdas/openuav-playground/samples/formation/:/simulation -e DISPLAY=:0 --entrypoint "/home/setup.sh" openuavapp_openuav

Assume the assigned simulation container name is openuav_x12345678 , you can verify yours by using docker ps 

- docker exec -it openuav_x12345678 bash 
- <container-id># source /usr/share/gazebo-7/setup.sh 
- <container-id># gzclient
  
Gazebo client will pop up on your host. 
  

 
