''' ArtNet Libary

Port 6454
'''
import socket
import asyncio
import os, random
from pca9633 import PCA9633
from smbus import SMBus
import logging
logging.basicConfig(level=logging.DEBUG)
# numeric_level = getattr(logging, loglevel.upper(), None)
# if not isinstance(numeric_level, int):
#     raise ValueError('Invalid log level: %s' % loglevel)
# logging.basicConfig(level=numeric_level, ...)


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
        if len(data) < 18:
            logging.debug(f'Packet only {len(data)} bytes - need 18 bytes')
            return False # Not enough data
        if data[0:7] != b'Art-Net':
            logging.debug(f'Does not start Art-Net {data[0:7]}')
            return False
        opcode = int.from_bytes(data[8:9],byteorder='little')
        protVer = int(data[10])
        # if protVer < 14: # ChamSys seems to send lots of version 0!
        #     logging.debug(f'Invalid versoin {protVer}')
        #     return False
        physical = data[13] # This field is for information only. Use Universe for data routing.

        universeAndNet = data[14:15]
        length = int.from_bytes(data[16:17],byteorder='big') # ChamSys again seems to send a rubbish length of 2 constantly
        address = int.from_bytes(universeAndNet,byteorder='little') #byteorder='big'
        logging.debug(f'Opcode: {opcode}, Version {protVer}, Payload length {length}, Universe and net {universeAndNet}, use address {address}')
        # https://art-net.org.uk/how-it-works/streaming-packets/artdmx-packet-definition/
    
        # type = data[8:9]
        
        # print(f'Type {type}  physical {physical}  ')
        subuni = data[14]
        net = data[15]      # SubUni and Net make up 
        length = data[16:17]
        dmx = data[18:]
        # print(f'Type {type}  physical {physical}  subuni {subuni}  net {net}  length {length}')
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
