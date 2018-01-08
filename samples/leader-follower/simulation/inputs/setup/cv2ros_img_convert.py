#!/usr/bin/env python
import roslib
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


class ImageConverter:

    def __init__(self):
        self.image_pub = rospy.Publisher("/objects/image_raw",Image)

        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber("/object_detection/detections_image",Image,self.callback)

    def callback(self,msg):
        try:
            print dir(msg)
            img = self.bridge.cv2_to_imgmsg(msg.data, encoding='8UC3')
            self.image_pub.publish(img)
        except CvBridgeError as e:
            print(e)

def main(args):
    ic = ImageConverter()
    rospy.init_node('image_converter', anonymous=True)
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)
