import subprocess
import sys
import tkinter.filedialog
import tkinter.simpledialog
import secret
from pathlib import Path
from github import Github
from junitxmlparser import get_results


def do_we_continue():
    ans = input("Countue?")
    ans = ans.lower()
    if ans == 'no' or ans == 'n':
        sys.exit("No Countue")


def step_get_labs(gitHubOauthToken, gitHubStartRepo, setupDir, class_csv):
    # Setup GitHub API
    github_tool = Github(gitHubOauthToken)
    start_repo = github_tool.get_repo(gitHubStartRepo)
    forks_pages = start_repo.get_forks()
    # Setup loop
    num_of_forks = 0
    num_of_fork_pages = 0
    forks = forks_pages.get_page(0)
    with open(f"{setupDir}/gitoutput.txt", "w") as outfile:  # debug output file
        while len(forks) > 0:  # GitHub API will only give page of forks at a time
            for fork in forks:  # Each fork
                # Check if in class (Use for when start repo is not just this class)
                github_user_name = fork.owner.login
                # TODO: check if user in class_csv
                # github_user_name class_csv

                # Clone the fork (student repo)
                url = fork.ssh_url
                clone_to = setupDir + "/" + github_user_name
                command = ["git", "clone", "--progress", url, clone_to]
                # run command
                subprocess.run(command, stdout=outfile)

                # Done with getting a lab
                print("User: ", github_user_name, ", clone to: ", clone_to)
                num_of_forks += 1
            num_of_fork_pages += 1
            forks = forks_pages.get_page(num_of_fork_pages) # GitHub API will only give page of forks at a time
            assert num_of_forks <= start_repo.forks
    # Done with getting the labs
    print("Number of Labs: ", num_of_forks,
          ", Number of Forks: ", start_repo.forks,
          ", Number of Fork Pages: ", num_of_fork_pages,
          ", Number of students: TODO add")


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
    gitHubOauthToken = tkinter.simpledialog.askstring(
        title="GitHub OAuth Token", prompt="Enter OAuth Token:", show='*',
        initialvalue=secret.GITHUB_OAUTH_TOKEN
    )
    gitHubStartRepo = tkinter.simpledialog.askstring(
        title="GitHub Staring Repo", prompt="Enter GitHub Repo:",
        initialvalue="EWU-CSCD212/cscd212-s23-lab#"
    )
    setupDir = tkinter.filedialog.askdirectory(
        title="Setup Dir",
        initialdir=Path.home().as_posix()
    )
    # class_csv = tkinter.filedialog.askopenfile(
    #     mode='r', title="Class CSV File", initialdir="../../EWU/CSCD212/Grading",
    #     filetypes=(("CSV files", "*.csv"), ("all files", "*")))
    class_csv = None
    step_get_labs(gitHubOauthToken, gitHubStartRepo, setupDir, class_csv)
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
        title="Canvas OAuth Token", prompt="Enter OAuth Token:", show='*', initialvalue=secret.API_KEY)
    API_URL = tkinter.simpledialog.askstring(
        title="Canvas URL", prompt="Enter Canvas URL:", initialvalue=secret.API_URL)
    COURSE_ID = tkinter.simpledialog.askinteger(
        title="Canvas Course ID", prompt="Enter Canvas Course ID:", initialvalue=secret.COURSE_ID)
    assignment_ID = tkinter.simpledialog.askinteger(
        title="Canvas assignment ID", prompt="Enter Canvas assignment ID:")
    step_upload_grades(grades, API_KEY, API_URL, COURSE_ID, assignment_ID, class_csv)
    print('Done')
