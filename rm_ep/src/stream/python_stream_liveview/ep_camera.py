#coding=utf-8
import sys
sys.path.append('../decoder/output/')
sys.path.append('../../connection/network/')
import libh264decoder
import robot_connection
import cv2
import threading
import numpy as np
import time
import signal
class EpCamera(object):
    CAMERA_IP_USB_DIRECT = 'tcp://192.168.42.2:40921'
    CAMERA_IP_WIFI_DIRECT = 'tcp://192.168.2.1:40921'
    def __init__(self,type,compression = 0.35):
        self.connect = type
        self.compression = compression #视频分辨率压缩
        self._stream_on()
        libh264decoder.disable_logging()#禁止打印相关信息
        self._cap = cv2.VideoCapture(f'tcp://192.168.42.2:40921')
        assert self._cap.isOpened(),'failed to connect to video stream'
        # self._cap.set(3,int(1280*self.compression))#设置分辨率
        # self._cap.set(4,int(720*self.compression))
        self.fps = self._cap.get(cv2.CAP_PROP_FPS)
        self.ok , self.image = self._cap.read()
        self.read_thread = threading.Thread(target=self._read_task)
        

    def open(self):
        self.read_thread.start()
    
    def close(self):
        self.read_thread.join()

    def read(self):
        return self.ok,self.image

    def _stream_on(self):
        print("stream")
        self.connect.send_data('command')
        time.sleep(1)
        self.connect.send_data('stream on')
        time.sleep(1)
        self.connect.send_data('stream on')
        
        
    def _read_task(self):
        while True:
            self.ok , image = self._cap.read()
            self.image = cv2.resize(image,(int(image.shape[1]*self.compression),int(image.shape[0]*self.compression)),interpolation=cv2.INTER_CUBIC)
            assert self.ok,'can not receive frame(stream end?)'
            # cv2.imshow("frame",self.image)
            # cv2.waitKey(1)
            #print('fps:',self.fps)
def main():
    connection = robot_connection.RobotConnection('192.168.42.2')
    connection.open()
    camera = EpCamera(connection)
    camera.open()
    def exit(signum, frame):
        print("signum:",signum)
        connection.close()
        camera.close()

    signal.signal(signal.SIGINT, exit)#SIGINT 中断进程
    signal.signal(signal.SIGTERM, exit)#SIGTERM 软件中止信号


# main()