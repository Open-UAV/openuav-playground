# demonstration of the best of dronekit (takeoff, missions, discrete commands) and mavros (offboard position and velocity control visual-servoing)
  

import rospy
from mavros_msgs.msg import State
from geometry_msgs.msg import PoseStamped, Point, Quaternion
import math
import numpy
import sys
import tf
import dronekit

class DroneKitMavrosDemo:
    curr_pose = PoseStamped()
    waypointIndex = 0
    distThreshold = 0.5
    sim_ctr = 1
    des_pose = PoseStamped()
    isReadyToFly = False

    def __init__(self, H,V,uav_prefix,yaw, connectionString):
        self.vehicle = dronekit.connect(connectionString, wait_ready=True)
        q = tf.transformations.quaternion_from_euler(0, 0, yaw)
        self.locations = numpy.matrix([[H, H, V, q[0], q[1], q[2], q[3]],
                                       [-H, H, V, q[0], q[1], q[2], q[3]],
                                       [-H, -H, V, q[0], q[1], q[2], q[3]],
                                       [H, -H, V, q[0], q[1], q[2], q[3]],
                                       ])
        print self.locations
        print '/mavros'+ uav_prefix + '/setpoint_position/local'
        rospy.init_node('offboard_test', anonymous=True)
        pose_pub = rospy.Publisher('/mavros'+ uav_prefix + '/setpoint_position/local', PoseStamped, queue_size=10)
        rospy.Subscriber('/mavros'+ uav_prefix + '/local_position/pose', PoseStamped, callback=self.mocap_cb)
        rospy.Subscriber('/mavros'+ uav_prefix + '/state', State, callback=self.state_cb)

        rate = rospy.Rate(10)  # Hz
        rate.sleep()
        self.des_pose = self.copy_pose(self.curr_pose)
        shape = self.locations.shape

        while not rospy.is_shutdown():
            print self.sim_ctr, shape[0], self.waypointIndex
            if self.waypointIndex is shape[0]:
                self.waypointIndex = 0
                self.sim_ctr += 1

            if self.isReadyToFly:
                des_x = self.locations[self.waypointIndex, 0]
                des_y = self.locations[self.waypointIndex, 1]
                des_z = self.locations[self.waypointIndex, 2]
                self.des_pose.pose.position.x = des_x
                self.des_pose.pose.position.y = des_y
                self.des_pose.pose.position.z = des_z

                self.des_pose.pose.orientation.x = self.locations[self.waypointIndex, 3]
                self.des_pose.pose.orientation.y = self.locations[self.waypointIndex, 4]
                self.des_pose.pose.orientation.z = self.locations[self.waypointIndex, 5]
                self.des_pose.pose.orientation.w = self.locations[self.waypointIndex, 6]

                curr_x = self.curr_pose.pose.position.x
                curr_y = self.curr_pose.pose.position.y
                curr_z = self.curr_pose.pose.position.z

                azimuth = math.atan2(0-curr_y, 20-curr_x)
                quaternion = tf.transformations.quaternion_from_euler(0, 0, azimuth)
                print quaternion
                self.des_pose.pose.orientation.x = quaternion[0]
                self.des_pose.pose.orientation.y = quaternion[1]
                self.des_pose.pose.orientation.z = quaternion[2]
                self.des_pose.pose.orientation.w = quaternion[3]



                dist = math.sqrt((curr_x - des_x)*(curr_x - des_x) + (curr_y - des_y)*(curr_y - des_y) + (curr_z - des_z)*(curr_z - des_z))
                if dist < self.distThreshold:
                    self.waypointIndex += 1

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

    def mocap_cb(self, msg):
        # print msg
        self.curr_pose = msg

    def state_cb(self,msg):
        print msg.mode
        if(msg.mode=='OFFBOARD'):
            self.isReadyToFly = True
            print "readyToFly"

    def arm_and_takeoff(self, aTargetAltitude):
        """
        Arms vehicle and fly to aTargetAltitude.
        """
        print "Basic pre-arm checks"
        # Don't try to arm until autopilot is ready
        while not vehicle.is_armable:
            print " Waiting for vehicle to initialise..."
            time.sleep(1)

        print "Arming motors"
        # Copter should arm in GUIDED mode
        vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = True

        # Confirm vehicle armed before attempting to take off
        while not vehicle.armed:
            print " Waiting for arming..."
            time.sleep(1)

        print "Taking off!"
        vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
        #  after Vehicle.simple_takeoff will execute immediately).
        while True:
            print " Altitude: ", vehicle.location.global_relative_frame.alt
            # Break and return from function just below target altitude.
            if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
                print "Reached target altitude"
                break
            time.sleep(1)


if __name__ == "__main__":

    dronekitMavros = DroneKitMavrosDemo(float(sys.argv[1]), float(sys.argv[2]), sys.argv[3], float(sys.argv[4]), sys.argv[5])
    dronekit.arm_and_takeoff(20)



