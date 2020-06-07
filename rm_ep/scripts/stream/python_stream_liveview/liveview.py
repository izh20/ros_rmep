#coding=utf-8

import sys
sys.path.append('../decoder/output/')
sys.path.append('../../connection/network/')
if int(sys.version[0]) > 2:
    PY3 = True
else:
    PY3 = False

if PY3:
    import libh264decoder
    import opus_decoder
else:
    from ctypes import *
    libh264decoder = cdll.LoadLibrary('libh264decoder.cpython-36m-aarch64-linux-gnu.so')
    opus_decoder = cdll.LoadLibrary('opus_decoder.cpython-36m-aarch64-linux-gnu.so')

import threading
import time
import numpy as np

import signal
from PIL import Image as PImage
import cv2

import pyaudio
import robot_connection
import enum
import queue
from kcf import Tracker , MessageItem
# from cv_bridge import CvBridge,CvBridgeError
# from sensor_msgs.msg import Image
# import rospy
# import jetson.inference
# import jetson.utils



class ConnectionType(enum.Enum):
    WIFI_DIRECT = 1
    WIFI_NETWORKING = 2
    USB_DIRECT = 3


class RobotLiveview(object):
    WIFI_DIRECT_IP = '192.168.2.1'
    WIFI_NETWORKING_IP = ''
    USB_DIRECT_IP = '192.168.42.2'
        
    def __init__(self,type ,connection_type = ConnectionType.WIFI_DIRECT):
        #self.connection = robot_connection.RobotConnection()
        self.connection = type
        
        self.connection_type = connection_type

        self.video_decoder = libh264decoder.H264Decoder()
        libh264decoder.disable_logging()

        self.audio_decoder = opus_decoder.opus_decoder() 

        self.video_decoder_thread = threading.Thread(target=self._video_decoder_task)
        self.video_decoder_msg_queue = queue.Queue(64)
        self.video_display_thread = threading.Thread(target=self._video_display_task)
        self.video_read_thread = threading.Thread(target=self._video_read_task)
        self.video_track_thread = threading.Thread(target=self._video_track_task)

        self.audio_decoder_thread = threading.Thread(target=self._audio_decoder_task)
        self.audio_decoder_msg_queue = queue.Queue(32)
        self.audio_display_thread = threading.Thread(target=self._audio_display_task)

        self.command_ack_list = []

        self.is_shutdown = False #默认连接上去了
        self.image = np.zeros((1280,680,3),np.uint8)

        #self.track_message = MessageItem.getMessage()
    def open(self):
        if self.connection_type is ConnectionType.WIFI_DIRECT:
            self.connection.update_robot_ip(RobotLiveview.WIFI_DIRECT_IP)
        elif self.connection_type is ConnectionType.USB_DIRECT:
            self.connection.update_robot_ip(RobotLiveview.USB_DIRECT_IP)
        elif self.connection_type is ConnectionType.WIFI_NETWORKING:
            robot_ip = self.connection.get_robot_ip(timeout=10)  
            if robot_ip:
                self.connection.update_robot_ip(robot_ip)
            else:
                print('Get robot failed')
                return False
        self.is_shutdown = not self.connection.open()
        
    def close(self):
        self.is_shutdown = True
        self.video_decoder_thread.join()
        self.video_display_thread.join()
        self.video_read_thread.join()
        self.video_track_thread.join()

        self.audio_decoder_thread.join()
        self.audio_display_thread.join()
        #self.connection.close()

    def display(self):
        self.command('command;')
        time.sleep(1)
        self.command('audio on;')
        time.sleep(1)
        self.command('stream on;')
        time.sleep(1)
        self.command('stream on;')

        # self._cap = cv2.VideoCapture(f'tcp://192.168.42.2:40921')
        # assert self._cap.isOpened(),'failed to connect to video stream'
        # while True:
        #     ok ,frame = self._cap.read()
        #     assert ok,'can not receive frame (stream end?)'
        #     cv2.imshow("frame",frame)
        #     cv2.waitKey(1)


        #self.video_decoder_thread.start()
        #self.video_display_thread.start()
        #self.video_read_thread.start()
        #self.video_track_thread.start()

        #self.audio_decoder_thread.start()
        #self.audio_display_thread.start()

        print('display!')

    def command(self, msg):
        # TODO: TO MAKE SendSync()
        #       CHECK THE ACK AND SEQ
        self.connection.send_data(msg)


    def _h264_decode(self, packet_data):
        res_frame_list = []
        frames = self.video_decoder.decode(packet_data)
        for framedata in frames:
            (frame, w, h, ls) = framedata
            if frame is not None:
                frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
                frame = (frame.reshape((h, int(ls / 3), 3)))
                frame = frame[:, :w, :]
                res_frame_list.append(frame)

        return res_frame_list

    def _video_decoder_task(self):
        package_data = b''

        self.connection.start_video_recv()

        while not self.is_shutdown: 
            buff = self.connection.recv_video_data()
            if buff:
                package_data += buff
                if len(buff) != 1460:
                    for frame in self._h264_decode(package_data):
                        try:
                            self.video_decoder_msg_queue.put(frame, timeout=2)
                        except Exception as e:
                            if self.is_shutdown:
                                break
                            print('video decoder queue full')
                            continue
                    package_data=b''

        self.connection.stop_video_recv()

    def _video_display_task(self):
        while not self.is_shutdown: 
            try:
                frame = self.video_decoder_msg_queue.get(timeout=2)
            except Exception as e:
                if self.is_shutdown:
                    break
                print('video decoder queue empty')
                continue
            image = PImage.fromarray(frame)
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            cv2.imshow("Liveview", img)
            cv2.waitKey(1)
    
    def _video_read_task(self):
        while not self.is_shutdown: 
            try:
                frame = self.video_decoder_msg_queue.get(timeout=2)
                #print("frame:",type(frame))  #<class 'numpy.ndarray'>
            except Exception as e:
                if self.is_shutdown:
                    break 
                print('video decoder queue empty')
                continue
            image = np.array(PImage.fromarray(frame)) 
            self.image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # frame = self.bridge.cv2_to_imgmsg(self.image,encoding="bgr8")
            # self.image_pub.publish(frame)
            # cv2.imshow("Liveview", self.image)
            # cv2.waitKey(1)
            #print("reading image",type(self.image),self.image.shape)
            

    def read(self):
        return not self.is_shutdown , self.image

   


    def _video_track_task(self,track_type='KCF'):
        time.sleep(2)
        fps=0
        gCapStatus, gFrame = self.read()
        print(type(gFrame))
        #img = cv2.cvtColor(gFrame, cv2.COLOR_RGB2BGR)
        print("按 n 选择下一帧，按 y 选取当前帧")
        while True:
            if (gCapStatus == False):
                print("捕获帧失败")
                quit()
            _key = cv2.waitKey(0) & 0xFF
            #print("key:",_key,"  n:",ord('n'),"  y",ord('y'))
            if(_key == ord('n')):
                gCapStatus,gFrame = self.read()
            if(_key == ord('y')):
                break

            cv2.imshow("pick frame",gFrame)
        # 框选感兴趣区域region of interest
        cv2.destroyWindow("pick frame")
        gROI = cv2.selectROI("ROI frame",gFrame,False)
        if (not gROI):
            print("空框选，退出")
            quit()
        # 初始化追踪器
        gTracker = Tracker(tracker_type=track_type)
        gTracker.initWorking(gFrame,gROI)

        # 循环帧读取，开始跟踪
        while True:
            timer = cv2.getTickCount()
            gCapStatus, gFrame = self.read()
            if(gCapStatus):
                
                _item = gTracker.track(gFrame)
                # Display tracker type on frame
                cv2.putText(_item.getFrame(), track_type+" Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2)
                # Display FPS on frame
                cv2.putText(_item.getFrame(), "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2)
                cv2.imshow("track result",_item.getFrame())
                if _item.getMessage():
                    # 打印跟踪数据
                    print(_item.getMessage(),type(_item.getMessage()))
                    
                else:
                    # 丢失，重新用初始ROI初始
                    print("丢失，重新使用初始ROI开始")
                    gTracker = Tracker(tracker_type=track_type)
                    gTracker.initWorking(gFrame, gROI)

                _key = cv2.waitKey(1) & 0xFF
                if (_key == ord('q')) | (_key == 27):
                    break
                if (_key == ord('r')) :
                    # 用户请求用初始ROI
                    print("用户请求用初始ROI")
                    gTracker = Tracker(tracker_type=track_type)
                    gTracker.initWorking(gFrame, gROI)
            else:
                print("捕获帧失败")
                quit()
            fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

    def _audio_decoder_task(self):
        package_data = b''

        self.connection.start_audio_recv()

        while not self.is_shutdown: 
            buff = self.connection.recv_audio_data()
            if buff:
                package_data += buff
                if len(package_data) != 0:
                    output = self.audio_decoder.decode(package_data)
                    #print("audio_output",output) bytes
                    if output:
                        try:
                            self.audio_decoder_msg_queue.put(output, timeout=2)
                        except Exception as e:
                            if self.is_shutdown:
                                break
                            print('audio decoder queue full')
                            continue
                    package_data=b''

        self.connection.stop_audio_recv()

    def _audio_display_task(self):

        p = pyaudio.PyAudio()

        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=48000,
                        output=True)

        while not self.is_shutdown: 
            try:
                output = self.audio_decoder_msg_queue.get(timeout=2)#将音频数据从队列中取出
            except Exception as e:
                if self.is_shutdown:
                    break
                print('audio decoder queue empty')
                continue
            stream.write(output)

        stream.stop_stream()
        stream.close()


def test():
    connect = robot_connection.RobotConnection('192.168.42.2')
    connect.open()
    robot = RobotLiveview(connect)
    #rospy.init_node('rmep_base',anonymous=True)
    #rate = rospy.Rate(37)
    def exit(signum, frame):
        print("signum:",signum)
        robot.close()

    signal.signal(signal.SIGINT, exit)#SIGINT 中断进程
    signal.signal(signal.SIGTERM, exit)#SIGTERM 软件中止信号

    #robot.open()
    robot.display()


# if __name__ == '__main__':
#     test()
