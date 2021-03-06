# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
import os
import sys

from twisted.application import service
from buildslave.bot import BuildSlave

# Default host reachable inside the VPN.
# Update it when accessing from external networks.
buildmaster_host = 'buildmaster.chevah.com'
port = 10089

# Get the buildslave_name set by paver.
# Update this when accesing from an external slave.
slavename = sys.buildslave_name
passwd = 'password'

basedir = '.'
rotateLength = 10000000
maxRotatedFiles = 10
umask = 0002

if os.name == 'nt':
    # On Windows we set a short path that contains `chevah`.
    basedir = 'c:\\Users\\buildslave\\chevah\\bs'
    if not os.path.exists(basedir):
        os.makedirs(basedir)

# if this is a relocatable tac file, get the directory containing the TAC
if basedir == '.':
    import os.path
    basedir = os.path.abspath(os.path.dirname(__file__))

# note: this line is matched against to check that this is a buildslave
# directory; do not edit it.
application = service.Application('buildslave')

if '--nodaemon' not in sys.argv:
    try:
        from twisted.python.logfile import LogFile
        from twisted.python.log import ILogObserver, FileLogObserver
        logfile = LogFile.fromFullPath(
            os.path.join(basedir, "twistd.log"),
            rotateLength=rotateLength,
            maxRotatedFiles=maxRotatedFiles,
            )
        application.setComponent(ILogObserver, FileLogObserver(logfile).emit)
    except ImportError:
        # probably not yet twisted 8.2.0 and beyond, can't set log yet
        pass

keepalive = 100
usepty = 0
maxdelay = 300
umask = 002

print 'Launching slave "%s"' % slavename
s = BuildSlave(buildmaster_host, port, slavename, passwd, basedir,
               keepalive, usepty, umask=umask, maxdelay=maxdelay)
s.setServiceParent(application)
