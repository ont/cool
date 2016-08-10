"""
Collection of tubes to build complex tubes for data processing.

Example usage:
    tube = MsgpackTube() | ZipTube()

    file = open('data.msg.z', 'wb')
    for chunk in tube([1,2,3,4,5], flush=True):
        file.write(chunk)

Code above will write to "data.msg.z" file serialized and
compressed version of list "[1,2,3,4,5]".

To process back:
    tube = UnzipTube() | MsgunpackTube()

    data = open('data.msg.z', 'rb').read
    for obj in tube(data):
        print('restored object:', obj)

"""
from .zip import ZipTube
from .unzip import UnzipTube
from .msgpack import MsgpackTube
from .msgunpack import MsgunpackTube
