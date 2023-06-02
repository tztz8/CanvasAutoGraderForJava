import os.path
import xml.etree.ElementTree as ET

import currentLab


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

    get_messages(tree, None)

    return ((tests - failures) / tests) * 100


def get_messages(tree, student):
    for test in tree.findall("testcase"):
        for fail in test.findall("failure"):
            message = "Test: "
            message += test.get("name")
            message += ", \t Fail: "
            message += fail.get("message")
            if student is not None:
                student.message.append(message)
            else:
                print(message)
        for err in test.findall("error"):
            message = "Test: "
            message += test.get("name")
            message += ", \t Error: "
            message += err.get("message")
            if student is not None:
                student.message.append(message)
            else:
                print(message)


def get_mut_tests_results(num, pre_file, after_file, student):
    num_of_tests = currentLab.NUM_OF_JUNIT_TESTS
    tests = 0
    failures = 0
    for i in range(1, num + 1):
        file_name = pre_file + str(i) + after_file
        if not os.path.exists(file_name):
            continue  # TODO: get missing tests

        tree = ET.parse(file_name)
        root = tree.getroot()

        get_messages(tree, student)

        # print("root.tag: ", root.tag, ", root.attrib", root.attrib)
        # print("Num of Tests: ", root.attrib['tests'], ", Failures: ", root.attrib['failures'])
        assert (root.tag == 'testsuite')
        # assert (root.attrib['skipped'] == '0')

        tests += int(root.attrib['tests'])
        failures += int(root.attrib['failures']) + int(root.attrib['errors'])
    if tests < num_of_tests:
        print("Warring Missing some tests")
        failures += (num_of_tests - tests)
    elif tests < num_of_tests:
        print("Warring To many tests")
    return ((num_of_tests - failures) / num_of_tests) * 100


if __name__ == '__main__':
    results = get_results('TEST-junit-jupiter.xml')
    print(results, type(results))
    results = get_results(
        '/home/tztz8/dev/IdeaProjects/EWU/CSCD212S23/grading/lab7_testing/forks/SandhuAaftab/build/test-results/test1/TEST-junit-jupiter.xml')
    print(results, type(results))
