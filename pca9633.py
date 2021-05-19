#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""

from smbus import SMBus
import time,sys

#define PCA9633_ADDR 		(0x62) // slave address

# auto increment definitions Datasheet page 10
AI2	= 0x80 # mask for AI2
AI1	= 0x40 # mask for AI1
AI0	= 0x20 # mask for AI0

INCOFF = 0x00 # AI2:0 000 no auto increment
INCALL = 0x80 # AI2:0 100 auto inc all registers
INCIND = 0xA0 # AI2:0 101 auto inc individual pwm registers
INCGBL = 0xC0 # AI2:0 110 auto inc global registers
INCINDGBL = 0xE0 # AI2:0 111 auto inc individual and global registers

# register definitions Datasheet page 11
MODE1 = 0x00 # mode register 1
MODE2 = 0x01 # mode register 2
PWM0 = 0x02  # PWM0 brightness control led0
PWM1 = 0x03  # PWM0 brightness control led0
PWM2 = 0x04  # PWM0 brightness control led0
PWM3 = 0x05  # PWM0 brightness control led0
GRPPWM = 0x06 # group brightness (duty cycle)
GRPFREQ	= 0x07 # group frequency
LEDOUT	= 0x08 # LED output state
SUBADR1	= 0x09 # i2c bus sub address 1
SUBADR2 = 0x0A # i2c bus sub address 1
SUBADR3 = 0x0B # i2c bus sub address 1
ALLCALLADR = 0x0C # LED All Call i2c address

# MODE1 definitions
SLEEP	=	0x10 # bit 4, low power mode enable, RW
SUB1	=	0x08 # bit 3, PCA9633 responds to sub address 1
SUB2	=	0x04 # bit 2, PCA9633 responds to sub address 2
SUB3	=	0x02 # bit 1, PCA9633 responds to sub address 3
ALLCALL	=	0x01 # bit 0, PCA9633 responds to all call address

# MODE2 definitions
DMBLINK	= 0x20 # bit 5, group control dim or blink
INVRT	= 0x10 # bit 4, output logic invert (1=yes, 0=no)
OCH		= 0x08 # bit 3, 0=output change on stop, 1=output change on ACK
OUTDRV	= 0x04 # bit 2, output drivers 0=open drain, 1=totem poll - push pull
OUTNE1	= 0x02 # bit 1, 2 bits see page 13, 16 pin device only
OUTNE0	= 0x01 # bit 0, see above


LEDLINEAR = [
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x02,
0x02, 0x02, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x04, 0x04, 0x04, 0x04, 0x04, 0x05, 0x05, 0x05,
0x05, 0x06, 0x06, 0x06, 0x07, 0x07, 0x07, 0x08, 0x08, 0x08, 0x09, 0x09, 0x0A, 0x0A, 0x0B, 0x0B,
0x0C, 0x0C, 0x0D, 0x0D, 0x0E, 0x0F, 0x0F, 0x10, 0x11, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1F, 0x20, 0x21, 0x23, 0x24, 0x26, 0x27, 0x29, 0x2B, 0x2C,
0x2E, 0x30, 0x32, 0x34, 0x36, 0x38, 0x3A, 0x3C, 0x3E, 0x40, 0x43, 0x45, 0x47, 0x4A, 0x4C, 0x4F,
0x51, 0x54, 0x57, 0x59, 0x5C, 0x5F, 0x62, 0x64, 0x67, 0x6A, 0x6D, 0x70, 0x73, 0x76, 0x79, 0x7C,
0x7F, 0x82, 0x85, 0x88, 0x8B, 0x8E, 0x91, 0x94, 0x97, 0x9A, 0x9C, 0x9F, 0xA2, 0xA5, 0xA7, 0xAA,
0xAD, 0xAF, 0xB2, 0xB4, 0xB7, 0xB9, 0xBB, 0xBE, 0xC0, 0xC2, 0xC4, 0xC6, 0xC8, 0xCA, 0xCC, 0xCE,
0xD0, 0xD2, 0xD3, 0xD5, 0xD7, 0xD8, 0xDA, 0xDB, 0xDD, 0xDE, 0xDF, 0xE1, 0xE2, 0xE3, 0xE4, 0xE5,
0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xEB, 0xEC, 0xED, 0xED, 0xEE, 0xEF, 0xEF, 0xF0, 0xF1, 0xF1, 0xF2,
0xF2, 0xF3, 0xF3, 0xF4, 0xF4, 0xF5, 0xF5, 0xF6, 0xF6, 0xF6, 0xF7, 0xF7, 0xF7, 0xF8, 0xF8, 0xF8,
0xF9, 0xF9, 0xF9, 0xF9, 0xFA, 0xFA, 0xFA, 0xFA, 0xFA, 0xFB, 0xFB, 0xFB, 0xFB, 0xFB, 0xFB, 0xFC,
0xFC, 0xFC, 0xFC, 0xFC, 0xFC, 0xFC, 0xFC, 0xFC, 0xFD, 0xFD, 0xFD, 0xFD, 0xFD, 0xFD, 0xFD, 0xFD,
0xFD, 0xFD, 0xFD, 0xFD, 0xFD, 0xFD, 0xFD, 0xFE, 0xFE, 0xFE, 0xFE, 0xFE, 0xFE, 0xFE, 0xFF, 0xFF]


