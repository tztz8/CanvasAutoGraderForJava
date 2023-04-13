# EWU Auto Grading

> In Progress

> NOT READY TO BE USED

## TODO:

 - [ ] Check if modified and safe to upload
   - [ ] check workflow file on GitHub only modified by `TeacherAssistants` team
   - [ ] check if GitHub user in Class Team (Ex `CSCD212-S23`)
   - [ ] decrypt python file from different repo
     - GitHub Organization Secrets
     - public key only (key file can only decrypt not encrypt)
       - pgp (`gpg` command)
   - [ ] Get canvas api token from GitHub Organization Secrets
 - [ ] Check due date (and lock date)
   - [ ] If possible get student due date (and lock date)
 - [ ] Get Student Canvas ID
   - [ ] Get class list from GitHub Organization Secrets
     - From Lab 1 (Github User Name --> Canvas ID)
 - [ ] Get Student Grade
   - [ ] Run and Read JUnit results
   - [ ] Run and Read CheckStyle results
 - [ ] Upload Grade
   - [ ] if potable use rubric
 - [ ] Make it a GitHub Action
 - [ ] Add Doc
   - start in notes move to docs folder
   - [ ] How to use it
   - [ ] How this works