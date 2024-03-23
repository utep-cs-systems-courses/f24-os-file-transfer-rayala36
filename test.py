#! /usr/bin/env python3

import Framer, Buffers, sys, os

bw = Buffers.BufferedWriter(1)
text = "I have an important message: Deh.".encode()
for bit in text:
    bw.writeByte(bit)
bw.flush()
