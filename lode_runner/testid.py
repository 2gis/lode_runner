# coding: utf-8
import multiprocessing
import sys
import os

try:
    from cPickle import dump, load
except ImportError:
    from pickle import dump, load

from nose.plugins.testid import TestId
from nose.plugins import Plugin
from nose.util import split_test_name


MANAGER = multiprocessing.Manager()
IDS = MANAGER.dict()
TESTS = MANAGER.dict()
SEEN = MANAGER.dict()
FAILED = MANAGER.list()
FAILED_LOADED = MANAGER.list()
SOURCE_NAMES = MANAGER.list()
TRANSLATED = MANAGER.list()
COLLECTING = MANAGER.Value(bool, True)


class TestId(TestId):
    collecting = COLLECTING

    def configure(self, options, conf):
        """Configure plugin.
        """
        Plugin.configure(self, options, conf)
        if options.failed:
            self.enabled = True
            self.loopOnFailed = True
        self.idfile = os.path.expanduser(options.testIdFile)
        if not os.path.isabs(self.idfile):
            self.idfile = os.path.join(conf.workingDir, self.idfile)
        self.id = 1
        self.ids = IDS
        self.tests = TESTS
        self.failed = FAILED
        self.failed_loaded = FAILED_LOADED
        self.source_names = SOURCE_NAMES
        self.translated = TRANSLATED
        # used to track ids seen when tests is filled from
        # loaded ids file
        self._seen = SEEN

        self._write_hashes = conf.verbosity >= 2
        self.stream = sys.stderr

    def _load_from_file(self, names):
        if not len(self.ids):
            try:
                fh = open(self.idfile, 'rb')
                data = load(fh)
                if 'ids' in data:
                    self.ids.update(data['ids'])
                    self.failed_loaded += data['failed']
                    self.source_names += data['source_names']
                else:
                    # old ids field
                    self.ids.update(data)
                    self.source_names += names
                if len(self.ids):
                    self.id = len(self.ids) + 1
                    self.tests.update(dict(list(zip(list(self.ids.values()), list(self.ids.keys())))))
                else:
                    self.id = 1
                fh.close()

                if self.loopOnFailed and len(self.failed_loaded):
                    failed = []
                    for name in list(self.failed_loaded):
                        failed.append(name)

                    del self.failed_loaded[:]
                    return failed
            except IOError:
                pass

        return names

    def loadTestsFromNames(self, names, module=None):
        """Translate ids in the list of requested names into their
        test addresses, if they are found in my dict of tests.
        """
        names = self._load_from_file(names)

        # I don't load any tests myself, only translate names like '#2'
        # into the associated test addresses
        new_source = []
        really_new = []
        translated = []
        for name in names:
            trans = self.tr(name)
            if trans != name:
                translated.append(trans)
                self.translated.append(trans)
            else:
                new_source.append(name)

        filtered = []
        if self.loopOnFailed and len(self.translated):
            for name in list(self.translated):
                test = parse_test_name(names[0])
                filtering = parse_test_name(name)
                if test[0] == filtering[0] and test[1] == filtering[1]:
                    filtered.append(name)
                    self.translated.remove(name)

        # names that are not ids and that are not in the current
        # list of source names go into the list for next time
        if new_source:
            old_set = set(self.source_names)
            really_new = [s for s in new_source
                          if not s in old_set]
            if really_new:
                # remember new sources
                self.source_names.extend(really_new)
            if not self.translated:
                # new set of source names, no translations
                # means "run the requested tests"
                names = new_source
        else:
            # no new names to translate and add to id set
            # self.collecting = False
            pass

        return (None, translated + really_new + filtered or names)

    def finalize(self, result):
        """Save new ids file, if needed.
        """
        ids = dict(self.ids)
        source_names = list(self.source_names)
        failed = list(self.failed)
        tests = dict(self.tests)

        if result.wasSuccessful():
            failed = []
        if self.collecting:
            ids = dict(list(zip(list(tests.values()), list(tests.keys()))))
        else:
            pass
        fh = open(self.idfile, 'wb')
        dump({'ids': ids,
              'failed': failed,
              'source_names': source_names}, fh)
        fh.close()


def parse_test_name(test):
    test_file, _, class_and_name = split_test_name(test)
    try:
        test_class, test_name = class_and_name.split(".")
    except AttributeError:
        test_class, test_name = (None, None)
    except ValueError:
        test_class, test_name = class_and_name, None

    return test_file, test_class, test_name
# do not collect
parse_test_name.__test__ = False
