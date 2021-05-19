#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PCA9633.py
Author : Alexis PAQUES (@AlexisTM)
"""

# import rospy
import wiringpi2 as wpi
import time
# from std_msgs.msg import ColorRGBA

class PCA9633(object):
  def __init__(self, addr=0x52, dev="/dev/i2c-1"):
    super(PCA9633, self).__init__()
    self.i2c_dev = "/dev/i2c-1"
    self.i2c_addr = 0x62
    wpi.wiringPiSetup()
    self.i2c_fd = wpi.wiringPiI2CSetupInterface(self.i2c_dev, self.i2c_addr)
    # leave time to init
    time.sleep(0.2)
    wpi.wiringPiI2CWriteReg8(self.i2c_fd, 0x08, 0x2A)
    wpi.wiringPiI2CWriteReg8(self.i2c_fd, 0x06, 0x00)
    wpi.wiringPiI2CWriteReg8(self.i2c_fd, 0x07, 0x80)
    # self.sub = rospy.Subscriber("led", ColorRGBA, self.color_msg_cb) 

  def color_msg_cb(self, msg):
    self.set_color(msg.r, msg.g, msg.b)

  def sanitize(self, data):
    data = int((1-data)*255)
    if data > 255:
      data = 255
    if data < 0: 
      data = 0
    return data

  def set_color(self, r, g, b):
    wpi.wiringPiI2CWriteReg8(self.i2c_fd, 0x02, self.sanitize(self.current_color.g))
    wpi.wiringPiI2CWriteReg8(self.i2c_fd, 0x03, self.sanitize(self.current_color.b))
    wpi.wiringPiI2CWriteReg8(self.i2c_fd, 0x04, self.sanitize(self.current_color.r))
    wpi.wiringPiI2CWriteReg8(self.i2c_fd, 0x06, 0x00)
    wpi.wiringPiI2CWriteReg8(self.i2c_fd, 0x07, 0x80)

def main():
  led = PCA9633()
  print ("Testing the LED (PCA9633 device on i2c bus)")
  print ("RED")
  led.set_color(1,0,0)
  time.sleep(1)
  print ("GREEN")
  led.set_color(0,1,0)
  time.sleep(1)
  print ("BLUE")
  led.set_color(0,0,1)
  time.sleep(1)
  print ("WHITE")
  led.set_color(1,1,1)
  time.sleep(5)

if __name__ == '__main__':
  # rospy.init_node("LED_controller_py")
  main()