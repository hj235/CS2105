import socket
import sys
import logging
import zlib

CHECKSUMLENGTH = 10
SEQNOLENGTH = 5
HEADERSIZE = 16
BODYSIZE = 64 - HEADERSIZE

# parameters are all integers, returns a string
def makeHeader(isEnd, seqNo, checkSum):
    return f'{str(checkSum).zfill(10)}{str(seqNo).zfill(5)}{isEnd}'

# takes in bytes (data), return a checksum which is an integer
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

def parseAck(packet):
    # header format: f'{str(checkSum).zfill(10)}{str(seqNo).zfill(5)}ACK'
    packet = packet.decode()
    seqNo = int(packet[CHECKSUMLENGTH:CHECKSUMLENGTH+SEQNOLENGTH])
    return seqNo

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)
logging.info('Starting Alice...')

portNumber = int(sys.argv[1])
address = ("localhost", portNumber)
commSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
commSocket.settimeout(0.05) # 50ms timeout
logging.info(f'Alice sending to {address}')

# data, body, header and packet are all strings
seqNo = 0
data = (''.join(sys.stdin.readlines()))[:-1]
logging.info(f'Sending data of length {len(data)}')

while data:
    # prepare information to send
    body = data[:BODYSIZE]
    if len(data) > BODYSIZE: # no more data to send
        isEnd = 0
    else:
        isEnd = 1
    # make checksum using seqNo, isEnd and body
    checkSum = computeChecksum(f'{str(seqNo).zfill(5)}{isEnd}{body}'.encode())
    logging.debug(f'C: {checkSum}, using {str(seqNo).zfill(5)}{isEnd}{body}')
    header = makeHeader(isEnd, seqNo, checkSum)

    # send packet
    packet = header + body
    commSocket.sendto(packet.encode(), address)

    # wait for ACK
    ack = b''
    try:
        ack = commSocket.recv(5000)
    except socket.timeout:
        logging.warning('timed out, resending')
        continue
    if ack == b'FIN':
        logging.info('FIN received, attempting to close connection')
        break
    if not compareChecksum(ack):
        logging.warning('ack corrupted, resending')
        continue
    if parseAck(ack) == seqNo:
        logging.warning(f'ack number mismatch, expected {seqNo+1}, got {parseAck(ack)}')
        continue

    # continue
    seqNo += 1
    data = data[BODYSIZE:]

# close connection
while True:
    commSocket.sendto(b'FINACK', address)
    refin = b''
    try:
        commSocket.settimeout(1)
        refin = commSocket.recv(5000)
    except socket.timeout:
        logging.info('Connection timed out, assumed closed')
        break
