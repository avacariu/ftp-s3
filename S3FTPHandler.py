import boto
from pyftpdlib.handlers import FTPHandler

class S3FTPHandler(FTPHandler):
    def __init__(self, *args, **kwargs):
        FTPHandler.__init__(self, *args, **kwargs)

    def on_logout(self, username):
        del self.authorizer.user_table[username]