class PCA9633:
    def __init__(self,i2cbus,address,allcall=True):
        self.address = address
        self.i2cbus = i2cbus
        self.status = True
        if allcall: 
            m1 = ALLCALL
        else:
            m1 = 0x00                   #; // set sleep = 0, turn on oscillator, disable allcall and subaddrs
        m2 = OUTDRV #((INVRT) | (OUTDRV))  #; // output inverted, totem pole drivers enabled
        ldout = 0xFF                #; // all outputs under individual and group control
        print('m2 is {0:b}'.format(m2))
        if address != 0x70:
            self.status = self._i2c_write(self.address, MODE1, m1)    
            self._i2c_write(self.address, MODE2, m2)
            self._i2c_write(self.address, LEDOUT, ldout)
            # If we get a bad write then return pixel error
        else:
            # This is the all call group probably!
            pass
    def _i2c_write(self,address, cmd, data):
        # self.i2cbus.  Wire.beginTransmission(address);
        try:
            self.i2cbus.write_byte_data(address, cmd, data) #; // control register
        except OSError as e:
            print(f'Error writeing to {address} with {cmd} {data}')
            return False
        return True
    def rgb(self,r,g,b,a=255):
        self._i2c_write(self.address, PWM0, b)
        self._i2c_write(self.address, PWM1, g)
        self._i2c_write(self.address, PWM2, r)
        self._i2c_write(self.address, GRPPWM, a)
    def getValues(self):
        return self.i2cbus.read_byte_data(self.address, LEDOUT)
  


if __name__ == "__main__":
    print('Hello world...')
    i2cbus = SMBus(1)  # Create a new I2C bus
    # i2cbus.write_byte_data(0x03, 0xa5)
    print('Init LED')
    # led = PCA9633(i2cbus,0x52)
    # led = PCA9633(i2cbus,0x3d)
    led = PCA9633(i2cbus,0x70)
    ledarry = []
    for i in range(0x3d,0x6e):
        temp_pixel = PCA9633(i2cbus,i)
        if temp_pixel.status:
            ledarry.append(temp_pixel)
    print(led.getValues())
    time.sleep(0.5)
    step = 0.51

    dim = 100

    led.rgb(255,0,0)
    time.sleep(step)
    led.rgb(0,255,0)
    time.sleep(step)
    led.rgb(0,0,255)
    time.sleep(step)
    led.rgb(0,0,0)
    # sys.exit(0)

    for l in ledarry:
        l.rgb(255,0,0)
        print('.', end='')
        time.sleep(step)
        l.rgb(0,0,0)

    for l in ledarry:
        l.rgb(0,255,0)
        print('.', end='')
        time.sleep(step)
        l.rgb(0,0,0)

    for l in ledarry:
        l.rgb(0,0,255)
        print('.', end='')
        time.sleep(step)
        l.rgb(0,0,0)

    sys.exit(0)

    print('0,0,0')
    led.rgb(0,0,0)
    print(led.getValues())
    time.sleep(step)
    
    print('255,0,0')
    led.rgb(LEDLINEAR[dim],0,0)
    print(led.getValues())
    time.sleep(step)
    
    print('0,0,0')
    led.rgb(0,0,0)
    print(led.getValues())
    time.sleep(step)
    
    print('0,255,0')
    led.rgb(0,LEDLINEAR[dim],0)
    print(led.getValues())
    time.sleep(step)

    print('0,0,0')
    led.rgb(0,0,0)
    print(led.getValues())
    time.sleep(step)
    
    print('0,0,255')
    led.rgb(0,0,LEDLINEAR[dim])
    print(led.getValues())
    time.sleep(step)
    
    print('0,0,0')
    led.rgb(0,0,0)
    print(led.getValues())
    time.sleep(step)

    led.rgb(LEDLINEAR[10],LEDLINEAR[200],LEDLINEAR[100],0)
    time.sleep(step)
    for i in range (0,dim):
        print(i)
        led._i2c_write(0x70, GRPPWM, LEDLINEAR[i])
        time.sleep(0.2)

    print('0,0,0')
    led.rgb(0,0,0)
    print(led.getValues())
    time.sleep(step)

    # print(0,0,0,255)
    # led.rgb(0,0,0,255)
    # print(led.getValues())
    # time.sleep(step)

    # print(0,0,0,0)
    # led.rgb(0,0,0,0)
    # print(led.getValues())
    # time.sleep(step)

    # print('255,0,0')
    # led.rgb(255,0,0)
    # print(led.getValues())
    # time.sleep(step)
     # print('PWM1 0')
    # led._i2c_write(0x52, PWM1, 0x00)
    # time.sleep(0.5)

    # print('PWM1 255')
    # led._i2c_write(0x52, PWM1, 0xFF)
    # time.sleep(0.5)

    # print('PWM1 0')
    # led._i2c_write(0x52, PWM1, 0x00)
    # time.sleep(0.5)


    # print('PWM1 255')
    # led._i2c_write(0x52, 0b00000110, 0xFF)
    # time.sleep(0.5)

    # i2cdump