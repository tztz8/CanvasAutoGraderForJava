import sys

from junitxmlparser import get_results


def do_we_continue():
    ans = input("Countue?")
    ans = ans.lower()
    if ans == 'no' or ans == 'n':
        sys.exit("No Countue")


def step_get_labs(gitHubOauthToken, gitHubUser, gitHubStartRepo, setupDir, class_csv):
    print("not setup")
    # download all labs
    # TODO: get labs


def step_setup_labs(setupDir):
    print("not setup")
    # remove any un-use things
    # TODO: setup labs


def step_setup_tests(setupDir, sourceTests):
    print("not setup")
    # copy tests into each lab
    # TODO: copy tests in to labs


def step_run_tests(setupDir):
    print("not setup")
    # TODO: run JUnit
    # TODO: run CheckStyle


def step_read_tests(setupDir):
    print("not setup")
    # TODO: read JUnit tests
    results = dict()
    results['test'] = get_results('TEST-junit-jupiter.xml')
    results['tztz8'] = 2.7
    # TODO: read CheckStyle

    for result in results:
        print(result, ":", results[result])

    return results


def step_upload_grades(grades, API_KEY, API_URL, COURSE_ID, assignment_ID, class_csv):
    print("not setup")
    # TODO: upload grades


if __name__ == '__main__':
    print('Start Auto Grader')
    gitHubOauthToken = input("GitHub OAuth Token: ")
    gitHubUser = input("GitHub UserName (GitHub class Organization User Name): ")
    gitHubStartRepo = input("GitHub Starting Repo (Ex EWU-CSCD999/cscd999-n99-lab9999): ")
    setupDir = input("Setup dir (Ex /home/graderUserName/TAcscd999/grading/lab9999): ")
    sourceTests = input("Source Tests (Ex /home/graderUserName/TAcscd999/setup/lab999-sol/tests): ")
    API_KEY = input("Canvas API KEY: ")
    API_URL = input("Canvas URL: ")
    COURSE_ID = input("Canvas course ID: ")
    assignment_ID = input("Canvas assignment ID: ")
    class_csv = input("Class Github To Canvas User ID csv file: ")
    print('Getting Student Labs')
    step_get_labs(gitHubOauthToken, gitHubUser, gitHubStartRepo, setupDir, class_csv)
    do_we_continue()
    print('Setup Labs')
    step_setup_labs(setupDir)
    do_we_continue()
    print('Setup Tests')
    step_setup_tests(setupDir, sourceTests)
    do_we_continue()
    print('Running Grader')
    step_run_tests(setupDir)
    do_we_continue()
    print('Read Grades')
    setupDir = "no"
    grades = step_read_tests(setupDir)
    do_we_continue()
    print('Uploading Grades')
    # step_upload_grades(grades, API_KEY, API_URL, COURSE_ID, assignment_ID, class_csv)
    print('Done')
