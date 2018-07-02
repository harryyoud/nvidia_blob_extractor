#!/bin/python
"""
Extracts NVIDIA blobs
"""

import os
import sys
import struct

def main(filepath):
    with open(filepath, 'rb') as blob:
        header = list(struct.unpack('=16sIIIIII', blob.read(struct.calcsize('=16sIIIIII'))))
        assert header[0] == b'NVIDIA__BLOB__V2', ("Not a NVIDIA blob!")
        print('[I] HEADER: {}'.format(header))
        if header[6] != 0:
            del header[6]
            print("[I] Blob does not support compression")
        if header[5] == 0:
            print("[I] Blob is update type")
        else:
            print("[I] Blob is bmp type")
        files = []
        for i in range(0, header[4]):
            offset = 36+(i*52)
            blob.seek(offset)
            rawd = blob.read(52)
            data = struct.unpack('=40sIII', rawd)
            name = data[0].split(b'\x00')[0].decode("utf-8")
            files.append({'name': name, 'pos': data[1], 'len': data[2]})
        for file in files:
            name = 'out/'+file['name']
            while os.path.isfile(name):
                name = name+'_'+str(i)
                i += 1
            with open(name, 'wb') as output:
                blob.seek(file['pos'])#36+(header[4]*52))
                output.write(blob.read(file['len']))


if __name__ == "__main__":
    main(sys.argv[1])
