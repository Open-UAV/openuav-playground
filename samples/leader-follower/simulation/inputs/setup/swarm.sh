#!/bin/bash
for NUM in $(seq $1)
do
	let PORT=$((140+$NUM))
	cp -r /root/src/Firmware/Tools/sitl_gazebo/models/f450-1 /root/src/Firmware/Tools/sitl_gazebo/models/f450-tmp-$NUM
	mv /root/src/Firmware/Tools/sitl_gazebo/models/f450-tmp-$NUM/f450-1.sdf /root/src/Firmware/Tools/sitl_gazebo/models/f450-tmp-$NUM/f450-tmp-$NUM.sdf
	sed -i "s/146/$PORT/g" /root/src/Firmware/Tools/sitl_gazebo/models/f450-tmp-$NUM/f450-tmp-$NUM.sdf 
	cp /root/src/Firmware/posix-configs/SITL/init/lpe/f450-1 /root/src/Firmware/posix-configs/SITL/init/lpe/f450-tmp-$NUM
	sed -i "s/146/$PORT/g" /root/src/Firmware/posix-configs/SITL/init/lpe/f450-tmp-$NUM
	sed -i "3,4s/2/$NUM/g" /root/src/Firmware/posix-configs/SITL/init/lpe/f450-tmp-$NUM
	sed -i "s/f450-1/f450-tmp-$NUM/g" /root/src/Firmware/Tools/sitl_gazebo/models/f450-tmp-$NUM/f450-tmp-$NUM.sdf
        sed -i "s/uav_camera/uav_$NUM\_camera/g" /root/src/Firmware/Tools/sitl_gazebo/models/f450-tmp-$NUM/f450-tmp-$NUM.sdf
 

done
touch  /root/src/Firmware/launch/posix_sitl_multi_tmp.launch

#Build launchfile from ground up
SOURCE="/root/src/Firmware/launch/posix_sitl_multibase.launch"
DEST="/root/src/Firmware/launch/posix_sitl_multi_tmp.launch"
sed -n 1,10p $SOURCE>>$DEST
OLD=1

#xy positions
for NUM in $(seq $1)
do
	sed -i "11s/x$OLD/x$NUM/g" $SOURCE
	sed -i "12s/y$OLD/y$NUM/g" $SOURCE
	sed -i "12s/$OLD/$NUM/g" $SOURCE
	sed -n 11,12p $SOURCE>>$DEST
	OLD=$NUM
done
sed -i "11s/x$NUM/x1/g" $SOURCE
sed -i "12s/y$NUM/y1/g" $SOURCE
sed -i "12s/$NUM/1/g" $SOURCE

sed -n 13,15p $SOURCE>>$DEST

OLD=1
#vehicle
for NUM in $(seq $1)
do
	sed -i "16s/$OLD/$NUM/g" $SOURCE
	sed -n 16p $SOURCE>>$DEST
	OLD=$NUM
done
sed -i "16s/$NUM/1/g" $SOURCE
sed -i "16s/f110/f450/g" $SOURCE
sed -n 17p $SOURCE>>$DEST
OLD=1
#rcs/sdf
for NUM in $(seq $1)
do
	sed -i "18,19s/$OLD/$NUM/g" $SOURCE
	sed -n 18,19p $SOURCE>>$DEST
	OLD=$NUM
done
sed -i "18,19s/$NUM/1/g" $SOURCE
sed -n 20,33p $SOURCE>>$DEST
OLD=1
#sitl
for NUM in $(seq $1)
do
	sed -i "34,36s/$OLD/$NUM/g" $SOURCE
	sed -n 34,36p $SOURCE>>$DEST
	OLD=$NUM
done
sed -i "34,36s/$NUM/1/g" $SOURCE
sed -n 37,47p $SOURCE>>$DEST
OLD=1
#spawn node
for NUM in $(seq $1)
do
	sed -i "48,50s/$OLD/$NUM/g" $SOURCE
	sed -n 48,50p $SOURCE>>$DEST
	OLD=$NUM
done
sed -i "48,50  s/$NUM/1/g" $SOURCE
sed -n 51p $SOURCE>>$DEST

OLD=1
#mavros node
for NUM in $(seq $1)
do
	echo $NUM
	sed -i "52s/$OLD/$NUM/g" $SOURCE
	sed -n 52p $SOURCE>>$DEST
	sed -i "53s/14$OLD/14$NUM/g" $SOURCE
	sed -i "60s/uav$OLD/uav$NUM/g" $SOURCE
	sed -n 53p $SOURCE>>$DEST
	sed -n 54p $SOURCE>>$DEST
	sed -i "55,57s/$OLD/$NUM/g" $SOURCE
	sed -n 55,57p $SOURCE>>$DEST
	sed -n 58,61p $SOURCE>>$DEST
	OLD=$NUM
done
sed -i "52s/$NUM/1/g" $SOURCE
sed -i "53s/14$NUM/141/g" $SOURCE
sed -i "55,57s/$NUM/1/g" $SOURCE
sed -n 62,62p $SOURCE>>$DEST

sed -i 's/px./px4/g' $SOURCE
sed -i 's/px./px4/g' $DEST
sed -i 's/f..0/f450/g' $SOURCE
sed -i 's/f..0/f450/g' $DEST


echo "$1 DRONES CREATED!"

