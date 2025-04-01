import sys
import logging
import zlib
from collections import deque

# dq = deque(maxlen=4)
# dq.append(1)
# dq.append(2)
# dq.append(3)
# dq.insert(0, 4)
# print(dq)
# print(dq.popleft())
# print(dq)
# print(dq.pop())
# dq.insert(0, 1)
# print(dq)

# logger = logging.getLogger()
# logging.basicConfig(level=logging.DEBUG)
# logger.info('Starting test.py...')
# logger.debug('Debugging test.py...')
# logger.warning('Warning in test.py...')
# logger.error('Error in test.py...')
# print(len(b'1 123 01234'))
# print('2572077806'.encode())
# checkSum = f'{zlib.crc32(b''):010d}'.encode()
# checkSumInt = zlib.crc32(b'1')
# print(checkSumInt)
# bs = checkSumInt.to_bytes(4)
# print(bs)
# print(bs[0:4])
# checkSum = str(zlib.crc32(b'2'))
# print(checkSum)
# print(checkSum.zfill(10))
# print(int(checkSum.decode()))
# print(len(bytes(32)))
# print(f'Hello World! {sys.argv}')
# s = '123'
# print(int(s))

data = sys.stdin.readlines()
print(data)
print(''.join(data))