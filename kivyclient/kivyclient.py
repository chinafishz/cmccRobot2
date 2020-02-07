import sys
sys.path.append('.')

from libs.thrift_file.gen_py.test import Transmit
from libs.thrift_file.gen_py.test.ttypes import *
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer



class TransmitHandler:
    def __init__(self):
        pass

    def saytext(self, from_usename, msg):
        print(from_usename, msg)
        return 'done'

    def saybinary(self,from_usename, data_binary):
        with open('abc.jpg','wb') as f:
            f.write(data_binary)
        print(from_usename)
        return 'done'

if __name__=="__main__":
    handler = TransmitHandler()
    processor = Transmit.Processor(handler)

    # kivyclient 监听端口为29981
    # itchatserver 监听端口为29982
    transport = TSocket.TServerSocket('127.0.0.1', 29981)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    print("Starting thrift server of kivyclient...")
    server.serve()