from .S3Authorizer import S3Authorizer
from .S3FileSystem import S3FileSystem
from .S3FTPHandler import S3FTPHandler

from pyftpdlib.servers import FTPServer

import urllib
import sys

def run(port=21, passive_ports=range(60000,65535), masquerade_address=None):
    authorizer = S3Authorizer()

    handler = S3FTPHandler
    handler.authorizer = authorizer
    handler.abstracted_fs = S3FileSystem

    if masquerade_address is not None:
        handler.masquerade_address = masquerade_address

    handler.permit_foreign_addresses = True
    handler.passive_ports = passive_ports

    server = FTPServer(('', port), handler)
    server.serve_forever()

if __name__ == "__main__":
    run()
