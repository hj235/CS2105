from socket import socket
from socket import SHUT_RDWR
import sys

httpStatus = {
    200: b'200 OK',
    404: b'404 NotFound',
    405: b'405 MethodNotAllowed'
}
_INF = b'Infinity'

keyValueStore = {} # mapping from bytes (key) to bytes (content)
counterStore = {} # mapping from bytes (key) to int (counter)

portNumber = int(sys.argv[1])
address = ("localhost", portNumber)
welcome_socket = socket()
welcome_socket.bind(address)
welcome_socket.listen(6)

while True:
    conn_socket, addr = welcome_socket.accept()
    print("Server test by A0282340M")
    print(f"Client connected from {addr}")

    packet = b''

    while True:
        header = b''
        headerFields = []
        contentLength = 0
        content = b''
        connectionClosed = False

        # receive the header
        while True:
            if b'  ' in packet:
                break

            data = conn_socket.recv(100)
            packet += data
            print(f'Received data: {data}')
            if len(data) == 0:
                connectionClosed = True
                break
        print(f'Received packet: {packet}')
        if connectionClosed:
            # conn_socket.shutdown(SHUT_RDWR)
            # conn_socket.close()
            print('Client connection was lost. Bye.')
            break

        # parse header
        headerIdx = packet.index(b'  ')
        header = packet[:headerIdx]
        headerFields = header.split(b' ')
        print(f'Header: {header}')

        # Check for content length
        #i = 2
        #while i < len(headerFields):
        #    if headerFields[i].decode().lower() == 'content-length':
        #        try:
        #            contentLength = int(headerFields[i + 1].decode())
        #            break
        #        except ValueError:
        #            i += 1
        #print(contentLength)
        contentLengthIdx = 2
        while contentLengthIdx < len(headerFields):
            if headerFields[contentLengthIdx].decode().lower() == 'content-length':
                try:
                    int(headerFields[contentLengthIdx+1].decode())
                    break
                except ValueError:
                    contentLengthIdx += 1
            contentLengthIdx += 1
        if contentLengthIdx < len(headerFields):
            contentLength = int(headerFields[contentLengthIdx + 1].decode())
        
        # Filter out header bytes
        packet = packet[headerIdx+2:]

        # receive content
        while len(packet) < contentLength:
            data =  conn_socket.recv(100)
            if len(data) == 0:
                connectionClosed = True
                break

            packet += data
        if connectionClosed:
            # conn_socket.shutdown(SHUT_RDWR)
            # conn_socket.close()
            print('Client connection was lost. Bye.')
            break

        # Filter out content bytes
        content = packet[:contentLength]
        packet = packet[contentLength:]
        print(f'Content: {content}')

        # process the http request
        method = headerFields[0].decode('ascii').lower()
        path = headerFields[1][1:].split(b'/')
        store = path[0]
        key = path[1]
        status = httpStatus[200]
        resContentLength = b''
        resContent = b''
        
        if store == b'key':
            match method:
                case 'post':
                    if key in keyValueStore and key in counterStore and counterStore[key] > 0:
                        status = httpStatus[405]
                    else:
                        keyValueStore[key] = content
                case 'get':
                    if key in keyValueStore and key in counterStore and counterStore[key] > 0:
                        resContent = keyValueStore[key]
                        resContentLength = len(resContent)
                        counterStore[key] -= 1
                        if counterStore[key] == 0:
                            del keyValueStore[key]
                            del counterStore[key]
                    elif key in keyValueStore:
                        resContent = keyValueStore[key]
                        resContentLength = len(resContent)
                    else:
                        status = httpStatus[404]
                case 'delete':
                    if key in keyValueStore and key in counterStore and counterStore[key] > 0:
                        status = httpStatus[405]
                    elif key in keyValueStore:
                        resContent = keyValueStore[key]
                        resContentLength = len(resContent)
                        del keyValueStore[key]
                    else:
                        status = httpStatus[404]
        else:
            match method:
                case 'post':
                    if key in keyValueStore and key in counterStore and counterStore[key] > 0:
                        inc = int(content.decode('ascii'))
                        counterStore[key] += inc
                    elif key in keyValueStore:
                        val = int(content.decode('ascii'))
                        counterStore[key] = val
                    else:
                        status = httpStatus[405]
                case 'get':
                    if key in keyValueStore and key in counterStore and counterStore[key] > 0:
                        resContent = str(counterStore[key]).encode()
                        resContentLength = len(resContent)
                    elif key in keyValueStore:
                        resContent = _INF
                        resContentLength = len(resContent)
                    else:
                        status = httpStatus[404]
                case 'delete': 
                    if key in counterStore and counterStore[key] > 0:
                        resContent = str(counterStore[key]).encode()
                        resContentLength = len(resContent)
                        del counterStore[key]
                    else:
                        status = httpStatus[404]

        # Prepare the http response
        response = [status]
        if resContent and resContentLength:
            response += [b'content-length', str(resContentLength).encode(), b' ']
            response = b' '.join(response)
            response += resContent
        else:
            response = status + b'  '

        # Send response to client
        print(f'Sending response: {response}')
        conn_socket.sendall(response)
        # conn_socket.shutdown(SHUT_RDWR)
        # conn_socket.close()
    
    conn_socket.close()
