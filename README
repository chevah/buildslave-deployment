Chevah Buildslave
=================

Buildbot slave part files used by the Chevah project.

The buildslave is designed to be executed under a special system account.

To run the builslave in debug mode, use::

    paver debug -n BUILDSLAVE

BUILDSLAVE is one of the names configured in buildbot-master. This paver
task will run in foreground, listing all logs in the console.

To start or stop the buildslave service, use::

    paver start -n BUILDSLAVE
    paver stop

The log file is located in build-ARCH/slave/twisted.log.


Usage on Windows
----------------

On Windows, only debug mode is supported since we don't run the buildslave
as a service/daemon.

To start the slave on Windows log using a remote session and make sure
the session is remains after you disconnect.

Use `local_paver.sh debug` for starting the buildslave.


Usage on OSX
-------------

Copy plist file in /Library/LaunchDaemons/chevah.buildslave.plist
Load the service::

    launchctl load -w /Library/LaunchDaemons/chevah.buildslave.plist

Create `buildslave` account with admin right.
Create `/var/log/buildslave` folder with write permissions for buildslave
account.

Reboot or force service start::

    launchctl start com.chevah.buildslave
