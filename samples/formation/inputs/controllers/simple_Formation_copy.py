"""
Authors: Arjun Kumar <karjun@seas.upenn.edu> and Jnaneshwar Das <jnaneshwar.das@gmail.com>
Testing simple formation control
"""

import rospy
import subprocess
import os
import sys
import math
import tf
import time

from std_msgs.msg import Float64, Float64MultiArray, Int8
from std_srvs.srv import Empty

from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, CommandTOL, SetMode, ParamGet, ParamSet, ParamPull
from sensor_msgs.msg import NavSatFix
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose, PoseStamped, PoseWithCovarianceStamped, Vector3, Point, Quaternion, Twist, TwistStamped


# UAV'S NUMBERED 0 -> NUM_UAV - 1
# MAKE SURE this_uav feed follows this scheme in run_this.sh
# /mavros topics follow 1 -> NUM_UAV
# Notes
#	-random drones not initializing, cant consistently recreate issue 
#	-commands get to velocity control and scramble
#	-need to completely swap to global 
#	-is there a heartbeat like dronekit?
 
class TestFormation: 
		
    isReadyToFly = False
    command = Float64MultiArray()
    command.data = [0,0,0,-1]
    status = Int8()
    status.data = -1
    convergence = 0

    def __init__(self, this_uav, NUM_UAV, D_GAIN):
	
	print 'init'	
	print 'this uav = ' + str(this_uav)
	print 'num uav = ' + str(NUM_UAV)

    	global cur_pose 
	global cur_state
	global cur_vel
	global cur_globalPose	

	cur_pose = [PoseStamped() for i in range(NUM_UAV)]
	cur_globalPose = [Odometry() for i in range(NUM_UAV)]
    	cur_state = [State() for i in range(NUM_UAV)]
    	cur_vel =  [TwistStamped() for i in range(NUM_UAV)]
  
	des_pose = PoseStamped() 	
	des_vel = TwistStamped()
	des_vel.header.frame_id = "map"	

        rospy.init_node('offboard_test'+str(this_uav), anonymous=True)
	rate = rospy.Rate(100) #Hz
	
	mode_proxy = rospy.ServiceProxy('mavros'+str(this_uav + 1)+'/set_mode' ,SetMode)
	arm_proxy = rospy.ServiceProxy('mavros'+str(this_uav + 1)+'/cmd/arming', CommandBool)
	paramPull_proxy = rospy.ServiceProxy('mavros'+str(this_uav+1)+'/param/pull', ParamPull)
	paramGet_proxy = rospy.ServiceProxy('mavros'+str(this_uav+1)+'/param/get', ParamGet)
	paramSet_proxy = rospy.ServiceProxy('mavros'+str(this_uav+1)+'/param/set', ParamSet)
	

	print('paramPull - \n' + str(paramPull_proxy(True)))
	#print('rospy_getParam-COM_ARM_AUTH\n'+ str(rospy.get_param('/mavros'+str(this_uav+1)+'/param/COM_ARM_AUTH')))
	print('paramGet MAV_TYPE - \n' + str(paramGet_proxy("MAV_TYPE")))
	print('______________________________________________________________________________')
	#generating subscribers to each drone
	for i in range(NUM_UAV):
    		exec('def position_cb'+ str(i) +'(msg): cur_pose['+ str(i) +'] = msg')	
		exec('def globalPosition_cb'+str(i)+'(msg): cur_globalPose['+ str(i) +'] = msg')
		exec('def velocity_cb'+ str(i) +'(msg): cur_vel['+ str(i) +'] = msg')
		exec('def state_cb'+ str(i) +'(msg): cur_state['+ str(i) +'] = msg')
		rospy.Subscriber('/mavros'+ str(i + 1) + '/local_position/pose', PoseStamped, callback= eval('position_cb'+ str(i)))
		rospy.Subscriber('/mavros'+ str(i + 1) + '/global_position/local', TwistStamped, callback= eval('globalPosition_cb'+str(i)))
        	rospy.Subscriber('/mavros'+ str(i + 1) + '/state', State, callback= eval('state_cb'+str(i)))
		rospy.Subscriber('/mavros'+ str(i + 1) + '/local_position/velocity', TwistStamped, callback=eval('velocity_cb'+ str(i)))

	#suscribe to sequencer
	rospy.Subscriber('/sequencer/command', Float64MultiArray, callback = self.command_cb)
        #publish status to sequencer
	status_pub = rospy.Publisher('/sequencer/status'+str(this_uav), Int8, queue_size = 10)
	#publish position to mav
	pose_pub = rospy.Publisher('/mavros'+ str(this_uav + 1) + '/setpoint_position/local', PoseStamped, queue_size = 10)
	#publish velocity to mav
	vel_pub = rospy.Publisher('/mavros'+str(this_uav + 1) + '/setpoint_velocity/cmd_vel', TwistStamped, queue_size = 10)
 
	#GOTO initial holding pattern command = [0,0,25,0]
	des_pose = cur_pose[this_uav]
	des_pose.pose.position.x = 10 * math.sin((this_uav * 2 * math.pi) / NUM_UAV)
	des_pose.pose.position.y = 10 * math.cos((this_uav * 2 * math.pi) / NUM_UAV)
	des_pose.pose.position.z = 20
	pose_pub.publish(des_pose)
	status_pub.publish(self.status)

	#....fix....double subscribe to status, check and set status in callback?
        while cur_state[this_uav].mode != 'OFFBOARD' and not cur_state[this_uav].armed:
		mode_sent = False
		success = False
		pose_pub.publish(des_pose)		
		while not mode_sent:
			rospy.wait_for_service('mavros'+str(this_uav + 1)+'/set_mode', timeout = None)
			try:
				mode_sent =  mode_proxy(1,'OFFBOARD')
			except rospy.ServiceException as exc:
				print exc
			rate.sleep()	
		while not success:
			rospy.wait_for_service('mavros'+str(this_uav + 1)+'/cmd/arming', timeout = None)
			try: 	
				success =  arm_proxy(True)
			except rospy.ServiceException as exc:
				print exc
			rate.sleep()
	
	print 'mode_sent - ' + str(mode_sent)
	print 'arm_sent - ' + str(success)
	print 'armed?'
	rate.sleep()
	print cur_state[this_uav].armed
	print cur_state[this_uav].mode

	#wait for sequencer to connect to /sequencer/status# 
	nc = status_pub.get_num_connections()
	print 'num_connections = ' +str(nc) 
	sys.stdout.flush()
	while nc == 0:
		nc = status_pub.get_num_connections()
		rate.sleep()

	print 'num_connections = ' + str(nc)
	sys.stdout.flush()
	rate.sleep()

	#MAIN LOOP
	print 'Loop INIT Time  - ' + str(time.clock())
        while not rospy.is_shutdown():

	    #pose_pub.publish(des_pose)
	    self.convergence =  math.sqrt(math.pow(des_pose.pose.position.x-cur_pose[this_uav].pose.position.x,2)+math.pow(des_pose.pose.position.y-cur_pose[this_uav].pose.position.y,2)+math.pow(des_pose.pose.position.z-cur_pose[this_uav].pose.position.z,2))
	    
	    if self.convergence < .5 and self.status != Int8(self.command.data[3]):
		self.status = Int8(self.command.data[3])
		print 'Status Set - '+ str(self.status) + '  time - '+ str(time.clock())
		print 'Current Pose - ' + str(cur_pose[this_uav].pose)
		status_pub.publish(self.status)
	    if self.command.data[3] > -1 and self.command.data[3] < 4:
            	des_pose.pose.position.x = self.command.data[0] + self.command.data[2]*math.sin((this_uav * 2 * math.pi)/NUM_UAV)
            	des_pose.pose.position.y = self.command.data[1] + self.command.data[2]*math.cos((this_uav * 2 * math.pi)/NUM_UAV)
	    	des_pose.pose.position.z = 25
		pose_pub.publish(des_pose)
	    if self.command.data[3] > 3:
		des_vel.twist.linear.x = (this_uav - cur_globalPose[this_uav].pose.pose.position.x) 
		des_vel.twist.linear.y = (this_uav - cur_globalPose[this_uav].pose.pose.position.y)
		des_vel.twist.linear.z = 0
		vel_pub.publish(des_vel)
	    rate.sleep()
		#azimuth = math.atan2(self.leader_pose.pose.position.y-self.curr_pose.pose.position.y, self.leader_pose.pose.position.x-self.curr_pose.pose.position.x)
                #quaternion = tf.transformations.quaternion_from_euler(0, 0, azimuth)
                #self.des_pose.pose.orientation.x = quaternion[0]
                #self.des_pose.pose.orientation.y = quaternion[1]
                #self.des_pose.pose.orientation.z = quaternion[2]
                #self.des_pose.pose.orientation.w = quaternion[3]

    def copy_pose(self, pose):
        pt = pose.pose.position
        quat = pose.pose.orientation
        copied_pose = PoseStamped()
        copied_pose.header.frame_id = pose.header.frame_id
        copied_pose.pose.position = Point(pt.x, pt.y, pt.z)
        copied_pose.pose.orientation = Quaternion(quat.x, quat.y, quat.z, quat.w)
        return copied_pose

    def state_cb(self, msg):
	self.curr_state = msg

    def command_cb(self, msg):
	self.command = msg
	print 'COMMAND callback ----- ' + str(msg)
	print 'COMMAND CALLBACK TIME  - '+ str(time.clock())
	sys.stdout.flush()
	



	
if __name__ == "__main__":
    TestFormation(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]))



