import sys
sys.path.append('../../connection/network/')
import robot_connection

from liveview import RobotLiveview
from chassis_ctrl import Chassis_Ctrl
from pynput import keyboard
from gimbal_ctrl import Gimbal_Ctrl

class Test(object):
    def __init__(self,type):
        #self.chassis_ctrl = Chassis_Ctrl(type)
        #self.gimbal_ctrl = Gimbal_Ctrl(type)
        self.view = RobotLiveview(type)
        self.view.display()
        with keyboard.Listener(on_press=self.on_press,
                           on_release=self.on_release) as listener:
           listener.join()
        
    
    def on_press(self,key):
        try:
            print('alphanumeric key {0} pressed'.format(
                key.char))
            if key.char == 'a':
                self.chassis_ctrl.move_with_speed(0,-1,0)
            if key.char == 'd':
                self.chassis_ctrl.move_with_speed(0,1,0)
            if key.char == 'w':
                self.chassis_ctrl.move_with_speed(1,0,0)
            if key.char == 's':
                self.chassis_ctrl.move_with_speed(-1,0,0)

        except AttributeError:
            print('special key {0} pressed'.format(key))
            if key == key.left:
                self.gimbal_ctrl.speed_control(0,-100)
            if key == key.right:
                self.gimbal_ctrl.speed_control(0,100)
            if key == key.up:
                self.gimbal_ctrl.speed_control(80,0)
            if key == key.down:
                self.gimbal_ctrl.speed_control(-80,0)
    
    def on_release(self,key):
        print('{0} released type {1}'.format(key,type(key)))
        self.gimbal_ctrl.speed_control(0,0)
        try:
            if key.char == 'w' or key.char == 's' or key.char == 'a' or key.char == 'd':
                self.chassis_ctrl.stop()
        except AttributeError:
            if key == keyboard.Key.esc:
                # Stop listener
                return False

#print('test')
connection = robot_connection.RobotConnection('192.168.42.2')
connection.open()
s = Test(connection)



