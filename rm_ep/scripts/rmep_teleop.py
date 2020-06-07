import rospy
from pynput import keyboard
from geometry_msgs.msg import Twist
import threading
class Rmep_teleop(object):
    def __init__(self):
        
        self.pub = rospy.Publisher('cmd_vel', Twist, queue_size=5)
        self.twist = Twist()
        self.test = threading.Thread(target=self.cmd_publish)
        #self.test.start()
        with keyboard.Listener(on_press=self.on_press,
                           on_release=self.on_release) as listener:
            listener.join()

    def cmd_publish(self):
        rate = rospy.Rate(30)
        while True:
            #print(self.twist)
            self.pub.publish(self.twist)
            rate.sleep()

    def on_press(self,key):
        try:
            print('alphanumeric key {0} pressed'.format(
                key.char))
            if key.char == 'a':
                self.twist.linear.y=-1
                print(self.twist.linear.y)
            if key.char == 'd':
                self.twist.linear.y=1
            if key.char == 'w':
                self.twist.linear.x=1
            if key.char == 's':
                self.twist.linear.x=-1
            
            

        except AttributeError:
            print('special key {0} pressed'.format(key))
            if key == key.left:
                self.twist.angular.z=-100
            if key == key.right:
                self.twist.angular.z=100
        finally:
            self.pub.publish(self.twist)
    def on_release(self,key):
        print('{0} released type {1}'.format(key,type(key)))
        
        self.twist.angular.z=0
        try:
            if key.char == 'w' or key.char == 's' or key.char == 'a' or key.char == 'd':
                self.twist.linear.y=0
                self.twist.linear.x=0
        except AttributeError:
            if key == keyboard.Key.esc:
                # Stop listener
                return False
        finally:
            self.pub.publish(self.twist)
def main():
    rospy.init_node('rmep_teleop')
    test=Rmep_teleop()

main()