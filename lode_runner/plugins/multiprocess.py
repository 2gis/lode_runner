# coding: utf-8

import unittest
import signal
import pickle
import time

from nose.pyversion import bytes_
from nose.suite import ContextSuite

from nose.plugins.multiprocess import MultiProcessTestRunner, MultiProcess

_instantiate_plugins = None


class MultiProcess(MultiProcess):
    def options(self, parser, env):
        """
        Register command-line options.
        """
        timeout = 60000
        parser.add_option("--processes", action="store",
                          default=env.get('NOSE_PROCESSES', 0),
                          dest="multiprocess_workers",
                          metavar="NUM",
                          help="Spread test run among this many processes. "
                          "Set a number equal to the number of processors "
                          "or cores in your machine for best results. "
                          "Pass a negative number to have the number of "
                          "processes automatically set to the number of "
                          "cores. Passing 0 means to disable parallel "
                          "testing. Default is 0 unless NOSE_PROCESSES is "
                          "set. "
                          "[NOSE_PROCESSES]")
        parser.add_option("--process-restartworker", action="store_true",
                          default=env.get('NOSE_PROCESS_RESTARTWORKER', False),
                          dest="multiprocess_restartworker",
                          help="If set, will restart each worker process once"
                          " their tests are done, this helps control memory "
                          "leaks from killing the system. "
                          "[NOSE_PROCESS_RESTARTWORKER]")
        parser.add_option("--process-timeout", action="store",
                          default=env.get('NOSE_PROCESS_TIMEOUT', timeout),
                          dest="multiprocess_timeout",
                          metavar="SECONDS",
                          help="Set timeout for return of results from each "
                          "test runner process. Default is %s. "
                          "[NOSE_PROCESS_TIMEOUT]" % timeout)

    def prepareTestRunner(self, runner):
        """Replace test runner with MultiProcessTestRunner.
        """
        # replace with our runner class
        return MultiProcessTestRunner(stream=runner.stream,
                                      verbosity=runner.config.verbosity,
                                      config=runner.config,
                                      loaderClass=self.loaderClass)


class MultiProcessTestRunner(MultiProcessTestRunner):
    def nextBatch(self, test):
        # allows tests or suites to mark themselves as not safe
        # for multiprocess execution
        if hasattr(test, 'context'):
            if not getattr(test.context, '_multiprocess_', True):
                return

        if ((isinstance(test, ContextSuite)
             and test.hasFixtures(self.checkCanSplit))
            or not getattr(test, 'can_split', True)
            or not isinstance(test, unittest.TestSuite)):
            # regular test case, or a suite with context fixtures

            # special case: when run like nosetests path/to/module.py
            # the top-level suite has only one item, and it shares
            # the same context as that item. In that case, we want the
            # item, not the top-level suite
            # if isinstance(test, ContextSuite):
            #     contained = list(test)
            #     if (len(contained) == 1
            #         and getattr(contained[0],
            #                     'context', None) == test.context):
            #         test = contained[0]
            yield test
        else:
            # Suite is without fixtures at this level; but it may have
            # fixtures at any deeper level, so we need to examine it all
            # the way down to the case level
            for case in test:
                for batch in self.nextBatch(case):
                    yield batch

    def startProcess(self, iworker, testQueue, resultQueue, shouldStop, result):
        from nose.plugins.multiprocess import Value, Event, Process
        from nose.plugins.multiprocess import signalhandler

        currentaddr = Value('c', bytes_(''))
        currentstart = Value('d', time.time())
        keyboardCaught = Event()

        mp_context = {plugin.name: plugin.mp_context for plugin in _instantiate_plugins if 'mp_context' in dir(plugin)}
        p = Process(target=runner,
                    args=(
                        iworker, testQueue,
                        resultQueue,
                        currentaddr,
                        currentstart,
                        keyboardCaught,
                        shouldStop,
                        self.loaderClass,
                        result.__class__,
                        pickle.dumps(self.config),
                        _instantiate_plugins,
                        mp_context))
        p.currentaddr = currentaddr
        p.currentstart = currentstart
        p.keyboardCaught = keyboardCaught
        old = signal.signal(signal.SIGILL, signalhandler)
        p.start()
        signal.signal(signal.SIGILL, old)
        return p


def runner(ix, testQueue, resultQueue, currentaddr, currentstart,
           keyboardCaught, shouldStop, loaderClass, resultClass, config, plugins, mp_context):
    from logging import getLogger

    try:
        from Queue import Empty
    except ImportError:
        from queue import Empty

    log = getLogger(__name__)
    try:
        try:
            for key in mp_context:
                plugin = next(x for x in plugins if x.name == key)
                plugin.mp_context = mp_context[key]
            return __runner(ix, testQueue, resultQueue, currentaddr, currentstart,
                            keyboardCaught, shouldStop, loaderClass, resultClass, config, plugins)
        except KeyboardInterrupt:
            log.debug('Worker %s keyboard interrupt, stopping', ix)
    except Empty:
        log.debug("Worker %s timed out waiting for tasks", ix)


def __runner(ix, testQueue, resultQueue, currentaddr, currentstart,
             keyboardCaught, shouldStop, loaderClass, resultClass, config, plugins):
    import nose.plugins.multiprocess as mp

    mp._instantiate_plugins = plugins
    mp.__runner(ix, testQueue, resultQueue, currentaddr, currentstart,
                keyboardCaught, shouldStop, loaderClass, resultClass, config)
