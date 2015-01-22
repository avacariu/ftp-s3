FTP frontend for S3
===================

This package provides an FTP server based on pyftpdlib and boto. It maps FTP
commands to S3 API calls. Authentication is done using the USER command with
your access key as your username and your secret key as your password.

Usage
-----

Execute `run.py [port] [internal]`, where `port` is the port number you want the
server to run on, and `internal` is the literal string you can use to disable
masquerading.

`ftp_s3` is a module with `ftp_s3.main.run()` being the function that puts the
entire thing together and runs the server.


Notes
-----

* The server displays buckets as if they're top level directories and parses the
  key names to figure out the directory structure. This means that if you have a 
  lot of keys in your bucket, it might take a while, and it doesn't get quicker
  as you navigate down the tree, either, since it reads all the keys each time.
  This is caused by a limitation of the API which doesn't deal with directory 
  structure itself.

  This is definitely something worth optimizing, possibly by caching the results,
  or relying on the order of the returned keys (which appears alphabetical).

* Permissions aren't properly mapped. PR would be appreciated to fix this!

* Only reading works. Writing has not been implemented yet.
