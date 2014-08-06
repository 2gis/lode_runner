# coding: utf-8

from nose.plugins.multiprocess import MultiProcessTestRunner, MultiProcess


class MultiProcess(MultiProcess):
    def prepareTestRunner(self, runner):
        super(MultiProcess, self).prepareTestRunner(runner)


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