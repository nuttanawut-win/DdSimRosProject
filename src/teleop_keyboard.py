#!/usr/bin/env python3 

from threading import Thread
import sys , select, tty, termios
import rospy 
from geometry_msgs.msg import Twist 

###class to publish twist mesges ###
class teleOpKeyboard(Thread):
  def __init__(self):
    Thread.__init__(self)
    self.publisher = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
    self.linearVel = 0.2
    self.angularZVel = 0.2
    self.direction = 0
    self.spin = 0
    self.msg = Twist()
    self.start()
  
  ### Method to update twist##
  def update(self):
    self.msg.linear.x = self.direction*self.linearVel
    self.msg.linear.y = 0
    self.msg.linear.z = 0
    self.msg.angular.x = 0
    self.msg.angular.y = 0
    self.msg.angular.z = self.spin*self.angularZVel 

  ### Method to publish twist##
  def pubData(self) :
    rate = rospy.Rate(10) 
    while not rospy.is_shutdown():
      self.publisher.publish(self.msg)
      rate.sleep()

  ### Start publish twist ##
  def run(self):
    self.pubData()

### Modthod to receice keyboard value ###
### Ref : https://github.com/ros-teleop/teleop_twist_keyboard/blob/master/teleop_twist_keyboard.py ###
def getKey(key_timeout):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], key_timeout)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = " "
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

### Main operation ###
if __name__ == '__main__':
  settings = termios.tcgetattr(sys.stdin)

  #set node name 
  rospy.init_node('teleop_keyboard')  

  #create publisher class 
  teloKey = teleOpKeyboard()

  #update twist for starting 
  teloKey.linearVel  -= 0.2
  teloKey.angularZVel += 0.2
  teloKey.direction = 0 
  teloKey.spin = 0
  teloKey.update()

  #set rate to receice keyboard value
  key_timeout = 0.1
  if key_timeout == 0.0:
    key_timeout = None

  try:
    while True :

      #receice keyboard value
      key = getKey(key_timeout)

      #check keyboard value to change twist
      if key == "w" :
        teloKey.direction = 1
      elif key == "s" :
        teloKey.direction = -1
      elif key == "d" :
        teloKey.spin = -1
      elif key == "a" :
        teloKey.spin = 1
      elif key == "e" :
        teloKey.linearVel  += 0.2
      elif key == "q" :
        teloKey.linearVel  -= 0.2
      elif key == "x" :
        teloKey.angularZVel += 0.2
      elif key == "c" :
        teloKey.angularZVel -= 0.2
      else :
        teloKey.direction = 0 
        teloKey.spin = 0

      #update twist 
      teloKey.update()
  except rospy.ROSInterruptException:
    pass