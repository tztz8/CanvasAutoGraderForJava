import sys
import tkinter.filedialog
import tkinter.simpledialog
from pathlib import Path

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


def step_read_tests(setup_dir):
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
    print('Getting Student Labs')
    gitHubUser = tkinter.simpledialog.askstring(
        title="GitHub OAuth User", prompt="Enter GitHub UserName:", initialvalue="EWU-CSCD212")
    gitHubOauthToken = tkinter.simpledialog.askstring(
        title="GitHub OAuth Token", prompt="Enter OAuth Token:", show='*')
    gitHubStartRepo = tkinter.simpledialog.askstring(
        title="GitHub Staring Repo", prompt="Enter GitHub Repo:", initialvalue="EWU-CSCD212/cscd212-s23-lab#")
    setupDir = tkinter.filedialog.askdirectory(title="Setup Dir", initialdir=Path.home().as_posix())
    class_csv = tkinter.filedialog.askopenfile(
        mode='r', title="Class CSV File", initialdir="../../EWU/CSCD212/Grading",
        filetypes=(("CSV files", "*.csv"), ("all files", "*")))
    step_get_labs(gitHubOauthToken, gitHubUser, gitHubStartRepo, setupDir, class_csv)
    do_we_continue()
    print('Setup Labs')
    step_setup_labs(setupDir)
    do_we_continue()
    print('Setup Tests')
    sourceTests = tkinter.filedialog.askdirectory(title="Tests Dir", initialdir=Path.home().as_posix())
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
    API_KEY = tkinter.simpledialog.askstring(
        title="Canvas OAuth Token", prompt="Enter OAuth Token:", show='*')
    API_URL = tkinter.simpledialog.askstring(
        title="Canvas URL", prompt="Enter Canvas URL:", initialvalue="https://canvas.ewu.edu/")
    COURSE_ID = tkinter.simpledialog.askinteger(
        title="Canvas Course ID", prompt="Enter Canvas Course ID:", initialvalue=1652821)
    assignment_ID = tkinter.simpledialog.askinteger(
        title="Canvas assignment ID", prompt="Enter Canvas assignment ID:")
    step_upload_grades(grades, API_KEY, API_URL, COURSE_ID, assignment_ID, class_csv)
    print('Done')
