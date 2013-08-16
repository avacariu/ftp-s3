from S3Authorizer import S3Authorizer
from S3FileSystem import S3FileSystem
from S3FTPHandler import S3FTPHandler

from pyftpdlib.servers import FTPServer

def main():
    authorizer = S3Authorizer()
    handler = S3FTPHandler
    handler.authorizer = authorizer
    handler.abstracted_fs = S3FileSystem
    server = FTPServer(('', 2121), handler)
    server.serve_forever()

if __name__ == "__main__":
    main()
