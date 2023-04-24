import os.path
import xml.etree.ElementTree as ET


def get_results(file_name):
    if not os.path.exists(file_name):
        return 0

    tree = ET.parse(file_name)
    root = tree.getroot()

    # print("root.tag: ", root.tag, ", root.attrib", root.attrib)
    # print("Num of Tests: ", root.attrib['tests'], ", Failures: ", root.attrib['failures'])
    assert (root.tag == 'testsuite')
    # assert (root.attrib['skipped'] == '0')

    tests = int(root.attrib['tests'])
    failures = int(root.attrib['failures']) + int(root.attrib['errors'])

    return ((tests - failures) / tests) * 100


def get_mut_tests_results(num, pre_file, after_file):
    tests = 0
    failures = 0
    for i in range(1, num + 1):
        file_name = pre_file + str(i) + after_file
        if not os.path.exists(file_name):
            continue

        tree = ET.parse(file_name)
        root = tree.getroot()

        # print("root.tag: ", root.tag, ", root.attrib", root.attrib)
        # print("Num of Tests: ", root.attrib['tests'], ", Failures: ", root.attrib['failures'])
        assert (root.tag == 'testsuite')
        # assert (root.attrib['skipped'] == '0')

        tests += int(root.attrib['tests'])
        failures += int(root.attrib['failures']) + int(root.attrib['errors'])

    return ((tests - failures) / tests) * 100


if __name__ == '__main__':
    results = get_results('TEST-junit-jupiter.xml')
    print(results, type(results))
