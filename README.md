# EWU Java Auto Grading

## Use to auto grade students Java assignments.

This start off as me learning about tools and libs to help with grading students assignments. Now it a tool that need to be **rebuilt** but still works for auto grading students assignments from both [Canvas LMS](https://www.instructure.com/canvas) and [GitHub](https://github.com/) and pushing those grades to Canvas LMS.

### Getting started using this tool

Requirements to use this tool

> This tool was and used in **Linux**

- [ ] Students Assignments need to be in a Jet Brains basic Java project (no gradle or maven) folder format

  - `*.java` in `src/` folder
  - JUnit testing code in  `tests/` folder

- [ ] For normal labs (Not checking the students JUnit test)

  Write some JUnit tests and jar them without the sol (TODO: Link to how to do so in Intellij)

  > Recommended to add a time outs to the JUnit if the students code has inf loop

- [ ] Make Both `secret.py` and `currentLab.py`

  - [ ] `secret.py` Has the api keys for both Canvas and GitHub
  - [ ] `currentLab.py` Has the needed info about the current Lab
    - Starting repo that the students fork from
    - The working dir for grading the lab
    - A csv file about the students in the class (TODO: Link to how to make the CSV file)
    - The JUnit Jar
    - Class name of the JUnit tests
    - Number of class names
    - Canvas HW ID (TODO: Link to how to get this)
    - Total number of JUnit tests
    - Path to java and javac version use for running these JUnit tests

- [ ] Update grade weights `grade_weight.py`

Basically ready to run the tool

> **Warring**: you are about to run the students code on your computer

> Recommended: use your IDE debugger when use the script

You can now run `testRunner.py` to grade the students assignments

As the script is running for each step it will ask to `: Countue?` you can:

- Use `r` to run/rerun the current step (`step_get_labs` is required for further steps)
- Use `no` or `n` to end the script
- Use anything else to skip the step

## Steps the scrip go throw

- `step_get_labs`

  > NOTE: Make a internal ref of the students for latter (This is why it can not be skipted)

  - Download the students lab
    - First look at forks of the starting repository for students code
      - if already clone in working dir it will refresh the clone
    - If did not find a student fork it will look for a zip on Canvas LMS on the HW ID

- `step_setup_labs`

  - Clean up students lab
    - Remove any `out` folder (Normally made by Jet Brains)
    - Remove any `.idea` folder (Make it easyer if you want to manaly grade to the students assgnment)
    - Remove any `docs` folder
    - Remove any `tests` folder
    - Check if `src` there and if not see if Canvas has a zip of students `src` code

- `step_setup_tests`

  - Make copy of tools in working dir
    - junit-platform-console-standalone jar file
    - checkstyle file
    - Junit jar file

- `step_run_tests`

  - Compile students code (with the test JUnit jar for if there was some lib you give the students to use can be include in that JUnit jar file)
  - Run the JUnit tests
  - Run CheckStyle on studetns code

- `step_read_tests`

  - Read the output files from above
  - Calculate the result of the student 

  > Also Makes a CSV with those result in the working dir

- `step_upload_grades`

  - Push those grades to Canvas LMS