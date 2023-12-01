import csv
import os
import sys

import git

import checkstyletools
import currentLab
import grade_weight
import junitxmlparser
import secret
from testRunner import TestRunner, do_we_continue

# TODO: move user_story_names
user_story_names = ["Add", "Subtract", "Multiply", "Doubles", "Divide", "Factorial", "Previous"]
ttd_tasks = ["Unit Test", "Feature Done", "Refactor"]
number_of_commits = 21

def step_run_tdd_tests(test_runer):
    commit_messages_for_ttd = []
    for user_story_name in user_story_names:
        for ttd_task in ttd_tasks:
            commit_messages_for_ttd.append(f"{user_story_name}: {ttd_task}")
    assert len(commit_messages_for_ttd) == number_of_commits
    for student in test_runer.students:
        if os.path.exists(f"{test_runer.setup_dir}/forks/{student.github_user_name}"):
            if student.canvas_id != secret.COURSE_TEST_STUDENT_ID:
                student_repo = git.Repo(f"{test_runer.setup_dir}/forks/{student.github_user_name}")
                if student_repo.bare:
                    print("Error: unable to open student_repo")
                    student.message.append("Unable to open student repo")
                # Note list is given from most recent commit to last commit
                student_commits = list(student_repo.iter_commits(student_repo.active_branch))[
                                  :(len(commit_messages_for_ttd) + 20)]
                student_commits.reverse()
                # Get index of tdd commits
                index_of_ttd = dict()
                for i, commit in enumerate(student_commits):
                    commit_message = commit.summary.lower()
                    # allow for incorrect spacing and caps
                    for user_story_name in user_story_names:
                        for ttd_task in ttd_tasks:
                            if (user_story_name.lower() in commit_message) and (ttd_task.lower() in commit_message):
                                index_of_ttd[f"{user_story_name}: {ttd_task}"] = i
                                break
                        else:
                            continue
                        break
                # Where the student code is at
                student_dir = test_runer.setup_dir + "/forks/" + student.github_user_name
                # Where the student result is at
                student_output = f"{test_runer.setup_dir}/forks/{student.github_user_name}-tdd-output"
                if not os.path.exists(student_output):
                    os.mkdir(student_output)
                # Test each step in TDD
                for commit_message in commit_messages_for_ttd:
                    # Output of the testing commit
                    with (open(f"{student_output}/test-{commit_message.lower().replace(' ', '-').replace(':', '')}-output.txt", "w") as output):
                        output.write(student.github_user_name)
                        output.write("\n")
                        output.write(student_dir)
                        output.write("\n")
                        output.write(commit_message)
                        output.write("\n\n")
                        # Checking if commit exist in student repo
                        if commit_message in index_of_ttd:
                            # Clean up old work
                            stream = test_runer.clean_up_repo(student_dir, False)
                            output.write(stream.read())
                            output.write("\n")
                            # Checkout commit (tdd step)
                            student_repo.git.checkout(student_commits[index_of_ttd[commit_message]])
                            if ttd_tasks[0] in commit_message:
                                output.write("Running Unit Test Test")
                                # Note: tests should fail
                                run_both_ta_and_student_junit_tests(commit_message, output, student_dir, student_output,
                                                                    test_runer, ttd_tasks, user_story_names)
                            elif ttd_tasks[1] in commit_message:
                                output.write("Running Feature Test")
                                # Note: tests should pass
                                run_both_ta_and_student_junit_tests(commit_message, output, student_dir, student_output,
                                                                    test_runer, ttd_tasks, user_story_names)
                            else:
                                assert ttd_tasks[2] in commit_message
                                output.write("Running Refactor Test")
                                # Note: tests should pass
                                run_both_ta_and_student_junit_tests(commit_message, output, student_dir, student_output,
                                                                    test_runer, ttd_tasks, user_story_names)
                                # TODO: Run student tests on sol src code
                                # Check Style (The only time we care about check style)
                                run_check_style(output, student_dir, True, test_runer, f"../{student.github_user_name}-tdd-output/{commit_message.lower().replace(' ', '-').replace(':', '')}-checkstyleoutfile")
                        else:
                            output.write(f"Missing {commit_message} commit")
                            student.message.append(f"Missing {commit_message} commit")
                print(student.github_user_name)
            else:
                print("not in class, skipping")
        else:
            print("missing ", student.github_user_name)


def run_both_ta_and_student_junit_tests(commit_message, output, student_dir, student_output, test_runer, ttd_tasks,
                                        user_story_names):
    junit_to_run = commit_message.replace(" ", "").replace(":", "_")
    # for user_story_name in user_story_names:
    #     if user_story_name.lower() in commit_message.lower():
    #         junit_to_run += user_story_name.replace(" ", "")
    #         break
    # # TA JUnit tests
    # run_junit_tests(junit_to_run, output, student_dir, student_output, test_runer,
    #                 ttd_tasks, True)
    # Student tests
    run_junit_tests(junit_to_run, output, student_dir, student_output, test_runer,
                    ttd_tasks, False)


