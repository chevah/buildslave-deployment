# Copyright (c) 2010-2012 Adi Roiban.
# See LICENSE for details.
'''
Build script for Chevah Server buildbot slave.

It should work on all operating system, including Windows.
'''
import sys
import os

from paver.easy import cmdopts, needs, task, consume_args, pushd
from paver.tasks import help

BUILD_PACKAGES = [
    # Main slave package.
    # We specify a custom twisted package, to use our patched version.
    'twisted==12.1.0.chevah12',
    'buildbot-slave==0.8.11.pre.143.gac88f1b.c1',

    'zope.interface==3.8.0',

    # Required for some unicode handling.
    'unidecode',
    ]

from brink.pavement_commons import (
    clean,
    default,
    harness,
    lint,
    pave,
    SETUP,
    )

# Make pyflakes shut up.
clean
default
harness
help
lint

SETUP['folders']['source'] = 'src'
SETUP['buildbot']['server'] = 'buildbot.chevah.com'
SETUP['buildbot']['web_url'] = 'https://chevah.com/buildbot/'
SETUP['pypi']['index_url'] = 'http://pypi.chevah.com/simple'

option_name = (
    'name=',
    'n',
    'Name of the buildslave. '
        'Must be a name configured in the buildbot master.',
    )


@task
def deps():
    """
    Copy external dependencies.
    """
    print('Installing dependencies to %s...' % (pave.path.build))
    pave.pip(
        command='install',
        arguments=BUILD_PACKAGES,
        )


@task
def build():
    '''Copy the required files for running buildbot.'''
    target = pave.path.build
    pave.fs.copyFolder(source=['src'], destination=[target, 'slave'])
    ip = pave.getIPAddress()
    pave.fs.appendContentToFile(
        destination=[target, 'slave', 'info', 'host'],
        content='\n' + ip + '\n')


@task
@consume_args
def buildslave(args):
    '''Run the buildslave command.'''
    from buildslave.scripts import runner
    new_args = ['buildslave']
    new_args.extend(args)
    sys.argv = new_args

    with pushd(pave.fs.join(pave.path.build, 'slave')):
        runner.run()


@task
@needs('deps', 'build')
@cmdopts([option_name])
def start(options):
    '''Start the slave buildbot.'''
    _remove_empty_pid_file()
    from buildslave.scripts import runner

    # Set buildslave name to be used in buildbot.tac.
    sys.buildslave_name = pave.getOption(
        options, 'start', 'name', default_value=pave.getHostname())

    new_args = [
        'buildslave', 'start', pave.fs.join([pave.path.build, 'slave'])]
    sys.argv = new_args
    runner.run()


@task
def stop():
    '''Stop the master buildbot.'''
    from buildslave.scripts import runner
    new_args = [
        'buildslave', 'stop', pave.fs.join([pave.path.build, 'slave'])]
    sys.argv = new_args
    runner.run()


@task
@needs('build')
@cmdopts([option_name])
def debug(options):
    '''Run the buildslave without forking in background.'''
    _remove_empty_pid_file()

    # Set buildslave name to be used in buildbot.tac.
    sys.buildslave_name = pave.getOption(
        options, 'debug', 'name', default_value=pave.getHostname())

    argv = [
        'twistd',
        '--no_save',
        '--nodaemon',
        '--logfile=-',
        '--python=buildbot.tac',
        ]
    sys.argv = argv

    try:
        from setproctitle import setproctitle
        setproctitle  # Shut up the linter.
    except ImportError:
        setproctitle = lambda t: None

    setproctitle('buildbot-slave')

    from twisted.scripts import twistd
    with pushd(pave.fs.join([pave.path.build, 'slave'])):
        twistd.run()

def _remove_empty_pid_file():
    """
    Remove zero-sized PID file from Twisted. Otherwise, Twisted fails to start.
    """
    pid_name = 'twistd.pid'
    with pushd(pave.fs.join([pave.path.build, 'slave'])):
        if not os.path.exists(pid_name):
            # All good, there is no PID file, nothing to do.
            return
        if os.stat(pid_name).st_size == 0:
            # PID file is empty. Remove it to prevent Twisted bailing out.
            print('Removing zero-sized PID file from Twisted: %s' % (pid_name))
            os.remove(pid_name)
