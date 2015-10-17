#!/bin/sh
### BEGIN INIT INFO
# Provides:          buildbot-slave
# Required-Start:    $local_fs $remote_fs $network $syslog
# Required-Stop:     $local_fs $remote_fs $network $syslog
# chkconfig:         2345 99 01
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: BuildBot Slave for Chevah Project
# Description:       BuildBot Slave for Chevah Project
### END INIT INFO

# Copy this file as /etc/init.d/buildbot-slave
#
# RedHat usage:
#  * enable service on all init levels:
#    chkconfig buildbot-slave --add
#  * enable service on selected init levels:
#    chkconfig buildbot-slave on --level 2,3,5
#  * start the service
#    service buildbot-slave start
#  * stop the service
#    service buildbot-slave stop
#
# Ubuntu/Debian usage:
#  * enable service on all init levels:
#    sudo update-rc.d buildbot-slave defaults
#  * enable service on selected init levels:
#    sudo update-rc.d buildbot-slave start 20 2 3 4 5 . stop 80 0 1 6 .
#  * start the service
#    sudo service buildbot-slave start
#  * stop the service
#    sudo service buildbot-slave stop

PATH=/opt/python2.5/bin:$PATH
export PATH

INSTALL_ROOT="/srv/buildslave/chevah/infrastructure/buildbot-slave"
COMMONS_BRANCH="/srv/buildslave/chevah/commons"
SERVICE_NAME="Chevah Buildbot Slave"
PID_FILE=$INSTALL_ROOT"/build-*/slave/twistd.pid"
LOG_FILE=$INSTALL_ROOT"/build-*/slave/twistd.log"
PAVER="/srv/buildslave/chevah/brink/paver.sh"

start_service() {
    echo -n "Starting ${SERVICE_NAME} services: "
    # Get the latest commons code in case these changes are required for
    # starting paver.
    cd $COMMONS_BRANCH
    sudo -E su buildslave -c "git pull"
    # The paver start target will do the rest.
    cd ${INSTALL_ROOT}
    sudo -E su buildslave -c "$PAVER start"
    echo "."
}

debug_service() {
    echo -n "Debugging ${SERVICE_NAME} services: "
    cd ${INSTALL_ROOT}
    sudo -E su buildslave -c "$PAVER debug"
}

stop_service() {
    echo -n "Shutting down ${SERVICE_NAME} services: "
    pid=`cat $PID_FILE`
    sudo -E kill $pid
    echo "."
}

status_service() {
    tail -f $LOG_FILE
}

case "$1" in
    start)
        start_service
    ;;
    stop)
        stop_service
    ;;
    status)
        status_service
    ;;
    debug)
        debug_service
    ;;
    restart)
        stop_service
        start_service
    ;;
    *)
        echo "Usage: ${SERVICE_NAME} {start|stop|restart|status|debug}"
        exit 1
    ;;
esac
