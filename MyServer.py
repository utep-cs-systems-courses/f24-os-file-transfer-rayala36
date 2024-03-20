#! /usr/bin/env python3

# Echo server program

import socket, sys, re, os, time
sys.path.append("lib")       # for params
import params
import Framer
import Buffer

def convertFromBin(len):
    decVal = 0
    div = 128
    if(len == 0):
        return len
    for bit in len:
        if(bit == "1"):
            decVal += div
        div = div//2
    return decVal

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

server = "MyServer"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''       # Symbolic name meaning all available interfaces

pidAddr = {}                    # for active connections: maps pid->client addr 

if paramMap['usage']:
    params.usage()

# server code to be run by child
def chatWithClient(connAddr):  
    sock, addr = connAddr
    print(f'Child: pid={os.getpid()} connected to client at {addr}')


    # Message to Client will be implemented here
    messagesToReceive = []
    messagesToReceive.append("Message.txt")
    # The map below will map file names to unique indices
    filesHM = {}
    br = Buffers.BufferedReader(sock.fileno())
    while(True):
        band = 8
        bandBytes = 0
        fileNameLenInB = ""
        while(bandBytes < band):
            binContents = os.read(sock.fileno(), 1)
            fileNameLenInB += binContents.decode()
            bandBytes += 1

        fileNameLenInB = convertFromBin(fileNameLenInB)

        if(fileNameLenInB == 0):
            return 0

        bandBytes = 0
        fName = ""
        while(bandBytes < fileNameLenInB):
            fName += os.read(sock.fileno(), 1).decode()
            bandBytes += 1

        # If there are duplicate files, the value corresponding to the file in the HM will increase by one for every duplicate
        if fName in filesHM:
            fName += str(filesHM[fName])
            filesHM[fName] += 1
        else:
            filesHM[fName] += 1

        os.chdir("MessageFolder")
        fName = os.open(fName, os.O_WRONLY)
        fLenInDec = ""
        bytesInLen = 0
        while(bytesInLen < 8):
            fLenInDec += os.read(sock.fileno(), 1).decode()
            bytesInLen += 1
            
        fLenInDec = convertFromBin(fLenInDec)

        bytesInLen = 0
        br = Buffers.BufferedReader(sock.fileno())
        bw = Buffers.BufferedWriter(fName)

        while(bytesInLen < fLenInDec):
            byteContents = br.readByte()
            bw.writeByte(byteContents)
            bytesInLen += 1
        bw.flush()
    print("File Transferred")

    sock.shutdown(socket.SHUT_WR)
    sys.exit(0)                 # terminate child

    
# My Own Socket Information will be implemented here


listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# listener socket will unbind immediately on close
listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# accept will block for no more than 5s
listenSock.settimeout(5)          
# bind listener socket to port
listenSock.bind((listenAddr, listenPort))
# set state to listen
listenSock.listen(1)              # allow only one outstanding request

# s is a factory for connected sockets


while True:
    # reap zombie children (if any)
    while pidAddr.keys():
        # Check for exited children (zombies).  If none, don't block (hang)
        if (waitResult := os.waitid(os.P_ALL, 0, os.WNOHANG | os.WEXITED)): 
            zPid, zStatus = waitResult.si_pid, waitResult.si_status
            print(f"""zombie reaped:
            \tpid={zPid}, status={zStatus}
            \twas connected to {pidAddr[zPid]}""")
            del pidAddr[zPid]
        else:
            break               # no zombies; break from loop
    print(f"Currently {len(pidAddr.keys())} clients")

    try:
        connSockAddr = listenSock.accept() # accept connection from a new client
    except TimeoutError:
        connSockAddr = None 

    if connSockAddr is None:
        continue
        
    forkResult = os.fork()     # fork child for this client 
    if (forkResult == 0):        # child
        listenSock.close()         # child doesn't need listenSock
        chatWithClient(connSockAddr)
    # parent
    sock, addr = connSockAddr
    sock.close()   # parent closes its connection to client
    pidAddr[forkResult] = addr
    print(f"spawned off child with pid = {forkResult} at addr {addr}")
    
