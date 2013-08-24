import sys
import urllib
from ftp_s3 import main

port = 21

# get an alternative port number
if len(sys.argv) >= 2:
    try:
        port = int(sys.argv[1])
    except ValueError:
        print "Invalid port number specified."
        sys.exit(1)

if 'internal' not in sys.argv:
    external_ip = urllib.urlopen("http://ifconfig.me/ip").read().strip()
else:
    external_ip = None

main.run(port, masquerade_address=external_ip)
