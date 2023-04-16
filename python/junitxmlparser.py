import xml.etree.ElementTree as ET


def get_results(file_name):
    tree = ET.parse(file_name)
    root = tree.getroot()

    # print("root.tag: ", root.tag, ", root.attrib", root.attrib)
    # print("Num of Tests: ", root.attrib['tests'], ", Failures: ", root.attrib['failures'])
    assert (root.tag == 'testsuite')
    assert (root.attrib['skipped'] == '0')
    assert (root.attrib['errors'] == '0')

    tests = int(root.attrib['tests'])
    failures = int(root.attrib['failures'])

    return ((tests - failures) / tests) * 100


if __name__ == '__main__':
    results = get_results('TEST-junit-jupiter.xml')
    print(results, type(results))
