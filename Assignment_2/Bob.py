import socket
import sys
import logging
import zlib
from collections import deque

CHECKSUMLENGTH = 10
SEQNOLENGTH = 5
HEADERSIZE = 16
BODYSIZE = 64 - HEADERSIZE

# takes in bytes (data), return an integer
def computeChecksum(data):
    checkSum = zlib.crc32(data)
    return checkSum

# packet and checkSum are both bytes
def compareChecksum(packet):
    checkSum = 0
    try:
        checkSum = int(packet[:CHECKSUMLENGTH].decode())
    except ValueError:
        logger.warning(f'CheckSum corrupted: {packet[:CHECKSUMLENGTH]}')
        return False
    recompute = computeChecksum(packet[CHECKSUMLENGTH:])
    logging.debug(f'R: {recompute}, c: {checkSum}, using {packet[CHECKSUMLENGTH:]}')
    return recompute == checkSum

# takes in bytes (packet), return a tuple of (isEnd, seqNo, body)
# isEnd & seqNo are integers, body is a string
def parsePacket(packet):
    # header format: f'{str(checkSum).zfill(10)}{str(seqNo).zfill(5)}{isEnd}'
    packet = packet.decode()
    # checkSum = packet[:CHECKSUMLENGTH]
    seqNo = int(packet[CHECKSUMLENGTH:HEADERSIZE-1])
    isEnd = int(packet[HEADERSIZE-1])
    body = packet[HEADERSIZE:]
    return (isEnd, seqNo, body)

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.info('Starting Bob...')

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
            # receive packet
            pkt = commSocket.recv(5000)
            logger.info(f'Received: {pkt}')

            # detect corruption
            # if not compareChecksum(pkt):
            #     # send unACK
            #     logger.warning(f'Packet corrupted, sending unACK')
            #     commSocket.sendto('unACK'.encode(), address)
            #     continue

            # parse packet
            isEnd, seqNo, body = parsePacket(pkt)
            logger.info(f'Parsed: isEnd={isEnd}, seqNo={seqNo}, body={body}')

            # send ACK
            commSocket.sendto('ACK'.encode(), address)

            data += body
            if isEnd:
                break
            
        logger.info(f'Received data of length {len(data)}: {data}')

        print(data)
    except KeyboardInterrupt:
        logger.info('Keyboard interrupt encountered, closing connection.')
        break