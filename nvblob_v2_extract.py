#!/bin/python
"""
Extracts NVIDIA blobs
"""

import os
import sys
import struct

BLOB_FORMATS =  {
                'update'       : ('=40sIII',    struct.calcsize('=40sIII')),
                'bmp'          : ('=IIII36s',   struct.calcsize('=IIII36s')),
                'compressed'   : ('=16sIIIIII', struct.calcsize('=16sIIIIII')),
                'uncompressed' : ('=16sIIIII',  struct.calcsize('=16sIIIII'))
                }

class Blob(object):
    def __init__(self, filename):
        self.filename = filename
        self._magic = None
        self._is_compressed = None
        self._type = None
        self._data = None
        self._magic_struct = None
        self._chunk_struct = None
    @property
    def magic(self):
        if self._magic is None:
            with open(self.filename, 'rb') as blob:
                magic_struct = '=16sIIIIII'
                size = struct.calcsize(magic_struct)
                self._magic = list(struct.unpack(magic_struct, blob.read(size)))
        assert self._magic[0] == b'NVIDIA__BLOB__V2', ("Not a NVIDIA blob!")
        return self._magic
    @property
    def is_compressed(self):
        if self._is_compressed is None:
            self._is_compressed = self.magic[6] == 0
        return self._is_compressed
    @property
    def type(self):
        if self._type is None:
            if self.magic[5] == 0:
                self._type = "update"
            else:
                self._type = "bmp"
        return self._type
    @property
    def magic_struct(self):
        if self._magic_struct is None:
            if self.is_compressed:
                self._magic_struct = BLOB_FORMATS['compressed']
            else:
                self._magic_struct = BLOB_FORMATS['uncompressed']
        return self._magic_struct
    @property
    def chunk_struct(self):
        if self._chunk_struct is None:
            if self.type == "update":
                self._chunk_struct = BLOB_FORMATS['update']
            elif self.type == "bmp":
                self._chunk_struct = BLOB_FORMATS['bmp']
        return self._chunk_struct
    @property
    def data(self):
        if self.is_compressed or self.type is 'bmp':
            raise NotImplementedError("This tool doesn't yet support extraction of bmp or compressed blobs")
        if self._data == None:
            self._data = []
            with open (self.filename, 'rb') as blob:
                for i in range(0, self.magic[4]):
                    offset = self.magic_struct[1]+(i*self.chunk_struct[1])
                    blob.seek(offset)
                    rawdata = blob.read(self.chunk_struct[1])
                    data = struct.unpack(self.chunk_struct[0], rawdata)
                    part_name = data[0].split(b'\x00')[0].decode("utf-8")
                    self._data.append({
                                        'name': part_name,
                                        'pos': data[1],
                                        'len': data[2]
                                     })
        return self._data
    def extract(self, part_num, out):
        if self.is_compressed or self.type is 'bmp':
            raise NotImplementedError("This tool doesn't yet support extraction of bmp or compressed blobs")
        with open(out, 'wb') as output:
            with open(self.filename, 'rb') as blob:
                blob.seek(self.data[part_num]['pos'])
                output.write(blob.read(self.data[part_num]['len']))


if __name__ == "__main__":
    blob = Blob(sys.argv[1])
    if len(sys.argv) >= 2:
        outfolder = sys.argv[2]
    else:
        outfolder = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    i = 0
    print("Extracting {} files to {}".format(len(blob.data), outfolder))
    for file in blob.data:
        out = os.path.join(outfolder, file['name'])
        if os.path.exists(out):
            out_old = out
            j = 0
            while os.path.exists(out):
                out = out_old+'_'+str(j)
                j += 1
        blob.extract(i, out)
        i += 1
