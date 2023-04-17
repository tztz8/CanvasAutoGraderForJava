from canvasapi import Canvas


class CanvasTools:
    def __init__(self, api_key: str, api_url: str, course_id: int, assignment_id: int):
        self.canvas = Canvas(api_url, api_key)
        self.course = self.canvas.get_course(course_id)
        self.assignment = self.course.get_assignment(assignment_id)

    def getAssignmentInfoStr(self):
        return "Assignment Name: " + self.assignment.name \
            + ", Due: " + self.assignment.due_at \
            + ", lock: " + self.assignment.lock_at

    def getAssignmentInfo(self):
        return (self.assignment.name, self.assignment.due_at, self.assignment.lock_at)

    def update_grade(self, user_id, grade):
        # Grab user submission
        submission = self.assignment.get_submission(user_id)

        points = self.assignment.points_possible

        output_grade = (grade / 100) * points

        submission.edit(submission={'posted_grade': output_grade})  # TODO: set grader auto
