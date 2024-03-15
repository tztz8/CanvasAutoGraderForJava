import csv
import os
import shutil
import subprocess
import sys
import tkinter.filedialog
import tkinter.simpledialog
import tkinter.messagebox
import warnings
import time

from github import Github

import currentLab
import grade_weight
from canvastools import CanvasTools

import checkstyletools
import junitxmlparser
import secret
from student_helper import student_object


#  TODO: add docs
class TestRunner:
    students: list[student_object]

    def __init__(self):
        print("Maker Tester")
        self.gitHub_oauthToken = secret.GITHUB_OAUTH_TOKEN
        # self.gitHub_start_repo = "EWU-CSCD212/cscd212-s23-lab#"
        self.gitHub_start_repo = currentLab.GIT_START_REPO

        self.github_tool = None
        self.start_repo = None

        # self.setup_dir = "../../../IdeaProjects/EWU/CSCD212S23/grading"
        self.setup_dir = currentLab.SETUP_DIR

        # self.class_csv = "../../../IdeaProjects/EWU/CSCD212S23"
        self.class_csv = currentLab.CLASS_CSV
        self.students = []
        # self.source_test_jar = "../../../IdeaProjects/EWU/CSCD212S23/setup"
        self.source_test_jar = currentLab.TEST_JAR
        # self.junit_to_run_list = []
        self.junit_to_run_list = currentLab.TEST_LIST
        # self.num_of_junit_tests = 0
        self.num_of_junit_tests = currentLab.NUM_OF_TESTS

        self.canvas_api_key = secret.API_KEY
        self.canvas_api_url = secret.API_URL
        self.canvas_course_id = secret.COURSE_ID
        # self.canvas_assignment_id = None
        self.canvas_assignment_id = currentLab.CANVAS_HW_ID
        self.canvas_tools = None
        self._check_canvas_tools()

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
            if self.canvas_tools.is_in_course(student.canvas_id):
                print("Uploading Grade for ", student.github_user_name)
                self.canvas_tools.update_grade_with_comment(student.canvas_id,
                                                            student.score,
                                                            student.get_message())
            else:
                print(student.github_user_name, " not in class")

    def step_read_tests(self):
        with open(self.setup_dir + '/grades.csv', 'w') as csvfile:
            grad_writer = csv.writer(csvfile)
            grad_writer.writerow(self.students[0].get_row_name())
            # TODO: add message to student
            for student in self.students:
                student_dir = self.setup_dir + "/forks/" + student.github_user_name

                junit_weight = grade_weight.JUnit_Weight / 100
                junit_result = junitxmlparser.get_mut_tests_results(
                    self.num_of_junit_tests, student_dir + '/build/test-results/test', '/TEST-junit-jupiter.xml',
                    student)
                junit_result = min(100, max(0, junit_result))
                student.junit_result = junit_result

                checkstyle_weight = grade_weight.Collaborators_Weight / 100
                checkstyle_result = checkstyletools.get_checkstyle_results(student_dir + '/checkstyleoutfile')
                if not student.has_src:
                    checkstyle_result = 0
                student.checkstyle_result = checkstyle_result

                collaborators_weight = grade_weight.CheckStyle_Weight / 100
                out_of = grade_weight.Collaborators_Weight
                collaborators_result = min(100, ((max(0, (out_of - student.num_of_bad_collaborators)) / out_of) * 100))
                if (not student.has_src) and (not student.has_fork):
                    collaborators_result = 0

                assert (junit_weight + checkstyle_weight + collaborators_weight) == 1
                result = (junit_weight * junit_result) + \
                         (checkstyle_weight * checkstyle_result) + \
                         (collaborators_weight * collaborators_result)
                student.score = result
                if (not student.has_src) and (not student.has_fork):
                    assert result == 0
                student.old_score = self.canvas_tools.get_grade(student.canvas_id)
                print(student.get_row_message())
                grad_writer.writerow(student.get_row())
        with open(self.setup_dir + '/grades_with_message.csv', 'w') as csvfile:
            grad_writer = csv.writer(csvfile)
            grad_writer.writerow(self.students[0].get_row_message_name())
            for student in self.students:
                grad_writer.writerow(student.get_row_message())

    def step_run_tests(self):
        # TODO: use containerized (Ex Docker) to test
        for student in self.students:
            if os.path.exists(f"{self.setup_dir}/forks/{student.github_user_name}"):
                if student.canvas_id != secret.COURSE_TEST_STUDENT_ID:
                    with open(f"{self.setup_dir}/forks/{student.github_user_name}/testoutput.txt", "w") as output:
                        student_dir = self.setup_dir + "/forks/" + student.github_user_name
                        output.write(student.github_user_name)
                        output.write("\n")
                        output.write(student_dir)
                        output.write("\n")
                        # Compile students code
                        compile_command = ("cd " + student_dir + " && " +
                                           currentLab.JAVA_PATH + "c -Xlint:unchecked -cp " +
                                           self.setup_dir + "/tools/junit-platform-console-standalone-1.9.2.jar -cp " +
                                           self.source_test_jar + " -d out/classes $(find src -name '*.java')")
                        output.write(compile_command)
                        output.write("\n")
                        stream = os.popen(compile_command)
                        output.write(stream.read())
                        # Run JUnit Tests
                        # TODO: add Timeout to the tests
                        index = 0
                        for junit_to_run in self.junit_to_run_list:
                            index += 1
                            junit_tests_command = "cd " + student_dir + " && " + \
                                                  currentLab.JAVA_PATH + " -jar " + \
                                                  self.setup_dir + "/tools/junit-platform-console-standalone-1.9.2.jar " + \
                                                  "--reports-dir=build/test-results/test" + str(index) + " -cp " + \
                                                  self.source_test_jar + " -cp out/classes --select-class=" + junit_to_run
                            print(junit_tests_command)
                            output.write(junit_tests_command)
                            output.write("\n")
                            stream = os.popen(junit_tests_command)
                            output.write(stream.read())
                        # Run CheckStyle Tests
                        checkstyle_command = ("cd " + student_dir + " && " +
                                              currentLab.JAVA_PATH + " -jar " +
                                              self.setup_dir + "/tools/checkstyle-10.9.3-all.jar " +
                                              "-c=https://github.com/tztz8/HelloGradle/raw/master/ewu-cscd212-error.xml " +  # Checkstyle for CSCD212
                                              "-o=checkstyleoutfile $(find src -name '*.java')")
                        output.write(checkstyle_command)
                        output.write("\n")
                        stream = os.popen(checkstyle_command)
                        output.write(stream.read())
                        print(student.github_user_name)
                else:
                    print("not in class, skipping")
            else:
                print("missing ", student.github_user_name)

    def step_setup_tests(self):
        # make tool dir, change into tool dir, download file
        if not os.path.exists(self.setup_dir + "/tools/" + "junit-platform-console-standalone-1.9.2.jar"):
            os.system("mkdir -p " + self.setup_dir + "/tools && cd " + self.setup_dir + "/tools && wget "
                      + "https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.9.2/junit-platform-console-standalone-1.9.2.jar")
        # make tool dir, change into tool dir, download file
        if not os.path.exists(self.setup_dir + "/tools/" + "checkstyle-10.9.3-all.jar"):
            os.system("mkdir -p " + self.setup_dir + "/tools && cd " + self.setup_dir + "/tools && wget "
                      + "https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.9.3/checkstyle-10.9.3-all.jar")
        # copy test jar to tools
        shutil.copy(self.source_test_jar, self.setup_dir + "/tools")
        # TODO: when running the JUnit tests use this jar file
        print("Copy Jar into tools done")

    def step_setup_labs(self):
        # [ name for name in os.listdir(setup_dir) if os.path.isdir(os.path.join(setup_dir, name)) ]
        for student in self.students:
            student_dir = self.setup_dir + "/forks/" + student.github_user_name
            if os.path.exists(student_dir + "/out"):
                shutil.rmtree(student_dir + "/out")  # If student modify/ignore the .gitignore file
            if os.path.exists(student_dir + "/.idea"):
                shutil.rmtree(student_dir + "/.idea", ignore_errors=True)  # If I need to grade make it better

            if os.path.exists(student_dir + "/docs"):
                shutil.rmtree(student_dir + "/docs")  # stop finding files in here that not needed
            else:
                print(student.github_user_name, " is missing docs folder")

            # TODO: add flag
            if os.path.exists(student_dir + "/tests"):
                shutil.rmtree(student_dir + "/tests")  # remove old tests (also the student may modify the tests)
            else:
                print(student.github_user_name, " is missing tests folder")

            if os.path.exists(student_dir + "/*.iml"):
                os.remove(student_dir + "/*.iml")  # If I need to grade make it better

            student.has_src = True
            if os.path.exists(student_dir + "/src"):
                print(student.github_user_name, " Setup Done")
            else:
                found = False
                found = self._step_get_student_canvas(found, student, student_dir)
                if found:
                    print(student.github_user_name, " Was Missing src folder")
                else:
                    student.message.append("Missing src folder")
                    student.has_src = False
                    print(student.github_user_name, " Missing src folder")

    def step_get_labs(self):
        # Setup GitHub API
        self.github_tool = Github(self.gitHub_oauthToken)
        self.start_repo = self.github_tool.get_repo(self.gitHub_start_repo)
        forks_pages = self.start_repo.get_forks()
        # Info
        github_users = dict()
        github_username_in_class = list()
        # Get class only
        row_num = 0
        with open(self.class_csv, 'r') as class_csv_file:
            csv_reader = csv.reader(class_csv_file, delimiter=',')
            self._check_canvas_tools()
            for row in csv_reader:
                if row_num != 0:
                    github_username_in_class.append(row[3].lower())
                row_num += 1
        # Setup loop
        num_of_forks = 0
        num_of_fork_pages = 0
        forks = forks_pages.get_page(0)
        if not os.path.exists(self.setup_dir):
            os.mkdir(self.setup_dir)
        with open(f"{self.setup_dir}/gitoutput.txt", "w") as outfile:  # debug output file
            while len(forks) > 0:  # GitHub API will only give page of forks at a time
                # TODO: fork only students from csv file (let us use starting repo that not only for this class)
                for fork in forks:  # Each fork
                    # Check if in class (Use for when start repo is not just this class)
                    github_user_name = fork.owner.login.lower()
                    if github_user_name not in github_username_in_class:
                        continue
                    student = student_object()
                    student.message = []
                    # updated_at = fork.updated_at
                    # TODO: check if user in class_csv
                    # github_user_name class_csv
                    outfile.write("Getting " + github_user_name + " fork")
                    outfile.write("\n")
                    # Clone the fork (student repo)
                    url = fork.ssh_url
                    clone_to = self.setup_dir + "/forks/" + github_user_name
                    already_exists = False
                    timer_start = time.time()
                    if not os.path.exists(clone_to):
                        # Wait for git (There is a limit of git clone can be done at a time)
                        # If it is there it is all good
                        while (abs(time.time() - timer_start) < 90) and (not os.path.exists(clone_to)):
                            timer_start_in = time.time()
                            # not there
                            # command = ["git", "clone", "--progress", url, clone_to]
                            command = ["git", "clone", url, clone_to]
                            # run command
                            subprocess.run(command, stdout=outfile, stderr=outfile)
                            time_to_wait = 2
                            if not os.path.exists(clone_to):
                                time_to_wait = 10
                            while abs(time.time() - timer_start_in) < time_to_wait:
                                pass
                    else:
                        already_exists = True
                        stream = self.clean_up_repo(clone_to, False)  # TODO: set get_new True
                        outfile.write(stream.read())
                        outfile.write("\n")
                        # Wait for git (There is a limit of git clone can be done at a time)
                        while abs(time.time() - timer_start) < 2:  # TODO: when get_new is True be 15
                            pass

                    collaborators = fork.get_collaborators()
                    allowed_users = secret.GITHUB_ALLOWED_USERS.copy()
                    allowed_users.append(github_user_name)
                    num_of_bad_collaborators = 0
                    try:
                        if collaborators.totalCount > len(allowed_users):
                            print(github_user_name, " has too many Collaborators")
                            student.message.append("has too many Collaborators in GitHub")
                            for collaborator in collaborators:
                                if collaborator.login not in allowed_users:
                                    num_of_bad_collaborators += 1
                    except:
                        print(github_user_name, " unable to read Collaborators")
                        print(github_user_name, " adding 50 to bad collaborators")
                        num_of_bad_collaborators += 50

                    # Done with getting a lab
                    self.students.append(student)
                    student.name = "Unknown"
                    student.canvas_id = secret.COURSE_TEST_STUDENT_ID
                    student.github_user_name = github_user_name
                    github_users[github_user_name] = len(self.students) - 1
                    student.clone_to = clone_to
                    student.num_of_bad_collaborators = num_of_bad_collaborators
                    student.old_score = 0
                    student.has_fork = True
                    print("User: ", github_user_name, ", already exists: ", already_exists, ", clone to: ", clone_to)
                    num_of_forks += 1
                num_of_fork_pages += 1
                forks = forks_pages.get_page(num_of_fork_pages)  # GitHub API will only give page of forks at a time
                assert num_of_forks <= self.start_repo.forks
        num_of_students = 0
        num_of_canvas_download = 0
        with open(self.class_csv, 'r') as class_csv_file:
            csv_reader = csv.reader(class_csv_file, delimiter=',')
            self._check_canvas_tools()
            for row in csv_reader:
                if num_of_students != 0 and row[3].lower() in github_users.keys():
                    self.students[github_users[row[3].lower()]].name = row[0]
                    self.students[github_users[row[3].lower()]].canvas_id = int(row[1])
                elif num_of_students != 0:
                    print("Missing Student Fork: ", row)
                studetn_folder = self.setup_dir + "/forks/" + row[3].lower()

                if num_of_students != 0 and row[3].lower() not in github_users.keys():
                    github_users[row[3].lower()] = len(self.students)
                    # [row[0], row[1], row[3]..lower(), self.setup_dir + "/forks/" + row[3]..lower(), 0]
                    student = student_object()
                    self.students.append(student)
                    student.name = row[0]
                    student.canvas_id = int(row[1])
                    student.github_user_name = row[3].lower()
                    student.clone_to = self.setup_dir + "/forks/" + row[3].lower()
                    student.num_of_bad_collaborators = 0
                    student.old_score = 0
                    student.has_fork = False
                    student.message = ["Missing Github Fork"]

                # Missing fork or src folder
                if num_of_students != 0 and not (row[3].lower() in github_users.keys() or os.path.exists(
                        studetn_folder + "/src")):
                    found_src_folder = False
                    found_src_folder = self._step_get_student_canvas(found_src_folder,
                                                                     self.students[github_users[row[3].lower()]],
                                                                     studetn_folder)
                    # Check if src folder is there
                    if os.path.exists(studetn_folder + "/src"):
                        # move src folder
                        found_src_folder = self.move_src_folder(found_src_folder, studetn_folder)
                    if not found_src_folder:
                        print("Missing Student src folder: ", row)
                    num_of_canvas_download += 1

                num_of_students += 1
        # Done with getting the labs
        print("Number of Labs: ", num_of_forks,
              ", Number of Forks: ", self.start_repo.forks,
              ", Number of Fork Pages: ", num_of_fork_pages,
              ", Number of Canvas Download: ", num_of_canvas_download,
              ", Number of students: ", num_of_students)
        return self.students

    def clean_up_repo(self, clone_to, get_new):
        # Move in to students fork
        command = "cd " + clone_to
        # Checkout there default branch
        command += " && git checkout $(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)"
        # Remove any old work we need in their fork
        command += " && git restore . && git clean -f"
        # Get any update from the student
        if get_new:
            command += " && git pull"
        stream = os.popen(command)
        return stream

    def _step_get_student_canvas(self, found_src_folder, student: student_object, studetn_folder):
        if self.canvas_tools.is_in_course(student.canvas_id):
            # get canvas submission
            submission = self.canvas_tools.assignment.get_submission(student.canvas_id)
            if not os.path.exists(studetn_folder):
                os.mkdir(studetn_folder)
            if not os.path.exists(studetn_folder + "/download"):
                os.mkdir(studetn_folder + "/download")
            for file in submission.attachments:
                file_name_parts = file.__str__().split(".")
                output_file = studetn_folder + "/download/" + file.__str__()
                file.download(output_file)
                if file_name_parts[len(file_name_parts) - 1] == "zip":
                    # unzip submission
                    shutil.unpack_archive(output_file, studetn_folder)
                    if os.path.exists(self.setup_dir + "/forks/" + student.github_user_name + "/__MACOSX"):
                        shutil.rmtree(self.setup_dir + "/forks/" + student.github_user_name + "/__MACOSX")
                    # move src folder
                    found_src_folder = self.move_src_folder(found_src_folder, studetn_folder)
        else:
            print("Student not in canvas: ", student.github_user_name)
        return found_src_folder

    def move_src_folder(self, found_src_folder, studetn_folder):
        for root, subdirs, files in os.walk(studetn_folder):
            for d in subdirs:
                if d == "src":
                    found_src_folder = True
                    shutil.move(os.path.join(root, d), studetn_folder + "/src")
        return found_src_folder


def do_we_continue(strin):
    ans = input(strin + ": Countue?")
    ans = ans.lower()
    if ans == 'no' or ans == 'n':
        sys.exit("No Countue")
    if ans == 'r':
        return True
    return False


if __name__ == '__main__':
    test_runer = TestRunner()
    # test_runer.gui_set_things()
    while do_we_continue("step_get_labs"):
        test_runer.step_get_labs()
    while do_we_continue("step_setup_labs"):
        test_runer.step_setup_labs()
    while do_we_continue("step_setup_tests"):
        test_runer.step_setup_tests()
    while do_we_continue("step_run_tests"):
        test_runer.step_run_tests()
    while do_we_continue("step_read_tests"):
        test_runer.step_read_tests()
    while do_we_continue("step_upload_grades"):
        test_runer.step_upload_grades()
