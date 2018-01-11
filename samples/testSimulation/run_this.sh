#!/bin/bash

source /simulation/inputs/parameters/swarm.sh
source /opt/ros/kinetic/setup.bash
source ~/catkin_ws/devel/setup.bash

## Previous clean-up
rm -rf /root/src/Firmware/Tools/sitl_gazebo/models/f450-tmp-*
rm -f /root/src/Firmware/posix-configs/SITL/init/lpe/f450-tmp-*
rm -f /root/src/Firmware/launch/posix_sitl_multi_tmp.launch

# world setup #
cp /simulation/inputs/world/empty.world /root/src/Firmware/Tools/sitl_gazebo/worlds/empty.world
cp /simulation/inputs/models/f450-1.sdf /root/src/Firmware/Tools/sitl_gazebo/models/f450-1/f450-1.sdf

rm -f /simulation/outputs/*.csv
echo "Setup..."
python /simulation/inputs/setup/testCreateUAVSwarm.py $num_uavs &> /dev/null &
sleep 15
python /simulation/inputs/setup/testArmAll.py $num_uavs &> /dev/null &
sleep 1
python /simulation/inputs/controllers/test_1_Loop.py $LOOP_EDGE $ALTITUDE 1 0 &> /dev/null &


for((i=1;i<$num_uavs;i+=1))
do
    one=1
    python /simulation/inputs/controllers/test_3_Follow.py $(( i + one)) $i $FOLLOW_D_GAIN &> /dev/null &
    sleep 1
done
roslaunch rosbridge_server rosbridge_websocket.launch ssl:=false &> /dev/null &

echo "Measures..."
python /simulation/inputs/measures/measureInterRobotDistance.py $num_uavs 1 &> /dev/null &


rosrun web_video_server web_video_server _port:=80 _server_threads:=100 &> /dev/null &
tensorboard --logdir=/simulation/outputs/ --port=8008 &> /dev/null &
roslaunch opencv_apps general_contours.launch  image:=/uav_2_camera/image_raw_front debug_view:=false &> /dev/null &

for((i=1;i<=$num_uavs;i+=1))
do
        /usr/bin/python -u /opt/ros/kinetic/bin/rostopic echo -p /mavros$i/local_position/odom > /simulation/outputs/uav$i.csv &
    done
    /usr/bin/python -u /opt/ros/kinetic/bin/rostopic echo -p /measure > /simulation/outputs/measure.csv &


    sleep $duration_seconds
    cat /simulation/outputs/measure.csv | awk -F',' '{sum+=$2; ++n} END { print sum/n }' > /simulation/outputs/average_measure.txt

