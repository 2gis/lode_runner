## 0.4.4

- Add 'lode_runner.plugins.Suppressor' plugin. Allows suppress any exceptions in tearDown-methods

- Add optional parameter '--xunit-dump-suite-output'. If enabled drops TestSuite-level sysout/syserr to XUnit report.

## 0.4.3

- Add XUnit plugin 'lode_runner.plugins.ClassSkipper'. Allows skip TestClasses with no setUpClass calls

## 0.4.2

- Skip 'nose.multiprocess' testcases dirung merging xml files

## 0.4.1

- XUnit plugin now prints full path to created xUnit report

## 0.4.0

- Add plugin Failer that allows to stop test execution after X failures/errors.

## 0.3.1

- Add option for logging dataproviders dataset

## 0.3.0

- Add optional dataproviders dataset verbosity

## 0.2.8

- Fix test doc when using dataprovider

## 0.2.7

- Fix test_suite_name setting

## 0.2.6

- Fix test suite name in xUnit report, now using self.xunit_testsuite_name

