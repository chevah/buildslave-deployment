# Copyright (c) 2010-2012 Adi Roiban.
# See LICENSE for details.
'''
Build script for Chevah Server buildbot slave.

It should work on all operating system, including Windows.
'''
import sys

from paver.easy import cmdopts, needs, task, consume_args, pushd
from paver.tasks import help

BUILD_PACKAGES = [
    # Main slave package.
    # We specify a custom twisted package, to use our patched version.
    'twisted==12.1.0.chevah4',
    'buildbot-slave==0.8.11.pre.143.gac88f1b.c1',

    'zope.interface==3.8.0',

    # Buildbot is used for try scheduler
    'buildbot',

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
SETUP['buildbot']['web_url'] = 'http://build.chevah.com:10088'
SETUP['pypi']['index_url'] = 'http://pypi.chevah.com:10042/simple'

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