#! /usr/bin/env python3

import sys
import os
import re
import subprocess
from Buffers import BufferedWriter, BufferedReader

class Framer:
    def __init__(self, bWr):
        self.bWr = bWr
        
    def writtenBytes(self, ibRegex):
        if ibRegex == ord('-'):
            self.bWr.writeByte(ibRegex)
        self.bWr.writeByte(ibRegex)
        
    def byteArray(self, byteArray):
        for ibRegex in byteArray:
            self.writtenBytes(ibRegex)

    def frameEnd(self):
        self.bWr.writeByte(ord('-'))
        self.bWr.writeByte(ord('f'))
        self.bWr.flush()
        
class DeFramer:
    def __init__(self, buffRdr):
        self.buffRdr = buffRdr

    def frameEndDetector(self, ibRegex):
        if ibRegex==ord('-'):
            nextChar = self.buffRdr.readByte()
            if nextChar == ord('f'):
                return False
        return True

    def readByte(self):
        data = ''

        while((byte := self.buffRdr.readByte()) != None):
            validData = self.frameEndDetector(byte)
            if validData:
                data += chr(byte)
            if not validData:
                return validData
        return None
