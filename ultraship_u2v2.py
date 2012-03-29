#!/usr/bin/env python

"""
ultraship_u2v2_serial.py

Code for interfacing with MyWeigh Ultraship U2 USB scales that use a PL2303
USB serial interface.

Licensed under a Simplified BSD License:

Copyright (c) 2012, Timothy Twillman
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
TIMOTHY TWILLMAN OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are
those of the authors and should not be interpreted as representing official
policies, either expressed or implied, of Timothy Twillman.
"""

import struct


class UltrashipU2v2(object):

    """Class for interfacing with USB-Serial version of UltraShip U2 scales.

    This handles reading / parsing packets sent by the scale when the "SEND"
    button is pushed.

    Note: It is not able to request data from the scale, or to get any more
    information than what is displayed on the top line of the display, and
    it's unknown whether those features might be possible with this scale.

    Version 1 of the scale used a USB HID interface; this class does not
    support that version.
    """

    def __init__(self, port):
        """Initialize the scale object."""
        port.baudrate = 9600
        self._port = port
        self._buf = ''

    def fill_buffer(self):
        c = self._port.read(14 - len(self._buf))
        self._buf += c

    @staticmethod
    def parse_packet(pkt):
        """Parse a scale packet & return the parsed value, or None if invalid.

        Args:
            pkt:  A 14-character string; should hold 1 packet of scale information.

        Returns:
            A string containing the packet's decoded contents, or None if the
            passed in array is not a valid packet.


        A properly formed packet is 14 bytes long.
         0: STX (0x02)
         1: XOR key for following bytes (needs to also be XORed with 0x26)
         2..10: Data Bytes
        11: Checksum High Byte
        12: Checksum Low Byte
        13: ETX (0x03)

        Checksum is calculated by simply adding together all of the bytes
        from index 1..10, before decoding with the key.
        """
        if len(pkt) >= 14:
            # The H is for the (big endian, 2-byte) checksum.
            data = struct.unpack('>BBBBBBBBBBBHB', pkt[0:14])

            if data[0] == 0x02 and data[12] == 0x03 and sum(data[1:11]) == data[11]:
                # Decode data bytes
                key = data[1] ^ 0x26
                # data[2] is a newline; toss it out.
                data = [ (data[i] ^ key) for i in range(3, 11) ]

                return struct.pack('BBBBBBBB', *data)

        return None

    def read(self):
        """Read a (decoded) packet's worth of data from the scale.

        This will keep reading bytes until it gets a valid packet, then will
        decode the packet and return the decoded contents (a string).
        """
        while True:
            self.fill_buffer()

            # Dump characters until find STX
            self._buf = self._buf[self._buf.find('\x02'):]

            while len(self._buf) >= 14:
                # Try to parse the packet... hopefully it's valid.
                result = self.parse_packet(self._buf)
                if result:
                    self._buf = self._buf[14:]
                    return result
                else:
                    # Bad packet.  Dump everything up to next STX and
                    # continue looking for a valid packet.
                    self._buf = self._buf[self._buf.find('\x02', 1):]

def main():
    """Basic main function for getting data from a scale and printing it out.

    To use, pass the device name of the USB port the scale is on
    (e.g. /dev/ttyACM0) on the command line.  When the "SEND" button on the
    scale is pressed, the program should output the number that is on the
    scale's display.
    """
    import serial
    import optparse
    import sys

    parser = optparse.OptionParser()
    (opts, args) = parser.parse_args()

    if not args:
        print >> sys.stderr, 'Please provide a device name on the command line.'
        sys.exit(1)

    port = serial.Serial(args[0])
    scale = UltrashipU2v2(port)

    while True:
        try:
            print "%s" % (scale.read())
        except KeyboardInterrupt:
            print >> sys.stderr, "Caught CTRL-C; exiting..."
            sys.exit(0)

if __name__ == '__main__':
    main()