def run_junit_tests(junit_to_run, output, student_dir, student_output, test_runer, ttd_tasks, use_ta_tests):
    compile_code(output, student_dir, use_ta_tests, test_runer)
    junit_tests_command = "cd " + student_dir + " && " + \
                          currentLab.JAVA_PATH + " -jar " + \
                          test_runer.setup_dir + "/tools/junit-platform-console-standalone-1.9.2.jar " + \
                          "--reports-dir=" + student_output + "/junit-out/" + junit_to_run
    # JUnit output name
    if use_ta_tests:
        junit_tests_command += "_TA"
    else:
        junit_tests_command += "_Student"
    # add students compiled code
    junit_tests_command += " -cp out/classes"
    if use_ta_tests:
        junit_tests_command += " --select-class=cscd212TATests." + junit_to_run
    else:
        junit_tests_command += " --scan-classpath"
    print(junit_tests_command)
    output.write(junit_tests_command)
    output.write("\n")
    stream = os.popen(junit_tests_command)
    output.write(stream.read())


def run_check_style(output, student_dir, include_tests, test_runer, outputfilename):
    # Run CheckStyle Tests
    checkstyle_command = ("cd " + student_dir + " && " +
                          currentLab.JAVA_PATH + " -jar " +
                          test_runer.setup_dir + "/tools/checkstyle-10.9.3-all.jar " +
                          "-c=https://github.com/tztz8/HelloGradle/raw/master/ewu-cscd212-error.xml " +  # Checkstyle for CSCD212
                          "-o=" + outputfilename)
    if include_tests:
        # All files
        checkstyle_command += " $(find . -name '*.java')"
    else:
        # Only src files
        checkstyle_command += " $(find src -name '*.java')"
    output.write(checkstyle_command)
    output.write("\n")
    stream = os.popen(checkstyle_command)
    output.write(stream.read())


def compile_code(output, student_dir, compile_tests, test_runer):
    compile_command = ("cd " + student_dir + " && " +
                       currentLab.JAVA_PATH + "c -Xlint:unchecked -cp " +
                       test_runer.setup_dir + "/tools/junit-platform-console-standalone-1.9.2.jar -cp " +
                       test_runer.source_test_jar + " -d out/classes")
    if compile_tests:
        # All files
        compile_command += " $(find . -name '*.java')"
    else:
        # Only src files
        compile_command += " $(find src -name '*.java')"
    # Compile students code
    output.write(compile_command)
    output.write("\n")
    stream = os.popen(compile_command)
    output.write(stream.read())


def step_read_tdd_tests(test_runer):
    # TODO: add ttd read code
    commit_messages_for_ttd = []
    for user_story_name in user_story_names:
        for ttd_task in ttd_tasks:
            commit_messages_for_ttd.append(f"{user_story_name}: {ttd_task}")
    assert len(commit_messages_for_ttd) == number_of_commits
    with open(test_runer.setup_dir + '/grades.csv', 'w') as csvfile:
        grad_writer = csv.writer(csvfile)
        grad_writer.writerow(test_runer.students[0].get_row_name())
        # TODO: add message to student
        for student in test_runer.students:
            student_dir = test_runer.setup_dir + "/forks/" + student.github_user_name
            test_runer.clean_up_repo(student_dir, False)
            student_output = f"{test_runer.setup_dir}/forks/{student.github_user_name}-tdd-output"

            junit_weight = grade_weight.JUnit_Weight / 100
            junit_result_total = 0
            for commit_message in commit_messages_for_ttd:
                # TODO: Check Read result
                for who_is in ["TA", "Student"]:
                    # TODO: add to junitxmlparser for TDD reader (no message for fail on Unit Tests and There Code)
                    junit_result = junitxmlparser.get_mut_tests_results(
                        test_runer.num_of_junit_tests,
                        student_output + '/junit-out/' + \
                        commit_message.replace(" ", "").replace(":", "_") + who_is,
                        '/TEST-junit-jupiter.xml',
                        student)
                    junit_result = min(100, max(0, junit_result))
                    # If unit tests
                    if ttd_tasks[0] in commit_message:
                        # TODO: want NEW fail tests (old test should still pass)
                        junit_result = 100 - junit_result  # FIXME: wrong
                    junit_result_total += junit_result
            # Fix 0 to 100 ((len(commit_messages_for_ttd) * 2) * 100)
            junit_result = junit_result_total / (len(commit_messages_for_ttd) * 2)
            student.junit_result = junit_result

            checkstyle_weight = grade_weight.Collaborators_Weight / 100
            checkstyle_result_total = 0
            for user_story_name in user_story_names:
                # TODO: check if works
                checkstyle_result = checkstyletools.get_checkstyle_results(f"{student_output}/{user_story_name.lower().replace(' ', '-').replace(':', '')}-{ttd_tasks[2].lower().replace(' ', '-').replace(':', '')}-checkstyleoutfile")
                checkstyle_result_total += checkstyle_result
            # Fix 0 to 100
            checkstyle_result = checkstyle_result_total / len(user_story_names)
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
            student.old_score = test_runer.canvas_tools.get_grade(student.canvas_id)
            print(student.get_row_message())
            grad_writer.writerow(student.get_row())
    with open(test_runer.setup_dir + '/grades_with_message.csv', 'w') as csvfile:
        grad_writer = csv.writer(csvfile)
        grad_writer.writerow(test_runer.students[0].get_row_message_name())
        for student in test_runer.students:
            grad_writer.writerow(student.get_row_message())


if __name__ == '__main__':
    test_runer = TestRunner()
    # test_runer.gui_set_things()
    while do_we_continue("step_get_labs"):
        test_runer.step_get_labs()
    while do_we_continue("step_setup_get_tests"):
        test_runer.step_setup_tests()
    while do_we_continue("step_run_tests"):
        step_run_tdd_tests(test_runer)
    while do_we_continue("step_read_tests"):
        step_read_tdd_tests(test_runer)
    # while do_we_continue("step_upload_grades"):
    #     test_runer.step_upload_grades()
