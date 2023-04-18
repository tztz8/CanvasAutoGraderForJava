import csv
import os
import shutil
import subprocess
import sys
import tkinter.filedialog
import tkinter.simpledialog
import tkinter.messagebox
import secret
from canvastools import CanvasTools
from github import Github

from checkstyletools import get_checkstyle_results
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
                already_exists = False
                if not os.path.exists(clone_to):
                    # not there
                    command = ["git", "clone", "--progress", url, clone_to]
                    # run command
                    subprocess.run(command, stdout=outfile)  # FIXME: no output
                else:
                    already_exists = True
                    os.system("cd " + clone_to + " && git restore . && git clean -f && git pull")

                # TODO: get_collaborators() only Teacher check (add to dict for grading)

                # Done with getting a lab
                dict_of_students[github_user_name] = ["Unknown", "4364626", github_user_name, clone_to]
                print("User: ", github_user_name, ", already exists: ", already_exists, ", clone to: ", clone_to)
                num_of_forks += 1
            num_of_fork_pages += 1
            forks = forks_pages.get_page(num_of_fork_pages)  # GitHub API will only give page of forks at a time
            assert num_of_forks <= start_repo.forks
    num_of_students = 0
    with open(class_csv, 'r') as class_csv_file:
        csv_reader = csv.reader(class_csv_file, delimiter=',')
        for row in csv_reader:
            if num_of_students != 0 and row[3] in dict_of_students.keys():
                dict_of_students[row[3]][0] = row[0]
                dict_of_students[row[3]][1] = row[1]
            elif num_of_students != 0:
                print("Missing Student: ", row)
            num_of_students += 1
    # Done with getting the labs
    print("Number of Labs: ", num_of_forks,
          ", Number of Forks: ", start_repo.forks,
          ", Number of Fork Pages: ", num_of_fork_pages,
          ", Number of students: ", num_of_students)
    return dict_of_students


def step_setup_labs(setup_dir, students):
    # [ name for name in os.listdir(setup_dir) if os.path.isdir(os.path.join(setup_dir, name)) ]
    for student in students:
        student_dir = setup_dir + "/forks/" + student
        if os.path.exists(student_dir + "/out"):
            shutil.rmtree(student_dir + "/out")  # If student modify/ignore the .gitignore file
        if os.path.exists(student_dir + "/.idea"):
            shutil.rmtree(student_dir + "/.idea", ignore_errors=True)  # If I need to grade make it better

        if os.path.exists(student_dir + "/tests"):
            shutil.rmtree(student_dir + "/docs")  # stop finding files in here that not needed
        else:
            print(student, " is missing docs folder")

        if os.path.exists(student_dir + "/tests"):
            shutil.rmtree(student_dir + "/tests")  # remove old tests (also the student may modify the tests)
        else:
            print(student, " is missing tests folder")

        if os.path.exists(student_dir + "/*.iml"):
            os.remove(student_dir + "/*.iml")  # If I need to grade make it better

        if os.path.exists(student_dir + "/src"):
            print(student, " Setup Done")
        else:
            print(student, " Missing src folder")


def step_setup_tests(setup_dir, source_tests, students):
    # make tool dir, change into tool dir, download file
    os.system("mkdir -p " + setup_dir + "/tools && cd " + setup_dir + "/tools && wget "
              + "https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.9.2/junit-platform-console-standalone-1.9.2.jar")
    # make tool dir, change into tool dir, download file
    os.system("mkdir -p " + setup_dir + "/tools && cd " + setup_dir + "/tools && wget "
              + "https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.9.3/checkstyle-10.9.3-all.jar")
    if os.path.isdir(source_tests):
        # copy tests into each lab
        for student in students:
            student_dir = setup_dir + "/forks/" + student + "/tests"
            shutil.copytree(source_tests, student_dir)
            print(student, " Setup Done")

    else:
        # copy test jar to tools
        shutil.copy(source_tests, setup_dir + "/tools")
        print("Copy Jar into tools done")


def step_run_tests(setup_dir, jar, junit_to_run, students):
    with open(f"{setup_dir}/testoutput.txt", "w") as output:
        for student in students:
            student_dir = setup_dir + "/forks/" + student
            output.write(student)
            output.write("\n")
            output.write(student_dir)
            output.write("\n")
            # Compile students code
            stream = os.popen("cd " + student_dir + " && " +
                              "javac -Xlint:unchecked -cp " +
                              setup_dir + "/tools/junit-platform-console-standalone-1.9.2.jar -cp " +
                              setup_dir + "/tools/tests.jar -d out/classes $(find src -name '*.java')")
            output.write(stream.read())
            # Run JUnit Tests
            stream = os.popen("cd " + student_dir + " && " +
                              "java -jar " +
                              setup_dir + "/tools/junit-platform-console-standalone-1.9.2.jar " +
                              "--reports-dir=build/test-results/test1 -cp " +
                              jar + " -cp out/classes --select-class=" + junit_to_run)
            output.write(stream.read())
            # Run CheckStyle Tests
            stream = os.popen("cd " + student_dir + " && " +
                              "java -jar " +
                              setup_dir + "/tools/checkstyle-10.9.3-all.jar " +
                              "-c=https://github.com/tztz8/HelloGradle/raw/master/ewu-cscd212-error.xml " +
                              "-o=checkstyleoutfile $(find src -name '*.java')")
            output.write(stream.read())
            print(student)
    # javac -Xlint:unchecked -cp junit-platform-console-standalone-1.9.2.jar -cp tools/${{ env.Junit_Test_Jar_File }} -d out/classes $(find src -name '*.java')
    # java -jar junit-platform-console-standalone-1.9.2.jar --reports-dir=build/test-results/test1 -cp tools/${{ env.Junit_Test_Jar_File }} -cp out/classes --select-class=${{ env.Junit_Class_To_run }}
    # java -jar checkstyle-10.9.3-all.jar -c=https://github.com/tztz8/HelloGradle/raw/master/ewu-cscd212-error.xml -o=checkstyleoutfile $(find src -name '*.java')


