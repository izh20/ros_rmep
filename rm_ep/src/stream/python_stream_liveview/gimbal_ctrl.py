import sys
sys.path.append('../../connection/network/')
import robot_connection
import enum
import cv2
from liveview import RobotLiveview
from chassis_ctrl import Chassis_Ctrl
import threading
import time
class ConnectionType(enum.Enum):
    WIFI_DIRECT = 1
    WIFI_NETWORKING = 2
    USB_DIRECT = 3
class Gimbal_Ctrl(object):
    # WIFI_DIRECT_IP = '192.168.2.1'
    # WIFI_NETWORKING_IP = ''
    # USB_DIRECT_IP = '192.168.42.2'
    def __init__(self,type):
        #self.connection = robot_connection.RobotConnection('192.168.2.1')
        #self.connection.open()
        self.connect = type
        # self.SDK()
        self.set_mode('free')#chassis_lead
        
        #self.speed_control(0,0)
        #self.relate_position_control(50,40)

    def SDK(self):
        self.connect.send_data('command')
        print('send data to robot   : command')
        recv = self.connect.recv_ctrl_data(5)
        print('recv data from robot : %s'%recv)

    def set_mode(self,mode):
        '''
        1 云台跟随地盘模式  chassis_lead
        2 底盘跟随云台模式  gimbal_lead
        3 自由模式         free
        '''
        command = 'robot mode '+mode
        print('input',command)
        self.connect.send_data(command)
        recv = self.connect.recv_ctrl_data(5)
        print('robot mode: %s'%recv)

    def set_follow_chassis_offset(degree):
        '''
        描述：在＂云台跟随底盘模式下＂，当底盘左右旋转时，云台始终与底盘保持指定夹角
        类型：设置类
        范例：云台跟随底盘
        参数：degree(int):[-180,180]度
        '''
        

    def speed_control(self,p_speed,y_speed):
        '''
        描述：控制云台运动速度
        参数：p (float:[-450, 450]) ：pitch 轴速度，单位 °/s
            y (float:[-450, 450]) ：yaw 轴速度，单位 °/s
        注意：只有在gimbal_lead模式下　y_speed才会生效
        '''
        command = 'gimbal speed p ' + str(p_speed) + ' y ' + str(y_speed)
        print('input:',command)
        self.connect.send_data(command)
        recv = self.connect.recv_ctrl_data(5)
        print('recv data from robot : %s'%recv)

    def relate_position_control(self,p,y,p_speed=200,y_speed=200):
        '''
        描述：控制云台运动到指定位置，坐标轴原点为当前位置
        参数：p (float:[-55, 55]) ：pitch 轴角度，单位 °
            y (float:[-55, 55]) ：yaw 轴速度，单位 °
            vp (float:[0, 540]) ：pitch 轴运动速速，单位 °/s
            vy (float:[0, 540]) ：yaw 轴运动速度，单位 °/s
        注意：只有在gimbal_lead模式下　y_speed才会生效
        '''
        command = 'gimbal move p ' + str(p) + ' y ' + str(y) + ' vp ' +str(p_speed) + ' vy ' + str(y_speed)
        print('input',command)
        self.connect.send_data(command)
        recv = self.connect.recv_ctrl_data(5)
        print('recv data from robot : %s'%recv)

class PID:
    def __init__(self, P, I, D):
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.sample_time = 0.00
        self.current_time = time.time()
        self.last_time = self.current_time
        self.clear()
    def clear(self):
        self.SetPoint = 0.0
        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0
        self.int_error = 0.0
        self.output = 0.0
    def update(self, feedback_value):
        error = self.SetPoint - feedback_value
        self.current_time = time.time()
        delta_time = self.current_time - self.last_time
        delta_error = error - self.last_error
        if (delta_time >= self.sample_time):
            self.PTerm = self.Kp * error#比例
            self.ITerm += error * delta_time#积分
            self.DTerm = 0.0
            if delta_time > 0:
                self.DTerm = delta_error / delta_time#微分
            self.last_time = self.current_time
            self.last_error = error
            self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)
        return self.output

    def setSampleTime(self, sample_time):
        self.sample_time = sample_time

def test():
    connection = robot_connection.RobotConnection('192.168.42.2')
    connection.open()
    #robot = RobotLiveview(connection)
    #robot.open()
    #robot.display()
    gimbal_ctrl = Gimbal_Ctrl(connection)
    #chassis_ctrl = Chassis_Ctrl(connection)
    
    

#test()