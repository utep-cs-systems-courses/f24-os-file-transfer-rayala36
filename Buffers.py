#! /usr/bin/env python3

import sys
import os
import re
import subprocess

class BufferedWriter:
    def __init__(self, fd, buffSize=1024*16):
        # Every bufferedWriter will consist of a file descriptor, a byte array that will be written and a value to keep track of the position in the byte array
        self.fd = fd
        self.outBuffer = bytearray(buffSize)
        self.buffPos = 0

    def writeByte(self, byte):
        self.outBuffer[self.buffPos] = byte
        self.buffPos += 1
        if self.buffPos >= len(self.outBuffer):
            #Once a certain length is reached, the buffer will be closed, and data will have to be written in the next buffer.
            self.flush()

    # Data will be written from the starting index of the buffer to the last index
    # "0" will imply there is nothing to read.
    def flush(self):
        buffBeginInd, buffEndInd = 0, self.buffPos
        while buffBeginInd < buffEndInd:
            data = os.write(self.fd, self.outBuffer[buffBeginInd:buffEndInd])
            if data==0:
                os.write(2, f"Flush for the file descriptor {self.fd} Unsuccessful : :(\n".encode())
                sys.exit(1)
            buffBeginInd += data
        self.buffPos = 0
        
    def close(self):
        self.flush()
        os.close(self.fd)

class BufferedReader:
    # Every bufferedReader will consist of a file descriptor, a buffer from which data will be read, a position index in the buffer, and the buffer's size
    def __init__(self, fd, buffSize=1024*16):
        self.fd = fd
        self.inBuffer = b""
        self.buffPos = 0
        self.buffSize = buffSize

    # Each byte in the buffer will be read by traversing the buffer.
    def readByte(self):
        if self.buffPos >= len(self.inBuffer):
            self.inBuffer = os.read(self.fd, self.buffSize)
            self.buffPos=0

        #This indicates the buffer length is 0, in which case None will be returned
        if len(self.inBuffer)==0:
            return None
        else:
            # The buffer will be traversed and all read bytes will be accumulated in "read file data."
            readFileData = self.inBuffer[self.buffPos]
            self.buffPos += 1
            return readFileData
        
    def close(self):
        os.close(self.fd)
