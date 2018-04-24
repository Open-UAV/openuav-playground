#!/bin/bash

#!/bin/bash

echo "++++++++INIT++++++++++"

source /simulation/inputs/parameters/swarm.sh
source /opt/ros/kinetic/setup.bash
source ~/catkin_ws/devel/setup.bash


## Previous clean-up
rm -rf /root/src/Firmware/Tools/sitl_gazebo/models/f450-tmp-*
rm -f /root/src/Firmware/posix-configs/SITL/init/lpe/f450-tmp-*
rm -f /root/src/Firmware/launch/posix_sitl_multi_tmp.launch

## world setup #
cp /simulation/inputs/world/empty.world /root/src/Firmware/Tools/sitl_gazebo/worlds/empty.world
cp /simulation/inputs/models/f450-1/f450-1.sdf /root/src/Firmware/Tools/sitl_gazebo/models/f450-1/f450-1.sdf
cp /simulation/inputs/setup/posix_sitl_openuav_swarm_base.launch /root/src/Firmware/launch/posix_sitl_openuav_swarm_base.launch

mkdir /simulation/outputs 
rm -f /simulation/outputs/*.csv
rm -f /simulation/outputs/*.txt
echo "Setup..." #>> /tmp/debug


python /simulation/inputs/setup/gen_gazebo_ros_spawn.py $num_uavs
python /simulation/inputs/setup/gen_px4_sitl.py $num_uavs
python /simulation/inputs/setup/gen_mavros.py $num_uavs

for((i=1;i<=$num_uavs;i+=1))
do
echo "px4 posix_sitl_multi_gazebo_ros$num_uavs.launch"
    echo "launching uav$i ..." >> /tmp/debug
    roslaunch px4 posix_sitl_multi_gazebo_ros$i.launch &> /dev/null &
    until rostopic echo /gazebo/model_states | grep -m1 f450-tmp-$i ; do : ; done
    roslaunch px4 posix_sitl_multi_px4_sitl$i.launch &> /dev/null &
    sleep 2
    roslaunch px4 posix_sitl_multi_mavros$i.launch &> /dev/null &
    until rostopic echo /mavros$i/state | grep -m1 "connected: True" ; do : ; done
    echo "launched uav$i ..." >> /tmp/debug
done

python /simulation/inputs/controllers/dostuff.py $num_uavs 1 &> /dev/null &

python /simulation/inputs/measures/measureInterRobotDistance.py $num_uavs 1 &> /dev/null &
rosrun web_video_server web_video_server _port:=80 _server_threads:=100 &> /dev/null &
roslaunch rosbridge_server rosbridge_websocket.launch ssl:=false &> /dev/null &


echo "Measures..."
roslaunch opencv_apps general_contours.launch  image:=/uav_2_camera_front/image_raw debug_view:=false &> /dev/null &

for((i=1;i<=$num_uavs;i+=1))
do
    /usr/bin/python -u /opt/ros/kinetic/bin/rostopic echo -p /mavros$i/local_position/odom > /simulation/outputs/uav$i.csv &
done

/usr/bin/python -u /opt/ros/kinetic/bin/rostopic echo -p /measure > /simulation/outputs/measure.csv &
sleep $duration_seconds
cat /simulation/outputs/measure.csv | awk -F',' '{sum+=$2; ++n} END { print sum/n }' > /simulation/outputs/average_measure.txt

