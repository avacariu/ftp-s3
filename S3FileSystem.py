import boto
from pyftpdlib.filesystems import AbstractedFS

import time
import os

class S3FileSystem(AbstractedFS):
    def __init__(self, *args, **kwargs):
        AbstractedFS.__init__(self, *args, **kwargs)

        self.conn = self.cmd_channel.authorizer.conn

    def realpath(self, path):
        return path

    def open(self, filename, mode):
        file_wrapper = self.mkstemp()
        fd = file_wrapper.file

        full_path = self.ftp2fs(filename)
        bucket_name = full_path.split('/')[1]

        try:
            bucket = self.conn.get_bucket(bucket_name)
        except:
            raise # TODO: Raise a proper exception here

        key_path = full_path[2 + len(bucket_name):]

        key = bucket.get_key(key_path)
        fd.write(key.read())
        fd.close()

        return open(file_wrapper.name, 'rb')

    def chdir(self, path):
        assert isinstance(path, unicode), path
            
        self._cwd = self.fs2ftp(path)

    def _gen_listing(self, key_path, result_set, depth=0):
        if isinstance(result_set[0], boto.s3.bucket.Bucket):
            return map(lambda b: ('dir', b.name), result_set)
        elif isinstance(result_set[0], boto.s3.key.Key):
            listing = []
            for key in result_set:
                if not key.name.startswith(key_path):
                    continue

                split_key = key.name.strip('/').split('/')
                try:
                    name = split_key[depth]
                except IndexError:
                    continue
                else:
                    if key.name.count('/') > depth:
                        if ('dir', name) not in listing:
                            listing.append(('dir', name))
                    else:
                        if ('file', name) not in listing:
                            listing.append(('file', name))

            return listing
        else:
            raise Exception


    def listdir(self, path):
        full_path = self.ftp2fs(path)

        if full_path == self.root:
            return self._gen_listing(None, self.conn.get_all_buckets())

        bucket_name = full_path.split('/')[1]

        try:
            bucket = self.conn.get_bucket(bucket_name)
        except:
            raise # TODO: Raise a proper exception here

        keys = bucket.get_all_keys()
        key_path = full_path[2 + len(bucket_name):]

        return self._gen_listing(key_path, keys, depth=(len(full_path.strip('/').split('/')) - 1))


    def isfile(self, path):
        if path.startswith('/'):
            bucket_name = path.split('/')[1]
            try:
                bucket = self.conn.get_bucket(bucket_name)
            except:
                return False

            if len(path.split('/')) > 3:
                key = path[2 + len(bucket_name) :]
                if key not in map(lambda k: k.name, bucket.get_all_keys()):
                    return False

            return True

        else:
            return False

    def islink(self, path):
        return False

    def isdir(self, path):
        if path.startswith('/'):
            bucket_name = path.split('/')[1]
            try:
                bucket = self.conn.get_bucket(bucket_name)
            except:
                return False

            if len(path.split('/')) > 3:
                key = path[2 + len(bucket_name) :]
                if key + '/' not in map(lambda k: k.name, bucket.get_all_keys()):
                    return False

            return True

        else:
            return False


    def format_list(self, basedir, listing, ignore_err=True):
        print "request for ls"
        for basename in listing:
            ft, name = basename
            if ft == 'dir':
                size = 0
                perm = "rwxrwxrwx"
                t = 'd'
            else:
                size = 0
                perm = "r-xr-xr-x"
                t = '-'

            line = "%s%s\t1\towner\tgroup\t%s\tSep 02 18:23\t%s\r\n" % (t, perm, size, name)
            yield line.encode("utf8", self.cmd_channel.unicode_errors)

    def format_mlsx(self, basedir, listing, perms, facts, ignore_err=True):
        print "request for mlsx"
        for basename in listing:
            ft, name = basename
            if ft == 'dir':
                size = 0
                perm = 'el'
            else:
                perm = 'r'
            line = "type=%s;size=0;perm=%s; %s\r\n" % (ft, perm, name)
            yield line.encode("utf8", self.cmd_channel.unicode_errors)

