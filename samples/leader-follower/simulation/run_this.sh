#!/bin/bash
export DISPLAY=:0 
source /root/.profile
source /simulation/inputs/parameters/swarm.sh
source /opt/ros/kinetic/setup.bash
source ~/catkin_ws/devel/setup.bash
cp /simulation/inputs/world/cityterrain.world /root/src/Firmware/Tools/sitl_gazebo/worlds/empty.world
cp /simulation/inputs/setup/posix_sitl_multibase.launch /root/src/Firmware/launch/
cp /simulation/inputs/setup/swarm.sh /root/src/Firmware/Tools/
rm /simulation/outputs/*.csv

#Xvfb :1 -screen 0 1600x1200x16  &
#export DISPLAY=:1.0

echo "Setup..."
python /simulation/inputs/setup/testCreateUAVSwarm.py $num_uavs & 
sleep 20

echo "arming"
python /simulation/inputs/setup/testArmAll.py $num_uavs &> /dev/null &
sleep 1

python /simulation/inputs/controllers/test_1_Loop.py $LOOP_EDGE $ALTITUDE 1 0 $DIST_THRESHOLD &> /dev/null &
sleep 2

for((i=1;i<$num_uavs;i+=1))
do
    one=1
sleep 3   
python /simulation/inputs/controllers/test_3_Follow.py $(( i + one)) $i  $(( i + one)) $FOLLOW_D_GAIN &> /dev/null &
done

sleep 2
roslaunch cob_people_object_detection_tensorflow cob_people_object_detection_tensorflow-front.launch &> /dev/null &

sleep 5
echo "Measures..."
python /simulation/inputs/measures/measureInterRobotDistance.py $num_uavs 1 &> /dev/null &
roslaunch rosbridge_server rosbridge_websocket.launch ssl:=false &> /dev/null &
rosrun web_video_server web_video_server _port:=80 _server_threads:=100 &> /dev/null &
tensorboard --logdir=/simulation/outputs/ --port=8008 &> /dev/null &
roslaunch opencv_apps general_contours.launch  image:=/uav_2_camera/image_raw_front debug_view:=false &> /dev/null &
python /simulation/inputs/measures/testGroundTruthTracker.py 1 2 &> /dev/null &


sleep 1

for((i=1;i<=$num_uavs;i+=1))
do
        /usr/bin/python -u /opt/ros/kinetic/bin/rostopic echo -p /mavros$i/local_position/odom > /simulation/outputs/uav$i.csv &
    done

/usr/bin/python -u /opt/ros/kinetic/bin/rostopic echo -p /measure > /simulation/outputs/measure.csv &



    sleep $duration_seconds
    cat /simulation/outputs/measure.csv | awk -F',' '{sum+=$2; ++n} END { print sum/n }' > /simulation/outputs/average_measure.txt

