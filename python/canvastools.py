from canvasapi import Canvas


# TODO: get info (name, due, lock, points)

def update_grade(api_key, api_url, course_id, assignment_id, user_id, grade):
    # Initialize a new Canvas object
    canvas = Canvas(api_url, api_key)

    # Grab course with ID of 123456
    course = canvas.get_course(course_id)

    # Grab assignment with ID of 1234
    assignment = course.get_assignment(assignment_id)

    # Grab user submission
    submission = assignment.get_submission(user_id)

    points = assignment.points_possible

    output_grade = (grade / 100) * points

    submission.edit(submission={'posted_grade': output_grade})
