#coding=utf-8

import sys
sys.path.append('../../connection/network/')
import robot_connection
import enum
import threading
import signal
class rm_define(enum.Enum):
    chassis_pitch = 1
    chassis_roll = 2
    chassis_yaw = 3
    chassis_forward = 4
    chassis_translation = 5
    chassis_rotate = 6
    chassis_push_position = 7 #底盘信息流推送
    chassis_push_attitude = 8
    chassis_push_status = 9
    chassis_push_all = 10
    clockwise = 11
    anticlockwise = 12

class ConnectionType(enum.Enum):
    WIFI_DIRECT = 1
    WIFI_NETWORKING = 2
    USB_DIRECT = 3
class Chassis_Ctrl(object):
    WIFI_DIRECT_IP = '192.168.2.1'
    WIFI_NETWORKING_IP = ''
    USB_DIRECT_IP = '192.168.42.2'
    def __init__(self,type,control_mode = 'chassis_lead'):#gimbal_lead , free
        #self.connection = robot_connection.RobotConnection(WIFI_DIRECT_IP)
        self.control_mode = control_mode
        self.connection = type
        self.control_mode = control_mode #底盘控制模式
        self.SDK() #进入SDK模式
        self.set_mode(self.control_mode)
        self.get_mode()
        self._position_x = 0
        self._position_y = 0
        self._attitude_pitch = 0
        self._attitude_roll = 0
        self._attitude_yaw = 0
        self._speed_x = 0
        self._speed_y = 0
        self._rate_z = 0
        #self.move_with_speed()
        #self.set_wheel_speed(0,0,300,0)
        #print(self.get_attitude(rm_define.chassis_yaw))
        #print(self.get_position_based_power_on(rm_define.chassis_rotate))
        #self.get_chassis_speed()
        #self.get_status()
        self.push()#打开消息推送
        self.get_chassis_speed()
        self.chassis_msg_thread = threading.Thread(target=self.chassis_msg_task)
        self.chassis_msg_thread.start()
        # def exit(signum, frame):
        #     print("signum:",signum)``
        #     self.close()

        # signal.signal(signal.SIGINT, exit)#SIGINT 中断进程
        # signal.signal(signal.SIGTERM, exit)#SIGTERM 软件中止信号


    def SDK(self):
        self.connection.send_data('command')
        print('send data to robot   : command')
        recv = self.connection.recv_ctrl_data(5)
        print('recv data from robot : %s'%recv)
        


    def close(self):
        #self.connection.close()
        self.chassis_msg_task.join()


    def command(self, msg):
        # TODO: TO MAKE SendSync()
        #       CHECK THE ACK AND SEQ
        self.connection.send_data(msg)    


    def chassis_msg_task(self):
        while True:
            self.recv_push_task()
            recv = self.get_chassis_speed()
            try:
                self._speed_x = float(recv[0])
                self._speed_y = float(recv[1])
                self._rate_z = float(recv[2])
                print(self._speed_x,' ',self._speed_y,' ',self._rate_z)
            except ValueError:#有时候获取的数据有问题，需要重新获取
                recv = self.get_chassis_speed()
                print("error")
            


    def set_pwm_value(pwm_port_enum , output_percent):
        '''
        描述：设置pwm输出百分比，数值越大，在某一周期内高电平持续时间越长，该pwm基础频率为５０hz
        类型：设置类
        范例：灯的亮灭，舵机转动
        参数：pwm_port_enum(enum)：rm_define.pwm_all , rm_define.pwm[1-6]
            output_percent(int):[0,100]
        '''
        
    def set_follow_gimbal_offset(degree):
        '''
        描述：在＂底盘跟随云台模式下＂，当云台左右旋转时，底盘始终与云台保持指定夹角
        类型：设置类
        范例：底盘跟随云台
        参数：degree(int):[-180,180]度
        '''


    def set_trans_speed(speed=0.5):
        '''
        描述：设置底盘平移速率，默认平移速率为0.5m/s,数值越大，移动越快
        类型：设置类
        范例：倒车减速
        参数：speed(float):[0,3.5]
        '''
        

    def set_rotate_speed(speed=30):
        '''
        描述：设置底盘旋转速率，默认旋转速率时３０度/s,数值越大，移动越快
        类型：设置类
        参数：speed(int):[0,600]度/s
        '''

    def set_wheel_speed(self,lf_speed,rf_speed,lr_speed,rr_speed):
        '''
        描述：独立控制四个麦轮的转速，符合麦轮转动方向和速度的有效组合才会生效
        类型：执行类
        范例：Ｓ形倒退，跑圈
        参数：lf_speed(int):[-1000,1000]rpm
            rf_speed(int):[-1000,1000]rpm
            lr_speed(int):[-1000,1000]rpm
            rr_speed(int):[-1000,1000]rpm
        '''
        command = 'chassis wheel w2 '+str(lf_speed)+' w1 '+str(rf_speed)+' w3 '+str(rr_speed)+' w4 '+str(lr_speed)
        print('input:',command)
        self.connection.send_data(command)
        recv = self.connection.recv_ctrl_data(5)
        print('recv data from robot : %s'%recv)


    def move(degree):
        '''
        描述：控制底盘向指定方向平移　　
        类型：执行类
        范例：例如往返运动
        参数：degree(int):[-180,180]度
        '''
    
    def move_with_time(degree,time):
        '''
        描述：控制底盘向指定方向平移指定时长　　
        类型：执行类
        范例：交叉平移
        '''

    def move_with_distance(degree,distance):
        '''
        描述：控制底盘向指定方向平移指定距离
        类型：执行类
        范例：＂十＂字形走位
        参数：degree(int):[-180,180]度
            distance(float):[0,5]m
        '''
        
    def move_degree_with_speed(speed,degree):
        '''
        描述：控制底盘以指定的平移速率向指定方向平移
        类型：执行类
        范例：变速旋转
        参数：speed(float):[0,3.5]m/s
            degree(int):[-180,180]
        '''



    def rotate(direction_enum):
        '''
        描述：控制底盘向指定方向旋转
        类型：执行类
        范例：变速旋转
        参数：direction_enum(enum):
            rm_define.clockwise
            rm_define.anticlockwise
        '''

    def rotate_with_time(direction_enum,time):
        '''
        描述：控制底盘向指定方向旋转指定时长
        类型：执行类
        范例：云台底盘交叉旋转
        参数：direction_enum(enum):　rm_define.clockwise　，　rm_define.anticlockwise
            time(float):[0,20]s
        '''

    def rotate_with_degree(direction_enum,degree):
        '''
        描述：控制底盘向指定方向旋转指定角度
        类型：执行类
        范例：持续往返
        参数：direction_enum(enum):　rm_define.clockwise　，　rm_define.anticlockwise
            degree(int):[0,180]度
        '''

    
    def move_and_rotate(degree,direction):
        '''
        描述：控制底盘向指定方向平移的同时做旋转运动
        类型：执行类
        范例：＂８＂字形路径运动
        参数：degree(int):[-180,180]度
            direction_enum(enum):　rm_define.clockwise　，　rm_define.anticlockwise
        '''
    
    def move_with_speed(self,speed_x=0 , speed_y=0 , speed_rotation=0) :
        '''
        描述：控制底盘以指定速度在指定方向运动
        类型：执行类
        范例：刷锅运动
        参数：speed_x(float):[0.3.5]m/s
            speed_y(float):[0.3.5]m/s
            speed_rotation(int):[-600.600]m/s
        '''
        command = 'chassis speed x '+str(speed_x) +' y '+str(speed_y)+' z '+str(speed_rotation)
        print("input:",command)
        self.connection.send_data(command)
        recv = self.connection.recv_ctrl_data(5)
        print('recv data from robot : %s'%recv)
    
    def stop(self):
        '''
        描述：停止底盘的所有运动
        类型：执行类
        '''
        self.move_with_speed(0,0,0)

    def get_attitude(self,attitude_enum):#
        '''
        描述：以上电时刻底盘位置为基准，获取底盘当前yaw,pitch,roll
        类型：信息类
        范例：转向示意
        参数：attitude_enum: rm_define.chassis_yaw , rm_define.chassis_pitch , rm_define.chassis_roll
        return: degree(float)
        '''
        command = 'chassis attitude ?'
        print('input',command)
        self.connection.send_data(command)
        recv = self.connection.recv_ctrl_data(5)
        print('chassis attitude: %s'%recv)
        recv = recv.decode().split(" ")#对bytes数据进行解码成str数据
        print('chassis attitude:',recv)
        if attitude_enum is rm_define.chassis_yaw:
            degree = float(recv[2])
            return degree
        if attitude_enum is rm_define.chassis_roll:
            degree = float(recv[1])
            return degree
        if attitude_enum is rm_define.chassis_yaw:
            degree = float(recv[0])
            return degree



    def get_position_based_power_on(self,action_enum):
        '''
        描述：获取底盘当前位置坐标和朝向数据
        类型：信息类(变量型数据)
        范例：当前位置信息
        参数：action_enum(enum): rm_define.chassis_forward , rm_define.chassis_translation , rm_define.chassis_rotate
        return: position(float)
        '''
        command = 'chassis position ?'
        print('input',command)
        self.connection.send_data(command)
        recv = self.connection.recv_ctrl_data(5)
        print('chassis position: %s'%recv)
        recv = recv.decode().split(" ")#对bytes数据进行解码成str数据
        print('chassis position:',recv)
        try:
            if action_enum is rm_define.chassis_forward:
                position = float(recv[0])
                return position
            if action_enum is rm_define.chassis_translation:
                position = float(recv[1])
                return position
            if action_enum is rm_define.chassis_rotate:
                position = float(recv[2])
                return position
        except IndexError:
            print('list index out of range')


    def chassis_impact_detection(msg):
        '''
        描述：在行驶过程中，当底盘撞击到人，等障碍物，运行本函数
        类型：事件类
        范例：自我保护
        type: Event callback
        '''

    def is_impact():
        '''
        描述：在行驶过程中，检测到底盘撞击到人等障碍物会返回＂true",否则返回＂假＂
        范例：危险警报
        return: impact_status(bool)
        '''
        return self._impact_x or self._impact_y or self._impact_z




    def set_mode(self,mode):
        '''
        1 云台跟随地盘模式  chassis_lead
        2 底盘跟随云台模式  gimbal_lead
        3 自由模式         free
        '''
        command = 'robot mode '+mode
        print('input',command)
        self.connection.send_data(command)
        recv = self.connection.recv_ctrl_data(5)
        print('robot mode: %s'%recv)

    def get_mode(self):
        '''
        返回当前机器人的控制模式
        '''
        command = 'robot mode ?'
        print('input',command)
        self.connection.send_data(command)
        recv = self.connection.recv_ctrl_data(5)
        print('robot mode: %s'%recv)
    

    def chassis_position_control(distance_x,distance_y,degree_z,speed_xy,speed_z):
        '''
        描述:控制底盘运动到指定位置，坐标轴原点为当前位置
        distance_x (float:[-5, 5]): x 轴向运动距离，单位 m
        distance_y (float:[-5, 5]): y 轴向运动距离，单位 m
        degree_z (int:[-1800, 1800]): z 轴向旋转角度，单位 °
        speed_xy (float:(0, 3.5]): xy 轴向运动速度，单位 m/s
        speed_z (float:(0, 600]): z 轴向旋转速度， 单位 °/s
        '''
        command = 'chassis move x '+str(distance_x)+' y '+str(distance_y)

    def get_chassis_speed(self):
        '''
        描述：获取地盘速度信息
        返回：<x> <y> <z> <w1> <w2> <w3> <w4> ：[list] str
        x 轴向运动速度(m/s)，
        y 轴向运动速度(m/s)，
        z 轴向旋转速度(°/s)，
        w1 右前麦轮速度(rpm)，
        w2 左前麦轮速速(rpm)，
        w3 右后麦轮速度(rpm)，
        w4 左后麦轮速度(rpm)
        '''
        command = 'chassis speed ?'
        #print('input',command)
        self.connection.send_data(command)
        recv = self.connection.recv_ctrl_data(5)
        #print('chassis speed: %s'%recv)
        recv = recv.decode().split(" ")#对bytes数据进行解码成str数据
        #print('chassis speed:',recv)
        return recv

    def get_status(self):
        '''
        描述：获取底盘状态信息
        返回值：<static> <uphill> <downhill> <on_slope> <pick_up> <slip> <impact_x> <impact_y> <impact_z> <roll_over> <hill_static>
            static:是否静止
            uphill:是否上坡
            downhill:是否下坡
            on_slope:是否溜坡
            pick_up:是否被拿起
            slip:是否滑行
            impact_x:ｘ轴是否感应到撞击
            impact_y:y轴是否感应到撞击
            impact_z:z轴是否被感应到撞击
            roll_over:是否翻车
            hill_static:是否在坡上静止
        '''
        command = 'chassis status ?'
        print('input',command)
        self.connection.send_data(command)
        recv = self.connection.recv_ctrl_data(5)
        print('chassis status: %s'%recv)
        recv = recv.decode().split(" ")#对bytes数据进行解码成str数据
        print('chassis status:',recv)
        return recv

    def push(self,push_enum = rm_define.chassis_push_all,switch = 'on'):
        '''
        描述：打开／关闭底盘中相应属性的信息推送
        参数：push_enum(enum):rm_define.chassis_push_position 
                            rm_define.chassis_push_attitude 
                            rm_define.chassis_push_status 
                            rm_define.chassis_push_all
            status(str): on , off
        '''
        if push_enum is rm_define.chassis_push_position:
            command = 'chassis push position '+ switch + ' pfreq 30'
            print('input',command)
            self.connection.send_data(command)
        if push_enum is rm_define.chassis_push_attitude:
            command = 'chassis push attitude '+ switch + ' afreq 30'
            print('input',command)
            self.connection.send_data(command)
        if push_enum is rm_define.chassis_push_status:
            command = 'chassis push status '+ switch + ' sfreq 30'
            print('input',command)
            self.connection.send_data(command)
        if push_enum is rm_define.chassis_push_all:
            command = 'chassis push position '+ switch + ' pfreq 30 attitude ' + switch + ' afreq 30 status ' + switch + ' sfreq 30'
            print('input',command)
            self.connection.send_data(command)
        recv=self.connection.recv_push_data(5)
        print(recv)
        print('recv push data from robot : %s'%recv)
        while recv == None:
            self.push()
            print('push...')

    def recv_push_task(self,push_enum = rm_define.chassis_push_all):
        '''
        描述：当调用 push()　函数时，机器人会以设置的频率(默认30hz)向用户推送相应信息
        参数：push_enum(enum):rm_define.chassis_push_position 
                            rm_define.chassis_push_attitude 
                            rm_define.chassis_push_status 
                            rm_define.chassis_push_all
        '''
        
        if push_enum is rm_define.chassis_push_all:
            try:
                recv = self.connection.recv_push_data(5).decode().split(' ')
                #print(recv)
            
                self._position_x = float(recv[3])
                self._position_y = float(recv[4])
                self._attitude_pitch = float(recv[7])
                self._attitude_roll = float(recv[8])
                self._attitude_yaw = float(recv[9])
                self._static = bool(int(recv[12]))
                self._uphill = bool(int(recv[13]))
                self._downhill = bool(int(recv[14]))
                self._on_slope = bool(int(recv[15]))
                self._pick_up = bool(int(recv[16]))
                self._slip = bool(int(recv[17]))
                self._impact_x = bool(int(recv[18]))
                self._impact_y = bool(int(recv[19]))
                self._impact_z = bool(int(recv[20]))
                self._roll_over = bool(int(recv[21]))
                self._hill_static = bool(int(recv[22]))
            except AttributeError as e:#可能接受的数据会由问题，若出现问题则重新接收
                #recv = self.connection.recv_push_data(5).decode().split(' ')
                print(e)
                
        if push_enum is rm_define.chassis_push_attitude:
            recv = self.connection.recv_push_data(5).decode().split(' ')
            print(recv)
            ## TO DO 
            self._attitude_pitch = float(recv[3])
            self._attitude_roll = float(recv[4])
            self._attitude_yaw = float(recv[5])
        if push_enum is rm_define.chassis_push_position:
            recv = self.connection.recv_push_data(5).decode().split(' ')
            print(recv)
            ## TO DO 
            self._position_x = float(recv[3])
            self._position_y = float(recv[4])
        if push_enum is rm_define.chassis_push_status:
            recv = self.connection.recv_push_data(5).decode().split(' ')
            print(recv)
            ## TO DO 
            self._static = bool(int(recv[3]))
            self._uphill = bool(int(recv[4]))
            self._downhill = bool(int(recv[5]))
            self._on_slope = bool(int(recv[6]))
            self._pick_up = bool(int(recv[7]))
            self._slip = bool(int(recv[8]))
            self._impact_x = bool(int(recv[9]))
            self._impact_y = bool(int(recv[10]))
            self._impact_z = bool(int(recv[11]))
            self._roll_over = bool(int(recv[12]))
            self._hill_static = bool(int(recv[13]))
            #print('static :',self._static,'  roll_over:',self._roll_over)
        






def test():
    chassis_ctrl = Chassis_Ctrl()
    
    
#test()

