import sys


def main():
    data = b''

    while (True):
        headerEnd = data.find(b'B')

        while (headerEnd < 0):
            nxtChunk = sys.stdin.buffer.read1(10)
            data += nxtChunk
            if len(data) == 0:
                return
            headerEnd = data.find(b'B')

        payloadSize = int(data[6:headerEnd].decode())
        data = data[headerEnd+1:]

        while len(data) < payloadSize:
            nxtChunk = sys.stdin.buffer.read1(10)
            data += nxtChunk

        payload = data[:payloadSize]
        data = data[payloadSize:]

        sys.stdout.buffer.write(payload)
        sys.stdout.buffer.flush()

if __name__ == "__main__":
    main()