# EWU Auto Grading

> In Progress

> NOT READY TO BE USED

---

Use to auto grade students Java assignments.

## Needs to have to run

- [ ]  csv file of the class GitHub user name's and canvas id (not the same as student id)
- [ ] Starting repository that the student's fork from
  - [ ] Students code need to be in `src` folder on the root of there repository
- [ ] Jar of the JUnit tests you want to tests the students code

## Test Runner

- Gets the labs

  - Get the students forks
  - If the fork or src folder in students fork does not exist
    - try to get the assignment from canvas
    - try to search for src folder

- Setup the labs

  - Remove things

  - > Not needed anymore, was used to make it easer when I need  to grade by hand

- Setup the tests

  - get the jar files needed

- Run Tests

  - Go to each student
  - Compile
  - Run JUnit tests
  - Run Checkstyle 

- Read 

  - Read the output files
    - Make a score
    - Get messages
  - Make a grade

- Push Grade

  - Upload grade and messages to canvas