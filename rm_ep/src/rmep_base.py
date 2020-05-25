
# license removed for brevity
import sys
import rospy
sys.path.append('stream/python_stream_liveview/')
sys.path.append('connection/network')
sys.path.append('stream/decoder/output/')
sys.path.append('~/catkin_workspace/install/lib/python3/dist-packages')
import cv2
from ep_camera import EpCamera
import robot_connection
from chassis_ctrl import Chassis_Ctrl
from gimbal_ctrl import Gimbal_Ctrl,PID
from face_detect import face_detect,face_match
import threading
from cv_bridge import CvBridge,CvBridgeError
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped,Quaternion
from vision_msgs.msg import Detection2D,Detection2DArray
from roborts_msgs.msg import GimbalAngle
import time
import math
from jetcam.csi_camera import CSICamera
import numpy as np
import signal

def QuaternionMsgFromEuler(roll,pitch,yaw):
    q=Quaternion()
    cosRoll = math.cos(roll)
    sinRoll = math.sin(roll)

    cosPit = math.cos(pitch)
    sinPit = math.sin(pitch)

    cosYaw = math.cos(yaw)
    sinYaw = math.sin(yaw)


    q.w = cosRoll*cosPit*cosYaw + sinRoll*sinPit*sinYaw
    q.x = sinRoll*cosPit*cosYaw - cosRoll*sinPit*sinYaw
    q.y = cosRoll*sinPit*cosPit + sinRoll*cosPit*sinYaw 
    q.z = cosRoll*cosPit*sinYaw - sinRoll*sinPit*cosYaw
    return q
class RmepCamera(object):
    def __init__(self,type):
        self.liveview = EpCamera(type)
        self.csi_img = np.zeros((1280,720,3),np.uint8)
        self.ep_image = np.zeros((1280,720,3),np.uint8)
        self.image_pub = rospy.Publisher("image_topic",Image,queue_size=10) #ep视频流信息
        self.csi_image_pub = rospy.Publisher("csi_topic",Image,queue_size=10)#nano上的csi视频流信息
        self.face_detect_pub = rospy.Publisher("face_detect",Detection2D,queue_size=10)#人脸roi信息
        self.bridge = CvBridge()
        self.detMsg = Detection2D()
        self.face_roi_thread = threading.Thread(target=self.get_face_roi_task)
        
        #self.camera = CSICamera(width=640, height=360, capture_width=1280, capture_height=720, capture_fps=30)
        
        self.open()
        
        

    def close(self):
        self.liveview.close()
        self.face_roi_thread.join()
        #self.camera.running = False
    
    def open(self):
        self.liveview.open()
        self.face_roi_thread.start()
        #self.camera.running = True
        #self.camera.observe(self.csi_callback,names='value')
        print("camera_node_open")

    def csi_callback(self,change):
        try:
            #print('reading csi image')
            self.csi_img = change['new']
            csi_frame = self.bridge.cv2_to_imgmsg(self.csi_img,encoding="bgr8")
            self.csi_image_pub.publish(csi_frame)
            # cv2.imshow("Liveview", self.csi_img)
            # cv2.waitKey(1)
        except CvBridgeError as e:
            print('error: ',e) 

    def read_csi_image(self):
        return self.csi_img

    def ImagePub(self):
        try:

            gCapStatus,self.ep_image = self.liveview.read()
            
            #print('shape:',ep_image.shape)
            frame = self.bridge.cv2_to_imgmsg(self.ep_image,encoding="bgr8")
            self.image_pub.publish(frame)
            
        except CvBridgeError as e:
            print('error: ',e)
    
    def get_face_roi_task(self):
        roi_rate = rospy.Rate(1)
        while True:
            try:
                flag,image = self.liveview.read()
                self.roi = face_detect(image)
                self.detMsg.bbox.size_x = self.roi['left']
                self.detMsg.bbox.size_y = self.roi['top']
                self.detMsg.bbox.center.x = self.roi['top']+self.roi['height']/2
                self.detMsg.bbox.center.y = self.roi['left']+self.roi['width']/2
                self.detMsg.bbox.center.theta = 0.0
                self.detMsg.source_img.width = self.roi['width']
                self.detMsg.source_img.height = self.roi['height']
                self.face_detect_pub.publish(self.detMsg)
                print("roi",self.roi['width'])
            except TypeError as e:
                flag,image = self.liveview.read()
                print(e)
            roi_rate.sleep()
            #time.sleep(1)

class RmepChassis(object):
    def __init__(self,type):
        self.chassis_ctrl = Chassis_Ctrl(type)
        self.odom_pub = rospy.Publisher("odom_topic",Odometry,queue_size=10)
        self.q=Quaternion()
        self.odom_ = Odometry()
        self.odom_.header.frame_id = "odom"
        self.odom_.child_frame_id = "base_link"
    def close(self):
        self.chassis_ctrl.close()
    
    
    def Odom_pub(self):
        #print(self.chassis_ctrl._attitude_yaw,self.chassis_ctrl._position_x)
        current_time = rospy.get_rostime()
        self.odom_.header.stamp = current_time
        self.odom_.pose.pose.position.x = self.chassis_ctrl._position_x
        self.odom_.pose.pose.position.y = self.chassis_ctrl._position_y
        self.odom_.pose.pose.position.z = 0.0
        self.q = QuaternionMsgFromEuler(0,0,self.chassis_ctrl._attitude_yaw/360.0*math.pi)
        self.odom_.pose.pose.orientation = self.q
        self.odom_.twist.twist.linear.x = self.chassis_ctrl._speed_x
        self.odom_.twist.twist.linear.y = self.chassis_ctrl._speed_y
        self.odom_.twist.twist.angular.z = self.chassis_ctrl._rate_z
        self.odom_pub.publish(self.odom_)

class RmepGimbal(object):
    def __init__(self,type):
        self.gimbal = Gimbal_Ctrl(type)
        rospy.Subscriber('cmd_gimbal_angle',GimbalAngle,self.cmd_callback)
        self.gimbal_angle = GimbalAngle()
        self.pid = PID(0.5 ,0,0)


    def cmd_callback(self,gimbal_angle):
        self.gimbal_angle = gimbal_angle
        #print('yaw:',self.gimbal_angle.yaw_angle,'pitch:',self.gimbal_angle.pitch_angle)
        yaw_out = self.pid.update(self.gimbal_angle.yaw_angle)
        pit_out = self.pid.update(self.gimbal_angle.pitch_angle)
        #self.gimbal.relate_position_control(0,-self.gimbal_angle.yaw_angle*180/3.14,10,10)
        #print('yaw_out',yaw_out)
        self.gimbal.speed_control(pit_out,yaw_out)

def main():
    WIFI_DIRECT_IP = '192.168.2.1'
    WIFI_NETWORKING_IP = ''
    USB_DIRECT_IP = '192.168.42.2'
    rospy.init_node('rmep_base',anonymous=True)
    connect = robot_connection.RobotConnection(USB_DIRECT_IP)
    connect.open()
    
    camera = RmepCamera(connect)
    gimbal = RmepGimbal(connect)
    #chassis = RmepChassis(connect)
    def exit(signum, frame):
        print("signum:",signum)
        connection.close()
        camera.close()

    signal.signal(signal.SIGINT, exit)#SIGINT 中断进程
    signal.signal(signal.SIGTERM, exit)#SIGTERM 软件中止信号

    rate = rospy.Rate(30)
    while not rospy.is_shutdown():
        camera.ImagePub()
        rate.sleep()
        
    
if __name__ == '__main__':
        main()
    
        

