#! /usr/bin/env python3

# Echo client program
import socket, sys, re, time, os
sys.path.append("lib")       # for params
import params
import Framer
import Buffers

def convertToBin(fileLen):
    binVal = ""
    div = 128
    while(div > 0):
        if(fileLen - div > -1):
            fileLen = fileLen-div
            binVal += "1"
        else:
            binVal += "0"
        div = div//2
    return binVal

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


client = "MyClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage  = paramMap["server"], paramMap["usage"]

if usage:
    params.usage()

try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    try:
        print(" attempting to connect to %s" % repr(sa))
        s.connect(sa)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    break

if s is None:
    print('could not open socket')
    sys.exit(1)

messagesToSend = []
messagesToSend.append("Message.txt")

#My own framer to send files; My original framer wasn't too useful so I made a custom Framer here
bufferedWriter = Buffers.BufferedWriter(s.fileno())
for message in messagesToSend:
    fd = os.open(message, os.O_RDONLY)
    bufferedReader = Buffers.BufferedReader(fd)

    # Size of file name in bits is obtained
    fnSizeInB = convertToBin(len(message)).encode()
    for Byte in fnSizeInB:
        bufferedWriter.writeByte(Byte)
        
    # File name is coverted to a byte array
    fnAsByteArr = message.encode()
    for Byte in fnAsByteArr:
        bufferedWriter.writeByte(Byte)

    # File size is converted to binary
    fileSizeInB = convertToBin(os.path.getsize(message)).encode()
    for Byte in fileSizeInB:
        bufferedWriter.writeByte(Byte)

    while(binString := bufferedReader.readByte()) is not None:
        bufferedWriter.writeByte(binString)
    bufferedWriter.flush()
    
bufferedWriter.flush()

s.shutdown(socket.SHUT_WR)

while 1:
    data = s.recv(1024).decode()
    print("Received '%s'" % data)
    if len(data) == 0:
        break
print("Zero length read.  Closing")
s.close()
