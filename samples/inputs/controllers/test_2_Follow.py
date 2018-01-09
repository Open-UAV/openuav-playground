"""
Author: Jnaneshwar Das <jnaneshwar.das@gmail.com> 
testing offboard positon control with a simple takeoff script
"""

import rospy
from mavros_msgs.msg import State
from geometry_msgs.msg import PoseStamped, Point, Quaternion
import sys


class TestFollow:
    curr_pose = PoseStamped()
    des_pose = PoseStamped()
    leader_pose = PoseStamped()
    isReadyToFly = False

    def __init__(self, this_uav,leader_uav, H):
        rospy.init_node('offboard_test', anonymous=True)

        pose_pub = rospy.Publisher('/mavros'+ this_uav + '/setpoint_position/local', PoseStamped, queue_size=10)

        rospy.Subscriber('/mavros'+ leader_uav + '/local_position/pose', PoseStamped, callback=self.leader_cb)
        rospy.Subscriber('/mavros'+ leader_uav + '/local_position/pose', PoseStamped, callback=self.follower_cb)
        rospy.Subscriber('/mavros'+ this_uav + '/state', State, callback=self.state_cb)

        rate = rospy.Rate(10)  # Hz
        rate.sleep()
        self.des_pose = self.copy_pose(self.curr_pose)

        while not rospy.is_shutdown():
            if self.isReadyToFly:
                self.des_pose.pose.position.x = self.leader_pose.pose.position.x 
                self.des_pose.pose.position.y = self.leader_pose.pose.position.y
                self.des_pose.pose.position.z = H
                self.des_pose.pose.orientation = self.leader_pose.pose.orientation

            pose_pub.publish(self.des_pose)
            rate.sleep()

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

    def leader_cb(self, msg):
        self.leader_pose = msg

    def state_cb(self,msg):
        print msg.mode
        if(msg.mode=='OFFBOARD'):
            self.isReadyToFly = True
            print "readyToFly"

if __name__ == "__main__":
    TestFollow(sys.argv[1], sys.argv[2], float(sys.argv[3]))

