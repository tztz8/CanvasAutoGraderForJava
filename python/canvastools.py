import os
import shutil

from canvasapi import Canvas
from canvasapi.user import User

import currentLab
import secret


class CanvasTools:
    def __init__(self, api_key: str, api_url: str, course_id: int, assignment_id: int):
        self.canvas = Canvas(api_url, api_key)
        self.course = self.canvas.get_course(course_id)
        self.users = self.course.get_users()
        self.assignment = self.course.get_assignment(assignment_id)
        print(self.getAssignmentInfoStr())

    def is_in_course(self, canvas_id: int):
        for user in self.users:
            if canvas_id == user.id:
                return True
        return False

    def getAssignmentInfoStr(self):
        return "Assignment Name: " + self.assignment.name \
            + ", Due: " + self.assignment.due_at \
            + ", lock: " + self.assignment.lock_at

    def getAssignmentInfo(self):
        return (self.assignment.name, self.assignment.due_at, self.assignment.lock_at)

    def download_submission(self, user_id: User | int, location: str):
        self.course.get_users()
        submission = self.assignment.get_submission(user_id)
        for file in submission.attachments:
            file.download(location)
            fileName = file.__str__().split(".")
            endPart = fileName[len(fileName)]
            print(endPart)

    def get_grade(self, user_id):
        if self.is_in_course(user_id):
            # Grab user submission
            submission = self.assignment.get_submission(user_id)
            old_points = submission.score
            if old_points is None:
                return 0
            else:
                return old_points
        else:
            return 0

    def update_grade(self, user_id, grade):
        # Grab user submission
        submission = self.assignment.get_submission(user_id)

        points = self.assignment.points_possible

        output_grade = (grade / 100) * points

        old_points = submission.score

        if old_points is None or output_grade >= old_points:
            submission.edit(submission={'posted_grade': output_grade})

    def update_grade_with_comment(self, user_id, grade, comment: str):
        # Grab user submission
        submission = self.assignment.get_submission(user_id)

        points = self.assignment.points_possible

        output_grade = (grade / 100) * points

        old_points = submission.score

        print(user_id, ": original grade: ", old_points, ", new grade: ", output_grade)
        if old_points is None or output_grade > float(old_points):
            submission.edit(submission={'posted_grade': output_grade}, comment={'text_comment': comment})
