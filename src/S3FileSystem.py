import boto
from pyftpdlib.filesystems import AbstractedFS

import time
import datetime
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
            return map(lambda b: ('dir', 0, None, b.name), result_set)
        elif isinstance(result_set[0], boto.s3.key.Key):
            listing = []
            listing_names = []
            for key in result_set:
                if not key.name.startswith(key_path):
                    continue

                split_key = key.name.strip('/').split('/')
                try:
                    name = split_key[depth]
                except IndexError:
                    continue
                else:
                    dt_modified = key.last_modified

                    if key.name.count('/') > depth:
                        if name not in listing_names:
                            listing.append(('dir', 0, dt_modified, name))
                            listing_names.append(name)
                    else:
                        if name not in listing_names:
                            listing.append(('file', key.size, dt_modified, name))
                            listing_names.append(name)

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
                if not any(map(lambda k: k.name.startswith(key+'/'),
                                bucket.get_all_keys())):
                    return False

            return True

        else:
            return False


    def format_list(self, basedir, listing, ignore_err=True):
        for basename in listing:
            ft, size, last_modified, name = basename
            last_modified = _format_lm(last_modified, form="ls")

            if ft == 'dir':
                perm = "rwxrwxrwx"
                t = 'd'
            else:
                perm = "r-xr-xr-x"
                t = '-'

            line = "%s%s\t1\towner\tgroup\t%s\t%s\t%s\r\n" % (t, perm, size, last_modified, name)
            yield line.encode("utf8", self.cmd_channel.unicode_errors)

    def format_mlsx(self, basedir, listing, perms, facts, ignore_err=True):
        for basename in listing:
            ft, size, last_modified, name = basename
            last_modified = _format_lm(last_modified, form="mlsx")

            if ft == 'dir':
                perm = 'el'
            else:
                perm = 'r'
            line = "type=%s;size=%d;perm=%s;modify=%s %s\r\n" % (ft, size, perm, last_modified, name)
            yield line.encode("utf8", self.cmd_channel.unicode_errors)



def _format_lm(last_modified, form="object"):
    if last_modified is None:
        dt_modified = datetime.datetime(1970, 1, 1)
    else:
        try:
            #this is the format used when you use get_key()
            dt_modified = datetime.datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
        except ValueError:
            #this is the format used when you use get_all_keys()
            dt_modified = datetime.datetime.strptime(last_modified, '%Y-%m-%dT%H:%M:%S.000Z')
        except:
            raise

    if form == "object":
        return dt_modified
    elif form == "ls":
        if (datetime.datetime.now() - dt_modified).days < 180:
            return dt_modified.strftime("%b %d %H:%M")
        else:
            return dt_modified.strftime("%b %d %Y")
    else:
        return dt_modified.strftime("%Y%m%d%H%M%S")
