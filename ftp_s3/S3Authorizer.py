import boto
from pyftpdlib.authorizers import DummyAuthorizer, AuthenticationFailed

class S3Authorizer(DummyAuthorizer):
    def __init__(self, *args, **kwargs):
        DummyAuthorizer.__init__(self, *args, **kwargs)
        self.conn = None

    def validate_authentication(self, aws_access_key_id, aws_secret_access_key, handler):
        self.conn = boto.connect_s3(aws_access_key_id, aws_secret_access_key)

        try:
            self.conn.get_all_buckets()
        except boto.exception.S3ResponseError:
            self.conn = None
            raise AuthenticationFailed
        else:
            if not self.has_user(aws_access_key_id):
                self.add_user(aws_access_key_id, u'', u'/', perm="elr")
            return True
