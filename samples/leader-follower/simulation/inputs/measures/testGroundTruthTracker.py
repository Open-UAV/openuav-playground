#! /usr/bin/python

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
from geometry_msgs.msg import PointStamped, PoseStamped, Point, Quaternion
import sys
import image_geometry 
from sensor_msgs.msg import Image, CameraInfo
import tf
import math 
from gazebo_msgs.srv import GetLinkState 
from gazebo_msgs.msg import LinkState
import numpy as np
from scipy.linalg import expm

class GroundTruthTracker():

    def rot_euler(self, v, xyz):
        for theta, axis in zip(xyz, np.eye(3)):
            v = np.dot(np.array(v), expm(np.cross(np.eye(3), axis*-theta)))
        return v
    def image_callback(self,msg):
        try:
            cv2_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except CvBridgeError, e:
            print(e)
        else:
	    rospy.wait_for_service('/gazebo/get_link_state')
	    leader = self.model_info_prox("f450-tmp-1::base_link" , "")
	    follower = self.model_info_prox("f450-tmp-2::base_link" , "")
            x = leader.link_state.pose.position.x - follower.link_state.pose.position.x
	    y = leader.link_state.pose.position.y - follower.link_state.pose.position.y
	    dist = math.sqrt(x*x + y*y)

	    z = leader.link_state.pose.position.z - follower.link_state.pose.position.z 
            azimuth = math.atan2(leader.link_state.pose.position.y - follower.link_state.pose.position.y, leader.link_state.pose.position.x - follower.link_state.pose.position.x)
	    elevation = math.atan2(dist, -z)

            _rot_leader = leader.link_state.pose.orientation
	    _rot_this = follower.link_state.pose.orientation
            euler_this = tf.transformations.euler_from_quaternion((_rot_this.x, _rot_this.y, _rot_this.z, _rot_this.w)) 
            euler_leader = tf.transformations.euler_from_quaternion((_rot_leader.x, _rot_leader.y, _rot_leader.z, _rot_this.w))

	    euler = (azimuth - euler_this[2])*180/math.pi
            trans = self.rot_euler((x,y,z),euler_this) 
            print x,y,z,euler_this[0]*180/math.pi , euler_this[1]*180/math.pi, euler_this[2]*180/math.pi 
            print trans
            #uav_center = self.model.project3dToPixel((dist, y*10.0, x*10.0))
	    cv2.circle(cv2_img, (int((-euler+30)*640/60), int(240)), 20, (0, 0, 255))
            self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv2_img, "bgr8"))
	    self.rate.sleep()	
    def __init__(self, leader_uav, this_uav):
        rospy.init_node('ground_truth_uav_tracker')
        self.rate = rospy.Rate(100)  # Hz
	self.model_info_prox = rospy.ServiceProxy('/gazebo/get_link_state', GetLinkState)

	self.bridge = CvBridge()
	self.tfl = tf.TransformListener()

        image_topic = "/uav_2_camera/image_raw_front/detections_image"
        rospy.Subscriber(image_topic, Image, self.image_callback)
        rospy.Subscriber('/uav_2_camera/camera_info'    , CameraInfo, self.info_cb)

	rospy.Subscriber('/mavros' + leader_uav + '/local_position/pose', PoseStamped, callback=self.leader_cb)
        rospy.Subscriber('/mavros' + this_uav + '/local_position/pose', PoseStamped, callback=self.this_cb)

        self.image_pub = rospy.Publisher("/uav_2_camera/image_raw_front/ground_truth_tracking", Image)
	self.model = image_geometry.PinholeCameraModel()
        rospy.spin()

    def this_cb(self, msg):
        self.this_pose = msg

    def leader_cb(self, msg):
        self.leader_pose = msg

    def info_cb(self, msg):
	self.model.fromCameraInfo(msg)

    def qv_mult(self, q1, v1):
        v1 = tf.transformations.unit_vector(v1)
        q2 = list(v1)
        q2.append(0.0)
        return tf.transformations.quaternion_multiply(tf.transformations.quaternion_multiply(q1, q2),tf.transformations.quaternion_conjugate(q1))[:3]

if __name__ == "__main__":
    GroundTruthTracker(sys.argv[1], sys.argv[2])


