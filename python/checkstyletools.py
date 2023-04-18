def get_checkstyle_results(file):
    with open(file, 'r') as checkstyle_file:
        lines = checkstyle_file.readlines()
        # for line in lines:
        #     print(line)
        # print(len(lines) - 2)
        outOf = 15
        numOfProblems = len(lines) - 2
        result = (max(0, (outOf - numOfProblems)) / outOf) * 100
        return result

if __name__ == '__main__':
    print("hello")
    print(get_checkstyle_results("/home/tztz8/IdeaProjects/EWU/CSCD212S23/testing/cscd212-s23-lab3-old/checkstyleoutfile"))

