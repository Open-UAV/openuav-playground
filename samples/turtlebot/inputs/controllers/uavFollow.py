"""
Authors: Arjun Kumar <karjun@seas.upenn.edu> and Jnaneshwar Das <jnaneshwar.das@gmail.com>
testing follower(leader) controller using offboard position control 
"""

import rospy
import math
import sys
import tf

from mavros_msgs.msg import State
from geometry_msgs.msg import PoseStamped, Point, Quaternion, TwistStamped
from nav_msgs.msg import Odometry

class TestFollow:
    des_pose = PoseStamped()
    curr_pose = PoseStamped()
    turtle_odom = Odometry()

    isReadyToFly = False

    def __init__(self, this_uav, lead_turtlebot, D_GAIN):

        rospy.init_node('offboard_test', anonymous=True)

        pose_pub = rospy.Publisher('/mavros'+ str(this_uav + 1) + '/setpoint_position/local', PoseStamped, queue_size=10)
        rospy.Subscriber('/mavros'+ str(this_uav + 1) + '/local_position/pose', PoseStamped, callback=self.follower_cb)
        rospy.Subscriber('/mavros'+ str(this_uav + 1) + '/state', State, callback=self.state_cb)
	rospy.Subscriber('/turtlebot'+ str(lead_turtlebot + 1) + '/odom', Odometry, callback=self.turtle_cb)

        rate = rospy.Rate(100)  # Hz
        rate.sleep()
        self.des_pose = self.copy_pose(self.curr_pose)

        while not rospy.is_shutdown():
            if self.isReadyToFly:
                self.des_pose.pose.position.x = self.turtle_odom.pose.pose.position.x + 3 #+ (self.leader_vel.twist.linear.x*D_GAIN)
                self.des_pose.pose.position.y = self.turtle_odom.pose.pose.position.y + (this_uav) #+ (self.leader_vel.twist.linear.y*D_GAIN)
		self.des_pose.pose.position.z = 10 + (this_uav*3) 
	
		if self.poseStampedXYTwoNorm(self.turtle_odom.pose, self.curr_pose) > .5:
			azimuth = math.atan2(self.turtle_odom.pose.pose.position.y-self.curr_pose.pose.position.y, self.turtle_odom.pose.pose.position.x-self.curr_pose.pose.position.x)
                	quaternion = tf.transformations.quaternion_from_euler(0, 0, azimuth)
                	self.des_pose.pose.orientation.x = quaternion[0]
                	self.des_pose.pose.orientation.y = quaternion[1]
                	self.des_pose.pose.orientation.z = quaternion[2]
                	self.des_pose.pose.orientation.w = quaternion[3]
	    #print self.turtle_odom
	    #print self.des_pose
            pose_pub.publish(self.des_pose)
            rate.sleep()
    def poseStampedXYTwoNorm(self, ps1, ps2):
    	return  math.sqrt(math.pow(ps1.pose.position.x-ps2.pose.position.x,2) + math.pow(ps1.pose.position.y-ps2.pose.position.y,2))

    def copy_pose(self, pose):
        pt = pose.pose.position
        quat = pose.pose.orientation
        copied_pose = PoseStamped()
        copied_pose.header.frame_id = pose.header.frame_id
        copied_pose.pose.position = Point(pt.x, pt.y, pt.z)
        copied_pose.pose.orientation = Quaternion(quat.x, quat.y, quat.z, quat.w)
        return copied_pose

    def follower_cb(self, msg):
        self.curr_pose = msg

    def turtle_cb(self, msg):
        self.turtle_odom = msg

    def state_cb(self,msg):
        print msg.mode
        if(msg.mode=='OFFBOARD'):
            self.isReadyToFly = True
            print "readyToFly"

if __name__ == "__main__":
    TestFollow(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]))
