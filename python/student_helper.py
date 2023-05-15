import grade_weight


class student_object:
    name: str
    canvas_id: int
    github_user_name: str
    clone_to: str
    num_of_bad_collaborators: int
    junit_result: float
    checkstyle_result: float
    score: float

    message: list[str]

    def get_row_name(self):
        return ["name", "canvas_id", "github_user_name", "clone_to",
                "num_of_bad_collaborators", "junit_result", "checkstyle_result",
                "score"]

    def get_row(self):
        return [self.name, self.canvas_id, self.github_user_name, self.clone_to,
                self.num_of_bad_collaborators, self.junit_result, self.checkstyle_result,
                self.score]

    def get_message(self):
        messages = ""
        for message in self.message:
            messages += message
            messages += "\nMessage:"
        messages += " No more messages"
        message_string = "Auto Grader Output for {username}: \n" \
                         "Message: {messages} \n" \
                         "Results Collaborators({nbcpoints}%)(" \
                         "Why: do you remove the class from collaborators on GitHub): {nbc}\n " \
                         "JUnit Score({junitpoints}%)(Why: do you pass junit tests): {junit}\n " \
                         "CheckStyle Score({checkpoints}%)(Why: do you use final, this, override): {check}"
        out_of = grade_weight.Collaborators_Weight
        collaborators_result = (max(0, (out_of - self.num_of_bad_collaborators)) / out_of) * 100
        out_message = message_string.format(username=self.github_user_name,
                                            messages=messages,
                                            nbcpoints=grade_weight.Collaborators_Weight,
                                            nbc=collaborators_result,
                                            junitpoints=grade_weight.JUnit_Weight,
                                            junit=self.junit_result,
                                            checkpoints=grade_weight.CheckStyle_Weight,
                                            check=self.checkstyle_result)
        return out_message
