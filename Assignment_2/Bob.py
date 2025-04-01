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
    seqNo = int(packet[CHECKSUMLENGTH:HEADERSIZE-1])
    isEnd = int(packet[HEADERSIZE-1])
    body = packet[HEADERSIZE:]
    return (isEnd, seqNo, body)

# takes in an integer seqNo, return bytes
# header format: f'{str(checkSum).zfill(10)}{str(seqNo).zfill(5)}ACK'
def makeAck(seqNo):
    ack = f'{str(seqNo).zfill(5)}ACK'
    checkSum = computeChecksum(ack.encode())
    return f'{str(checkSum).zfill(10)}{ack}'.encode()

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.info('Starting Bob...')

portNumber = int(sys.argv[1])
address = ("localhost", portNumber)
commSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
commSocket.bind(address)
logger.info(f'Bob receiving from {address}')

# data is a string
expectedSeqNo = 0
data = ''
try:
    while True:
        # receive packet
        pkt, aliceAddr = commSocket.recvfrom(5000)
        logger.info(f'Received: {pkt} from {aliceAddr}')

        # detect corruption
        if not compareChecksum(pkt):
            # send ACK
            logger.warning(f'Packet corrupted, requesting resend')
            commSocket.sendto(makeAck(expectedSeqNo), aliceAddr)
            continue

        # parse packet
        isEnd, seqNo, body = parsePacket(pkt)
        logger.info(f'Parsed: isEnd={isEnd}, seqNo={seqNo}, body={body}')

        # detect duplicate packet
        if seqNo != expectedSeqNo:
            # drop packet, request resend
            logger.warning(f'Duplicate packet, requesting resend')
            commSocket.sendto(makeAck(expectedSeqNo), aliceAddr)
            continue

        # send ACK
        commSocket.sendto(makeAck(seqNo+1), aliceAddr)
        expectedSeqNo += 1

        data += body
        if isEnd:
            break
        
    logger.info(f'Received data of length {len(data)}: {data}')
    
    logger.info('Data received, attempting to close the connection...')
    while True:
        commSocket.sendto(b'FIN', aliceAddr)
        finack = b''
        try:
            commSocket.settimeout(0.06)
            finack = commSocket.recv(5000)
            if finack == b'FINACK':
                logger.info('FINACK received, closing connection')
                break
            else:
                logger.warning(f'FINACK corrupted, resending')
                continue
        except socket.timeout:
            logger.warning('Timeout, resending FIN')
            continue

    print(data)
except KeyboardInterrupt:
    logger.info('Keyboard interrupt encountered, ending program')