import zlib
import sys

bytes = []
with open(sys.argv[1], "rb") as f:
    bytes = f.read()
checksum = zlib.crc32(bytes)
print(checksum)