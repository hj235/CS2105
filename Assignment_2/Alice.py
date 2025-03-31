import socket
import sys
import logging
import zlib

HEADERSIZE = 20

# isEnd & seqNo are integers, checkSum is a string, returns a string
def makeHeader(isEnd, seqNo, checkSum):
    return f'{isEnd} {str(seqNo).zfill(5)} {checkSum}  '

# takes in bytes (data), return a checksum which is always a string
# representing a 10 digit number
def computeChecksum(data):
    checkSum = str(zlib.crc32(data)).zfill(10)
    return checkSum

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)
logging.debug('Starting Alice...')

portNumber = int(sys.argv[1])
address = ("localhost", portNumber)
commSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
logging.info(f'Alice sending to {address}')

# data, body, header and packet are all strings
seqNo = 0
while True:
    data = ''
    try:
        data = input()
    except EOFError:
        logging.info('EOF encountered, closing connection.')
        commSocket.close()
        break
    # except KeyboardInterrupt:
    #     logging.warning('Keyboard interrupt, closing connection.')
    #     commSocket.close()
    #     break
    logging.info(f'Sending data of length {len(data)}: {data}')

    while data:
        seqNo %= 100000
        body = data[:44]
        data = data[44:]
        if not data:
            isEnd = 1
        else:
            isEnd = 0
        header = makeHeader(isEnd, seqNo, computeChecksum(body.encode()))
        seqNo += 1
        packet = header + body
        commSocket.sendto(packet.encode(), address)
