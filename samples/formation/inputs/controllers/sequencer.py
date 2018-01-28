"""
Authors: Arjun Kumar and Jnaneshwar Das
testing sequencer
"""

import rospy
import subprocess
import os
import sys
import math
import tf
import time

from std_msgs.msg import Int8, Bool, Float64, Float64MultiArray, MultiArrayLayout, MultiArrayDimension
from std_srvs.srv import Empty


class TestSequence:

    command = Float64MultiArray()
    command.layout = MultiArrayLayout()
    command.layout.dim = [MultiArrayDimension()]

    def __init__(self, NUM_UAV):

        global status

        self.command.layout.dim[0].label = 'command'
        self.command.layout.dim[0].size = 3
        self.command.layout.dim[0].stride = 3*8
        self.command.layout.data_offset = 0

        #testing circle  data = [x, y, r, n]; n - sequence number
        self.command.data = [0,0,0,1]

        status = [Int8() for i in range(NUM_UAV)]
        dummyStatus = [Int8() for i in range(NUM_UAV)]

        for i in range(NUM_UAV):
            dummyStatus[i].data = 0

        sum_stat = Int8()
        sum_stat.data = 0

        #subscribing to each uav's status
        for i in range(NUM_UAV):
            exec('def status_cb'+str(i)+'(msg): status['+str(i)+'] = msg' )
            rospy.Subscriber('/sequencer/status'+str(i), Int8, callback = eval('status_cb'+str(i)))


        rospy.init_node('sequencer_test', anonymous=True)

        print "INIT\n"

        pub = rospy.Publisher('/sequencer/command', Float64MultiArray, queue_size = 10)
        rospy.Subscriber('/sequencer/status', Float64MultiArray, callback = self.status_cb)

        rate = rospy.Rate(10)  # Hz
        rate.sleep()

        #wait to all drones to connect to the sequencer
        nc = pub.get_num_connections()
        while nc < NUM_UAV:
            nc = pub.get_num_connections()
            rate.sleep()


        print 'num_connections = '+ str(nc)
        print 'publishing - \n'+ str(self.command)
        pub.publish(self.command)
        sys.stdout.flush()


        while not rospy.is_shutdown():
            for i in range(NUM_UAV):
                sum_stat.data = sum_stat.data + status[i].data
            if sum_stat.data == self.command.data[3] * NUM_UAV:
                self.command.data = [0,0,40,2]
                pub.publish(self.command)
                print 'published circle'
                print status
            sum_stat.data = 0
            dummy_flag = False
            for j in range(NUM_UAV):
                dummy_flag = dummyStatus[j].data!=status[j].data or dummy_flag
        if dummy_flag:
            print 'DUMMY FLOP'
            print status
            dummyStatus = status
        sys.stdout.flush()


def status_cb(self, msg):
    self.status = msg


if __name__ == "__main__":
    TestSequence(int(sys.argv[1]))
