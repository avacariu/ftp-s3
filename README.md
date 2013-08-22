FTP frontend for S3
===================

This package provides a ftp server based on pyftpdlib. It maps USER command
to the S3 authentication on the fly, so you can log into the server with your
access key as your username and your secret key as your password, and the server
will authenticate against S3, and provide a listing of the directories and files
within.


Notes
-----

* The server displays buckets as if they're top level directories and parses the
  key names to figure out which are directories and which are files. This means
  that if you have a lot of keys in your bucket, this might take a while to do,
  and it doesn't get easier as you navigate down the tree, either, since it reads
  all the keys each time. This is definitely something to look into to optimize.

* Only reading works. Writing has not been implemented yet. 