def step_read_tests(setup_dir, students):
    with open(setup_dir + '/grades.csv', 'w') as csvfile:
        grad_writer = csv.writer(csvfile)
        grad_writer.writerow(["name", "canvas_id", "github_user_name", "clone_to", "score"])
        for student in students:
            student_dir = setup_dir + "/forks/" + student
            junit_weight = 98/100
            junit_result = get_results(student_dir + '/build/test-results/test1/TEST-junit-jupiter.xml')
            checkstyle_weight = 2/100
            checkstyle_result = get_checkstyle_results(student_dir + '/checkstyleoutfile')
            assert (junit_weight + checkstyle_weight) == 1
            result = (junit_weight * junit_result) + (checkstyle_weight * checkstyle_result)
            students[student].append(result)
            print(students[student])
            grad_writer.writerow(students[student])


def step_upload_grades(grades, api_key, api_url, course_id, assignment_id,):
    print("not setup")
    # TODO: upload grades
    tool = CanvasTools(api_key, api_url, course_id, assignment_id)
    for student in grades:
        print("Uploading Grade for ", grades[student][0])
        tool.update_grade(grades[student][1], grades[student][4])
    # tool.update_grade()
    # for grade in grades:


if __name__ == '__main__':
    print('Start Auto Grader')
    response = True
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
        filetypes=(("CSV files", "*.csv"), ("all files", "*"))).name
    # Print args for step
    print("gitHubOauthToken: ", gitHubOauthToken,
          ", gitHubStartRepo: ", gitHubStartRepo,
          ", setupDir: ", setupDir,
          ", class_csv: ", class_csv)
    # Check if run step with user
    # response = tkinter.messagebox.askokcancel("askokcancel", "Want to run get labs step?")
    students = dict()
    if response:
        students = step_get_labs(gitHubOauthToken, gitHubStartRepo, setupDir, class_csv)
    else:
        print("Skip")

    do_we_continue()
    print('Setup Labs')
    # Print args for step
    print("setupDir: ", setupDir, ", students: ", students)
    # response = tkinter.messagebox.askokcancel("askokcancel", "Want to run setup labs step?")
    if response:
        step_setup_labs(setupDir, students)
    else:
        print("Skip")

    do_we_continue()
    print('Setup Tests')
    # Get needed args from user
    sourceTests = tkinter.filedialog.askopenfile(
        title="Tests", initialdir="../../../IdeaProjects/EWU/CSCD212S23/setup",
        filetypes=(("Java Jar files", "*.jar"), ("all files", "*"))
    ).name
    # Print args for step
    print("setupDir: ", setupDir, ", sourceTests: ", sourceTests, ", students: ", students)
    # Check if run step with user
    # response = tkinter.messagebox.askokcancel("askokcancel", "Want to run setup tests step?")
    if response:
        step_setup_tests(setupDir, sourceTests, students)
    else:
        print("Skip")

    do_we_continue()
    print('Running Grader')
    junit_to_run = tkinter.simpledialog.askstring(
        title="JUnit Class to run",
        prompt="Class To Run",
        initialvalue="cscd211tests.lab3.CSCD212Lab3Test"
    )
    # Print args for step
    print("setupDir: ", setupDir, ", junit_to_run: ", junit_to_run, ", students: ", students)
    # Check if run step with user
    # response = tkinter.messagebox.askokcancel("askokcancel", "Want to run grading step?")
    if response:
        step_run_tests(setupDir, sourceTests, junit_to_run, students)
    else:
        print("Skip")

    do_we_continue()
    print('Read Grades')
    # Print args for step
    print("setupDir: ", setupDir)
    # Check if run step with user
    # response = tkinter.messagebox.askokcancel("askokcancel", "Want to run read grades step?")
    if response:
        step_read_tests(setupDir, students)
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
    print("students: ", students,
          ", API_KEY: ", API_KEY,
          ", API_URL: ", API_URL,
          ", COURSE_ID: ", COURSE_ID,
          ", assignment_ID: ", assignment_ID)
    # Check if run step with user
    response = tkinter.messagebox.askokcancel("askokcancel", "Want to run post grades step?")
    if response:
        step_upload_grades(students, API_KEY, API_URL, COURSE_ID, assignment_ID)
    else:
        print("Skip")
    print('Done')
