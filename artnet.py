''' ArtNet Libary

Port 6454
'''
import socket
import asyncio
import os, random
from pca9633 import PCA9633
from smbus import SMBus

HOST, PORT = '192.168.0.255', 6454

BROADCAST = '192.168.0.255'

class Channel():
    def __init__(self) -> None:
        pass

class ArtnetUniverse(asyncio.DatagramProtocol):
    ''' https://art-net.org.uk/how-it-works/streaming-packets/artdmx-packet-definition/ '''
    def __init__(self,subuni=0,net=0,physical=0):
        super().__init__()
        self.subuni=subuni
        self.net=net
        self.physical=physical

        self.pixels = []
        for i in range(0x3d,0x6e):
            temp_pixel = PCA9633(i2cbus,i)
            if temp_pixel.status:
                self.pixels.append(temp_pixel)
    def connection_made(self, transport) -> "Used by asyncio":
        self.transport = transport    
    def datagram_received(self, data, addr) -> "Main entrypoint for processing message":
        # Here is where you would push message to whatever methods/classes you want.
        net = -1
        physical = -1
        subuni = -1
        try:
            type = data[8:9]
            physical = data[13]
            # print(f'Type {type}  physical {physical}  ')
            subuni = data[14]
            net = data[15]
            length = data[16:17]
            dmx = data[18:]
            # print(f'Type {type}  physical {physical}  subuni {subuni}  net {net}  length {length}')
        except IndexError as e:
            pass
        if net == self.net and subuni == self.subuni and physical == self.physical:
            # print(f'Process {dmx}')
            for pixel in range(0,len(self.pixels),3):
                self.pixels[pixel].rgb(dmx[pixel],dmx[pixel+1],dmx[pixel+2])

        # print(f"Received Syslog message: {addr} {data}")

if __name__ == '__main__':
    i2cbus = SMBus(1)  # Create a new I2C bus
    loop = asyncio.get_event_loop()
    t = loop.create_datagram_endpoint(ArtnetUniverse, local_addr=('0.0.0.0', PORT))
    loop.run_until_complete(t) # Server starts listening
    loop.run_forever()
