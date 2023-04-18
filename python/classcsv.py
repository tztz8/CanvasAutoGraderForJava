import csv



if __name__ == '__main__':
    with open("/home/tztz8/IdeaProjects/EWU/CSCD212S23/class.csv", 'r') as class_csv_file:
        csv_reader = csv.reader(class_csv_file, delimiter=',')
