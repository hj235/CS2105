import socket
from socket import SHUT_RDWR
import sys
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)
logger.debug('Starting Bob...')

portNumber = int(sys.argv[1])
address = ("localhost", portNumber)
commSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
commSocket.bind(address)
logger.info(f'Bob receiving from {address}')

while True:
    try:
        data = b''
        # pkt, addr = commSocket.recvfrom(64)
        while True:
            pkt = commSocket.recv(5000)
            if len(pkt) == 0:
                break
            data += pkt
            # pkt, addr = commSocket.recvfrom(5000)
            logger.info(f'Received packet of length {len(pkt)}: {pkt}')
            print(pkt.decode())
        logger.info(f'Received data of length {len(data)}:\n{data}')
        print(data.decode())
    except KeyboardInterrupt:
        logger.info('Keyboard interrupt encountered, closing connection.')
        break
