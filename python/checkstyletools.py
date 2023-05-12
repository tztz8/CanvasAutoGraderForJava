import os.path

import grade_weight


def get_checkstyle_results(file):
    if os.path.exists(file):
        with open(file, 'r') as checkstyle_file:
            lines = checkstyle_file.readlines()
            # for line in lines:
            #     print(line)
            # print(len(lines) - 2)
            out_of = grade_weight.CHECKSTYLE_OUT_OF
            num_of_problems = len(lines) - 2
            result = (max(0, (out_of - num_of_problems)) / out_of) * 100
            return result
    else:
        return 0

if __name__ == '__main__':
    print("hello")
    print(get_checkstyle_results("/home/tztz8/IdeaProjects/EWU/CSCD212S23/testing/cscd212-s23-lab3-old/checkstyleoutfile"))

