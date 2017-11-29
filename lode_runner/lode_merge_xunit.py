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

    def modify_suite(suite, testcase, value):
        if len(testcase):
            tags = [child.tag for child in list(testcase)]
            if "failure" in tags:
                change_attribute_by(suite, 'failures', value)
            elif "error" in tags:
                change_attribute_by(suite, 'errors', value)
            elif "skipped" in tags:
                change_attribute_by(suite, 'skip', value)
        change_attribute_by(suite, 'tests', value)

    for suite in roots:
        for testcase in suite:
            if "nose.plugins.multiprocess" in testcase.get("classname", ""):
                continue
            candidates = base_root.findall(xpath % testcase.get('classname'))
            matching_testcase = next(t for t in candidates if t.get('name') == testcase.get('name'))
            if matching_testcase is not None:
                modify_suite(base_root, matching_testcase, -1)
                base_root.remove(matching_testcase)

            modify_suite(base_root, testcase, 1)
            base_root.append(testcase)

    return base_root

get_roots = lambda reports: [ElementTree.parse(r).getroot() for r in reports]


def merge_reports(reports, output):
    roots = get_roots(reports)
    root = merge(roots)
    write_output(root, output)


def main():
    args = parser.parse_args()
    reports = args.input
    output = args.output

    merge_reports(reports, output)

if __name__ == "__main__":
    main()
