import subprocess
import sys
import tkinter.filedialog
import tkinter.simpledialog
import tkinter.messagebox
import secret
from canvastools import CanvasTools
from github import Github
from junitxmlparser import get_results


def do_we_continue():
    ans = input("Countue?")
    ans = ans.lower()
    if ans == 'no' or ans == 'n':
        sys.exit("No Countue")


def step_get_labs(git_hub_oauth_token, git_hub_start_repo, setup_dir, class_csv):
    # Setup GitHub API
    github_tool = Github(git_hub_oauth_token)
    start_repo = github_tool.get_repo(git_hub_start_repo)
    forks_pages = start_repo.get_forks()
    # Setup loop
    dict_of_students = dict()
    num_of_forks = 0
    num_of_fork_pages = 0
    forks = forks_pages.get_page(0)
    with open(f"{setup_dir}/gitoutput.txt", "w") as outfile:  # debug output file
        while len(forks) > 0:  # GitHub API will only give page of forks at a time
            for fork in forks:  # Each fork
                # Check if in class (Use for when start repo is not just this class)
                github_user_name = fork.owner.login
                # TODO: check if user in class_csv
                # github_user_name class_csv

                # Clone the fork (student repo)
                url = fork.ssh_url
                clone_to = setup_dir + "/forks/" + github_user_name
                command = ["git", "clone", "--progress", url, clone_to]
                # run command
                subprocess.run(command, stdout=outfile)

                # TODO: get_collaborators() only Teacher check (add to dict for grading)

                # Done with getting a lab
                dict_of_students[github_user_name] = (github_user_name, clone_to)
                print("User: ", github_user_name, ", clone to: ", clone_to)
                num_of_forks += 1
            num_of_fork_pages += 1
            forks = forks_pages.get_page(num_of_fork_pages)  # GitHub API will only give page of forks at a time
            assert num_of_forks <= start_repo.forks
    # Done with getting the labs
    print("Number of Labs: ", num_of_forks,
          ", Number of Forks: ", start_repo.forks,
          ", Number of Fork Pages: ", num_of_fork_pages,
          ", Number of students: TODO add")
    return dict_of_students


def step_setup_labs(setup_dir):
    print("not setup")
    # remove any un-use things
    # TODO: setup labs


def step_setup_tests(setup_dir, source_tests):
    print("not setup")
    # wget https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.9.2/junit-platform-console-standalone-1.9.2.jar
    # https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.9.3/checkstyle-10.9.3-all.jar
    # copy tests into each lab
    # TODO: copy tests in to labs


def step_run_tests(setup_dir):
    print("not setup")
    # TODO: run JUnit
    # javac -Xlint:unchecked -cp junit-platform-console-standalone-1.9.2.jar -cp tools/${{ env.Junit_Test_Jar_File }} -d out/classes $(find src -name '*.java')
    # java -jar junit-platform-console-standalone-1.9.2.jar --reports-dir=build/test-results/test1 -cp tools/${{ env.Junit_Test_Jar_File }} -cp out/classes --select-class=${{ env.Junit_Class_To_run }}
    # subprocess.run(command, stdout=outfile)
    # TODO: run CheckStyle
    # java -jar checkstyle-10.9.3-all.jar -c=https://github.com/tztz8/HelloGradle/raw/master/ewu-cscd212-error.xml -o=checkstyleoutfile $(find src -name '*.java')
    # subprocess.run(command, stdout=outfile)


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


def step_upload_grades(grades, api_key, api_url, course_id, assignment_id, class_csv):
    print("not setup")
    # TODO: upload grades
    tool = CanvasTools(api_key, api_url, course_id, assignment_id)
    # tool.update_grade()
    # for grade in grades:


if __name__ == '__main__':
    print('Start Auto Grader')
    print('Getting Student Labs')
    # Get needed args from user
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
        initialdir="../../../IdeaProjects/EWU/CSCD212S23/grading"  # Path.home().as_posix()
    )
    class_csv = tkinter.filedialog.askopenfile(
        mode='r', title="Class CSV File", initialdir="../../../IdeaProjects/EWU/CSCD212S23",
        filetypes=(("CSV files", "*.csv"), ("all files", "*")))
    # Print args for step
    print("gitHubOauthToken: ", gitHubOauthToken,
          ", gitHubStartRepo: ", gitHubStartRepo,
          ", setupDir: ", setupDir,
          ", class_csv: ", class_csv)
    # Check if run step with user
    response = tkinter.messagebox.askokcancel("askokcancel", "Want to run get labs step?")
    if response:
        step_get_labs(gitHubOauthToken, gitHubStartRepo, setupDir, class_csv)
    else:
        print("Skip")


    do_we_continue()
    print('Setup Labs')
    # Print args for step
    print("setupDir: ", setupDir)
    response = tkinter.messagebox.askokcancel("askokcancel", "Want to run setup labs step?")
    if response:
        step_setup_labs(setupDir)
    else:
        print("Skip")


    do_we_continue()
    print('Setup Tests')
    # Get needed args from user
    sourceTests = tkinter.filedialog.askdirectory(
        title="Tests Dir", initialdir="../../../IdeaProjects/EWU/CSCD212S23/setup")
    # Print args for step
    print("setupDir: ", setupDir, ", sourceTests: ", sourceTests)
    # Check if run step with user
    response = tkinter.messagebox.askokcancel("askokcancel", "Want to run setup tests step?")
    if response:
        step_setup_tests(setupDir, sourceTests)
    else:
        print("Skip")


    do_we_continue()
    print('Running Grader')
    # Print args for step
    print("setupDir: ", setupDir)
    # Check if run step with user
    response = tkinter.messagebox.askokcancel("askokcancel", "Want to run grading step?")
    if response:
        step_run_tests(setupDir)
    else:
        print("Skip")


    do_we_continue()
    print('Read Grades')
    # Print args for step
    print("setupDir: ", setupDir)
    # Check if run step with user
    response = tkinter.messagebox.askokcancel("askokcancel", "Want to run read grades step?")
    grades = []
    if response:
        grades = step_read_tests(setupDir)
    else:
        print("Skip")



    do_we_continue()
    print('Uploading Grades')
    # Get needed args from user
    API_KEY = tkinter.simpledialog.askstring(
        title="Canvas OAuth Token", prompt="Enter OAuth Token:", show='*', initialvalue=secret.API_KEY)
    API_URL = tkinter.simpledialog.askstring(
        title="Canvas URL", prompt="Enter Canvas URL:", initialvalue=secret.API_URL)
    COURSE_ID = tkinter.simpledialog.askinteger(
        title="Canvas Course ID", prompt="Enter Canvas Course ID:", initialvalue=secret.COURSE_ID)
    assignment_ID = tkinter.simpledialog.askinteger(
        title="Canvas assignment ID", prompt="Enter Canvas assignment ID:")
    # Print args for step
    print("grades: ", grades,
          ", API_KEY: ", API_KEY,
          ", API_URL: ", API_URL,
          ", COURSE_ID: ", COURSE_ID,
          ", assignment_ID: ", assignment_ID,
          ", class_csv: ", class_csv)
    # Check if run step with user
    response = tkinter.messagebox.askokcancel("askokcancel", "Want to run post grades step?")
    if response:
        step_upload_grades(grades, API_KEY, API_URL, COURSE_ID, assignment_ID, class_csv)
    else:
        print("Skip")
    print('Done')
