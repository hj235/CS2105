import socket
from socket import SHUT_RDWR
import sys
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)
logging.debug('Starting Alice...')

portNumber = int(sys.argv[1])
address = ("localhost", portNumber)
commSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# commSocket.bind(address)
logging.info(f'Alice sending to {address}')

while True:
    data = b''
    try:
        data = input()
    except EOFError:
        logging.info('EOF encountered, closing connection.')
        commSocket.close()
        break
    logging.info(f'Sending data of length {len(data)}:\n{data}')
    # if len(data) == 0:
    #     logging.info('Empty line encountered, closing connection.')
    #     commSocket.shutdown(SHUT_RDWR)
    #     commSocket.close()
    #     break
    while data:
        packet = data[:64]
        data = data[64:]
        commSocket.sendto(packet.encode(), address)
