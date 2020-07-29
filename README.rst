Chevah Buildslave
=================

Buildbot slave files used by the Chevah project.

The build slave process is designed to be executed under a special
system account, typically ``buildslave``.

To run the build slave process in debug mode with logs in the current console::

    ./brink.sh debug

To start or stop the buildslave service, use::

    ./brink.sh start
    ./brink.sh stop

Logs are saved at ``build-OS-ARCH/slave/twistd.log``.


Usage on Windows
----------------

On Windows, only ``debug`` mode is supported as we don't run the build slave
process as a service/daemon.

To start the slave on Windows, we use a simple script that runs on boot to
launch the ``./brink.sh start`` command.
