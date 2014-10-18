# coding: utf-8

import argparse
from xml.etree import ElementTree


parser = argparse.ArgumentParser()
parser.add_argument("input", metavar='report', type=str, nargs='+')
parser.add_argument("-o", "--output", type=str, default="output.xml")


def write_output(root, stream):
    ElementTree.ElementTree(root).write(stream, encoding="utf-8", xml_declaration=True)


def merge(roots):
    assert len(roots) > 0
    base_root = roots.pop(0)
    xpath = "testcase[@classname='%s']"

    def change_attribute_by(suite, attribute, value):
        suite.set(attribute, str(int(suite.get(attribute)) + value))

    def delete_testcase(suite, testcase):
        if len(testcase):
            result = list(testcase)[0]
            if result.tag == "failure":
                change_attribute_by(suite, 'failures', -1)
            elif result.tag == "error":
                change_attribute_by(suite, 'errors', -1)
            elif result.tag == "skipped":
                change_attribute_by(suite, 'skip', -1)
        change_attribute_by(suite, 'tests', -1)
        suite.remove(testcase)

    def add_testcase(suite, testcase):
        if len(testcase):
            result = list(testcase)[0]
            if result.tag == "failure":
                change_attribute_by(suite, 'failures', 1)
            elif result.tag == "error":
                change_attribute_by(suite, 'errors', 1)
            elif result.tag == "skipped":
                change_attribute_by(suite, 'skip', 1)
        change_attribute_by(suite, 'tests', 1)
        suite.append(testcase)

    for suite in roots:
        for testcase in suite:
            candidates = base_root.findall(xpath % testcase.get('classname'))
            matching_testcase = next(t for t in candidates if t.get('name') == testcase.get('name'))
            if matching_testcase is not None:
                delete_testcase(base_root, matching_testcase)

            add_testcase(base_root, testcase)

    return base_root


def main():
    args = parser.parse_args()
    reports = args.input
    output = args.output

    roots = [ElementTree.parse(r).getroot() for r in reports]
    root = merge(roots)
    write_output(root, output)


if __name__ == "__main__":
    main()
