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

    old_score: float

    has_src: bool
    has_fork: bool

    message: list[str]

    def get_row_name(self):
        return ["name", "canvas_id", "github_user_name", "clone_to",
                "old_score",
                "num_of_bad_collaborators", "junit_result", "checkstyle_result",
                "score"]

    def get_row(self):
        return [self.name, self.canvas_id, self.github_user_name, self.clone_to,
                self.old_score,
                self.num_of_bad_collaborators, self.junit_result, self.checkstyle_result,
                self.score]

    def get_row_message_name(self):
        row = self.get_row_name()
        row.append("message")
        return row

    def get_row_message(self):
        row = self.get_row()
        row.append(self.get_message())
        return row

    def get_message(self):
        messages = ""
        for message in self.message:
            messages += message
            messages += "\nMessage: "
        messages += "No more messages"
        message_string = "Auto Grader Output for {username}:\n\n" \
                         "Message: {messages}\n\n" \
                         "----------------------------------------------------------------------------------------\n" \
                         "Results\n" \
                         "Collaborators Score({nbcpoints}% weight) " \
                         "(What score for: if you remove the class from collaborators on GitHub): {nbc}\n" \
                         "JUnit Score({junitpoints}% weight) " \
                         "(What score for: how much junit tests you pass): {junit}\n" \
                         "CheckStyle Score({checkpoints}% weight) " \
                         "(What score for: if you use final, this, override): {check}"
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
