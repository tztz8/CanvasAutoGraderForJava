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


def get_messages_with_note(tree, student, commit_message):
    found_some_thing = False
    for test in tree.findall("testcase"):
        for fail in test.findall("failure"):
            if not found_some_thing:
                found_some_thing = True
                if student is not None:
                    student.message.append("Tests For " + commit_message)
                else:
                    print("Tests For " + commit_message)
            message = "Test: "
            message += test.get("name")
            message += ", \t Fail: "
            message += fail.get("message")
            if student is not None:
                student.message.append(message)
            else:
                print(message)
        for err in test.findall("error"):
            if not found_some_thing:
                found_some_thing = True
                if student is not None:
                    student.message.append("Tests For " + commit_message)
                else:
                    print("Tests For " + commit_message)
            message = "Test: "
            message += test.get("name")
            message += ", \t Error: "
            if (err.get("message") is None):
                message += "Unable to read Error Message"
            else:
                message += err.get("message")
            if student is not None:
                student.message.append(message)
            else:
                print(message)


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
            if (err.get("message") is None):
                message += "Unable to read Error Message"
            else:
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
    elif tests > num_of_tests:
        print("Warring To many tests")
    return ((num_of_tests - failures) / num_of_tests) * 100


# TODO: expanded for TDD
def get_tdd_tests_results(file_name, commit_message, is_unit, is_ta, set_pass_tests, student):
    if not os.path.exists(file_name):
        score = 0
        return set_pass_tests, score
    tree = ET.parse(file_name)
    root = tree.getroot()

    if (not is_unit) and is_ta:
        get_messages_with_note(tree, student, commit_message)

    assert (root.tag == 'testsuite')

    tests = int(root.attrib['tests'])
    failures = int(root.attrib['failures']) + int(root.attrib['errors'])

    failures_read = 0
    all_failures_read = 0

    for test in tree.findall("testcase"):
        test_pass = True
        for fail in test.findall("failure"):
            test_pass = False
        for err in test.findall("error"):
            test_pass = False
        test_name = test.get("classname") + "." + test.get("name")
        # Have we encountered this test (pass feature) and now fail when need to pass
        if (test_name in set_pass_tests) and (not test_pass):
            failures_read += 1
        # Fail and is unit test
        elif (not test_pass) and (not is_unit):
            failures_read += 1

        if not test_pass:
            all_failures_read += 1
        set_pass_tests.add(test_name)

    assert (all_failures_read == failures)

    score = 0

    if tests == 0:
        return set_pass_tests, score

    if is_unit and all_failures_read > 1:
        score = ((tests - failures_read) / tests) * 90
        # Is Unit and has fail tests
        score += 10
    elif is_unit:
        score = ((tests - failures_read) / tests) * 90
        # Is unit and has no fail tests (missing 10 points)
        # NO ADD 10
    else:
        score = ((tests - failures_read) / tests) * 100

    return set_pass_tests, score


if __name__ == '__main__':
    results = get_results('TEST-junit-jupiter.xml')
    print(results, type(results))
    results = get_results(
        '/home/tztz8/dev/IdeaProjects/EWU/CSCD212S23/grading/lab7_testing/forks/SandhuAaftab/build/test-results/test1/TEST-junit-jupiter.xml')
    print(results, type(results))
