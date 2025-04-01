import socket
import sys
import logging
import zlib
from collections import deque

# takes in bytes (data), return a checksum which is always a string
# representing a 10 digit number
def computeChecksum(data):
    checkSum = str(zlib.crc32(data)).zfill(10)
    return checkSum

# data is bytes, checkSum is a string
def compareChecksum(data, checkSum):
    return computeChecksum(data) == checkSum

# 

# takes in bytes (packet), return a tuple of (isEnd, seqNo, checkSum, body)
# isEnd & seqNo are integers, checkSum & body are strings
def parsePacket(packet):
    packet = packet.decode()
    isEnd = int(packet[0])
    seqNo = int(packet[2:7])
    checkSum = packet[8:18]
    body = packet[20:]
    return (isEnd, seqNo, checkSum, body)

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)
logger.debug('Starting Bob...')

portNumber = int(sys.argv[1])
address = ("localhost", portNumber)
commSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
commSocket.bind(address)
logger.info(f'Bob receiving from {address}')

# data is a string
while True:
    try:
        data = ''
        while True:
            pkt = commSocket.recv(5000)
            logger.info(f'Received packet of length {len(pkt)}: {pkt}')
            isEnd, seqNo, checkSum, body = parsePacket(pkt)
            data += body
            if isEnd:
                break
            
        logger.info(f'Received data of length {len(data)}: {data}')

        print(data)
    except KeyboardInterrupt:
        logger.info('Keyboard interrupt encountered, closing connection.')
        break