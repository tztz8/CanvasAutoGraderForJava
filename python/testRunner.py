import csv
import os
import shutil
import subprocess
import tkinter.filedialog
import tkinter.simpledialog
import tkinter.messagebox
import warnings

from github import Github
from canvastools import CanvasTools

import checkstyletools
import junitxmlparser
import secret


#  TODO: add docs
class TestRunner:
    def __init__(self):
        print("Maker Tester")
        self.gitHub_oauthToken = secret.GITHUB_OAUTH_TOKEN
        self.gitHub_start_repo = "EWU-CSCD212/cscd212-s23-lab#"

        self.github_tool = None
        self.start_repo = None

        self.setup_dir = "../../../IdeaProjects/EWU/CSCD212S23/grading"

        self.class_csv = "../../../IdeaProjects/EWU/CSCD212S23"
        self.students = dict()

        self.source_test_jar = "../../../IdeaProjects/EWU/CSCD212S23/setup"
        self.junit_to_run_list = []
        self.num_of_junit_tests = 0

        self.canvas_api_key = secret.API_KEY
        self.canvas_api_url = secret.API_URL
        self.canvas_course_id = secret.COURSE_ID
        self.canvas_assignment_id = None
        self.canvas_tools = None

    def _check_canvas_tools(self):
        if self.canvas_assignment_id is None:
            raise RuntimeError("Missing Assignment ID")
        if self.canvas_tools is None:
            self.canvas_tools = CanvasTools(
                self.canvas_api_key, self.canvas_api_url, self.canvas_course_id, self.canvas_assignment_id)

    def gui_set_things(self):
        self.gitHub_oauthToken = tkinter.simpledialog.askstring(
            title="GitHub OAuth Token", prompt="Enter OAuth Token:", show='*',
            initialvalue=secret.GITHUB_OAUTH_TOKEN
        )
        self.gitHub_start_repo = tkinter.simpledialog.askstring(
            title="GitHub Staring Repo", prompt="Enter GitHub Repo:",
            initialvalue=self.gitHub_start_repo
        )
        self.setup_dir = tkinter.filedialog.askdirectory(
            title="Setup Dir",
            initialdir=self.setup_dir
        )
        self.class_csv = tkinter.filedialog.askopenfile(
            mode='r', title="Class CSV File", initialdir=self.class_csv,
            filetypes=(("CSV files", "*.csv"), ("all files", "*"))).name
        self.source_test_jar = tkinter.filedialog.askopenfile(
            title="Tests", initialdir="../../../IdeaProjects/EWU/CSCD212S23/setup",
            filetypes=(("Java Jar files", "*.jar"), ("all files", "*"))
        ).name
        response = True
        while response:
            junit_to_run = tkinter.simpledialog.askstring(
                title="JUnit Class to run",
                prompt="Class To Run",
                initialvalue="cscd211tests.lab3.CSCD212Lab3Test"
            )
            self.junit_to_run_list.append(junit_to_run)
            response = tkinter.messagebox.askokcancel("Add more", "Want to add more tests?")
        self.num_of_junit_tests = len(self.junit_to_run_list)
        self.canvas_api_key = tkinter.simpledialog.askstring(
            title="Canvas OAuth Token", prompt="Enter OAuth Token:", show='*', initialvalue=secret.API_KEY)
        self.canvas_api_url = tkinter.simpledialog.askstring(
            title="Canvas URL", prompt="Enter Canvas URL:", initialvalue=secret.API_URL)
        self.canvas_course_id = tkinter.simpledialog.askinteger(
            title="Canvas Course ID", prompt="Enter Canvas Course ID:", initialvalue=secret.COURSE_ID)
        self.canvas_assignment_id = tkinter.simpledialog.askinteger(
            title="Canvas assignment ID", prompt="Enter Canvas assignment ID:")

    def step_upload_grades(self):
        self._check_canvas_tools()
        for student in self.students:
            print("Uploading Grade for ", self.students[student][0])
            self.canvas_tools.update_grade(self.students[student][1],
                                           self.students[student][len(self.students[student]) - 1])

    def step_read_tests(self):
        with open(self.setup_dir + '/grades.csv', 'w') as csvfile:
            grad_writer = csv.writer(csvfile)
            grad_writer.writerow(
                ["name", "canvas_id", "github_user_name", "clone_to", "junit_result", "checkstyle_result", "score"])
            for student in self.students:
                student_dir = self.setup_dir + "/forks/" + student
                junit_weight = 98 / 100
                junit_result = junitxmlparser.get_mut_tests_results(
                    self.num_of_junit_tests, student_dir + '/build/test-results/test', '/TEST-junit-jupiter.xml')
                self.students[student].append(junit_result)
                checkstyle_weight = 2 / 100
                checkstyle_result = checkstyletools.get_checkstyle_results(student_dir + '/checkstyleoutfile')
                self.students[student].append(junit_result)
                assert (junit_weight + checkstyle_weight) == 1
                result = (junit_weight * junit_result) + (checkstyle_weight * checkstyle_result)
                self.students[student].append(result)
                print(self.students[student])
                grad_writer.writerow(self.students[student])

    def step_run_tests(self):
        for student in self.students:
            with open(f"{self.setup_dir}/forks/{student}/testoutput.txt", "w") as output:
                student_dir = self.setup_dir + "/forks/" + student
                output.write(student)
                output.write("\n")
                output.write(student_dir)
                output.write("\n")
                # Compile students code
                stream = os.popen("cd " + student_dir + " && " +
                                  "javac -Xlint:unchecked -cp " +
                                  self.setup_dir + "/tools/junit-platform-console-standalone-1.9.2.jar -cp " +
                                  self.source_test_jar + " -d out/classes $(find src -name '*.java')")
                output.write(stream.read())
                # Run JUnit Tests
                index = 0
                for junit_to_run in self.junit_to_run_list:
                    index += 1
                    stream = os.popen("cd " + student_dir + " && " +
                                      "java -jar " +
                                      self.setup_dir + "/tools/junit-platform-console-standalone-1.9.2.jar " +
                                      "--reports-dir=build/test-results/test" + str(index) + " -cp " +
                                      self.source_test_jar + " -cp out/classes --select-class=" + junit_to_run)
                    output.write(stream.read())
                # Run CheckStyle Tests
                stream = os.popen("cd " + student_dir + " && " +
                                  "java -jar " +
                                  self.setup_dir + "/tools/checkstyle-10.9.3-all.jar " +
                                  "-c=https://github.com/tztz8/HelloGradle/raw/master/ewu-cscd212-error.xml " +
                                  "-o=checkstyleoutfile $(find src -name '*.java')")
                output.write(stream.read())
                print(student)

    def step_setup_tests(self):
        # make tool dir, change into tool dir, download file
        os.system("mkdir -p " + self.setup_dir + "/tools && cd " + self.setup_dir + "/tools && wget "
                  + "https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.9.2/junit-platform-console-standalone-1.9.2.jar")
        # make tool dir, change into tool dir, download file
        os.system("mkdir -p " + self.setup_dir + "/tools && cd " + self.setup_dir + "/tools && wget "
                  + "https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.9.3/checkstyle-10.9.3-all.jar")
        # copy test jar to tools
        shutil.copy(self.source_test_jar, self.setup_dir + "/tools")
        print("Copy Jar into tools done")


    def step_setup_labs(self):
        # [ name for name in os.listdir(setup_dir) if os.path.isdir(os.path.join(setup_dir, name)) ]
        for student in self.students:
            student_dir = self.setup_dir + "/forks/" + student
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
                warnings.warn(student, " Missing src folder")

    def step_get_labs(self):
        # Setup GitHub API
        self.github_tool = Github(self.gitHub_oauthToken)
        self.start_repo = self.github_tool.get_repo(self.gitHub_start_repo)
        forks_pages = self.start_repo.get_forks()
        # Setup loop
        num_of_forks = 0
        num_of_fork_pages = 0
        forks = forks_pages.get_page(0)
        with open(f"{self.setup_dir}/gitoutput.txt", "w") as outfile:  # debug output file
            while len(forks) > 0:  # GitHub API will only give page of forks at a time
                for fork in forks:  # Each fork
                    # Check if in class (Use for when start repo is not just this class)
                    github_user_name = fork.owner.login
                    # TODO: check if user in class_csv
                    # github_user_name class_csv

                    # Clone the fork (student repo)
                    url = fork.ssh_url
                    clone_to = self.setup_dir + "/forks/" + github_user_name
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
                    self.students[github_user_name] = ["Unknown", "4364626", github_user_name, clone_to]
                    print("User: ", github_user_name, ", already exists: ", already_exists, ", clone to: ", clone_to)
                    num_of_forks += 1
                num_of_fork_pages += 1
                forks = forks_pages.get_page(num_of_fork_pages)  # GitHub API will only give page of forks at a time
                assert num_of_forks <= self.start_repo.forks
        num_of_students = 0
        with open(self.class_csv, 'r') as class_csv_file:
            csv_reader = csv.reader(class_csv_file, delimiter=',')
            for row in csv_reader:
                if num_of_students != 0 and row[3] in self.students.keys():
                    self.students[row[3]][0] = row[0]
                    self.students[row[3]][1] = row[1]
                elif num_of_students != 0:
                    print("Missing Student Fork: ", row)

                if num_of_students != 0:
                    print("Hi")
                    # TODO: use src from submission from canvas if src missing in git repo

                num_of_students += 1
        # Done with getting the labs
        print("Number of Labs: ", num_of_forks,
              ", Number of Forks: ", self.start_repo.forks,
              ", Number of Fork Pages: ", num_of_fork_pages,
              ", Number of students: ", num_of_students)
        return self.students
