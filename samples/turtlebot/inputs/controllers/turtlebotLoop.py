"""
Author: Jnaneshwar Das <jnaneshwar.das@gmail.com> 
testing looping behavior across a set of waypoints using offboard control
"""

import rospy
import math
import numpy
import sys
import tf
import random

from mavros_msgs.msg import State
from geometry_msgs.msg import PoseStamped, Point, Quaternion, Twist
from nav_msgs.msg import Odometry
from kobuki_msgs.msg import BumperEvent

class TestLoop:
    curr_odom = Odometry()
    des_vel = Twist()
    bumper = BumperEvent()

    def __init__(self, this_turtlebot):
        rospy.init_node('turtlebot_InfiniteWalk', anonymous=True)
        vel_pub = rospy.Publisher('/turtlebot'+ str(this_turtlebot + 1) + '/mobile_base/commands/velocity', Twist, queue_size=10)
        rospy.Subscriber('/mavros'+ str(this_turtlebot + 1) + '/odom', Odometry, callback=self.odom_cb)
        rate = rospy.Rate(10)  # Hz
        rate.sleep()

        while not rospy.is_shutdown():
	    linearX =(random.random() - 1) 
	    angularZ = (random.random() - 1) * .75  
	    self.des_vel.linear.x = linearX
	    self.des_vel.angular.z = angularZ
            vel_pub.publish(self.des_vel)
            rate.sleep()


    def odom_cb(self, msg):
        self.curr_odom = msg

    def bumper_cb(self, msg):
	self.bumper = msg

if __name__ == "__main__":
    TestLoop(int(sys.argv[1]))

