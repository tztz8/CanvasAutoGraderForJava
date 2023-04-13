# update Grade using python

```python
# Import the Canvas class
from canvasapi import Canvas

import csv

def updateGrades():
    # Canvas API URL
    API_URL = "https://canvas.url/"
    # Canvas API key
    API_KEY = "CANVAS-USER-OAUTH-API-TOKEN"

    # Initialize a new Canvas object
    canvas = Canvas(API_URL, API_KEY)

    # Grab course with ID of 123456
    course = canvas.get_course(1234567)

    # Grab assignment with ID of 1234
    assignment = course.get_assignment(1234567)

    users = course.get_users()

    added_points = 2

    submissions = assignment.get_submissions()
    # assignment.get_submission(1234567)

    print("Assignment Name: ", assignment.name, ", Due: ", assignment.due_at, ", lock: ", assignment.lock_at)
    print("Points: ", assignment.points_possible)

    # with open('grades.csv', 'w') as csvfile:
    #     gradwriter = csv.writer(csvfile)
    #
    #     gradwriter.writerow(["name", "canvas_id", "email", "score"])
    #
    #     for submission in submissions:
    #
    #         # Handle an unscored assignment by checking the `score` value
    #         username = "unknown"
    #         email = "unknown"
    #         for user in users:
    #             if (user.id == submission.user_id):
    #                 username = user.name
    #                 email = user.email
    #                 break
    #         print("user_name: ", username, ", email: ", email, ", score:", submission.score)
    #
    #         gradwriter.writerow([username, submission.user_id, email, submission.score])

    for submission in submissions:

        # Handle an unscored assignment by checking the `score` value
        username = "unknown"
        email = "unknown"
        for user in users:
            if (user.id == submission.user_id):
                username = user.name
                email = user.email
                break
        print("user_name: ", username, ", email: ", email, ", score:", submission.score)

        if (username == "unknown"):
            print("user id: ", submission.user_id)
            # test student
            if (submission.user_id == 1234567):
                submission.edit(submission={'posted_grade': 2})

        # if submission.score is not None:
        #     score = submission.score + added_points
        # else:
        #     # Treat no submission as 0 points
        #     score = 0 + added_points
        #
        # submission.edit(submission={'posted_grade': score})




if __name__ == '__main__':
    print("canvasapi run:")
    updateGrades()

```