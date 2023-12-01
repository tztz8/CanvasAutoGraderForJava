from git import Repo

# https://blog.knoldus.com/gitpython-how-to-use-git-with-python/

COMMITS_TO_PRINT = 500


def print_commit_data(commit):
    print('-----')
    print(str(commit.hexsha))
    print("\"{}\" by {} ({})".format(commit.summary, commit.author.name, commit.author.email))
    print(str(commit.authored_datetime))
    print(str("count: {} and size: {}".format(commit.count(), commit.size)))
    # print("gpg: {}".format(commit.gpgsig))


def print_repository_info(repo):
    print('Repository description: {}'.format(repo.description))
    print('Repository active branch is {}'.format(repo.active_branch))

    for remote in repo.remotes:
        print('Remote named "{}" with URL "{}"'.format(remote, remote.url))

    print('Last commit for repository is {}.'.format(str(repo.head.commit.hexsha)))


if __name__ == '__main__':
    print("Testing Git")
    repo = Repo("/home/tztz8/dev/IdeaProjects/EWU/CSCD212F23/cscd212-f23-jar-tests-files")
    if not repo.bare:
        print('Repo at {} successfully loaded.'.format("cscd212-f23-lab7"))
        print_repository_info(repo)

        # create list of commits then print some of them to stdout
        commits = list(repo.iter_commits(repo.active_branch))[:COMMITS_TO_PRINT]
        for commit in commits:
            print_commit_data(commit)
            pass

        found = False
        index = -1
        for i, commit in enumerate(commits):
            if "lab 7" in commit.summary:
                found = True
                index = i
        if found:
            print("found")
            print_commit_data(commits[index])
            repo.git.checkout(commits[index])
        else:
            print("Not found")

    else:
        print('Could not load repository at {} :'.format("cscd212-f23-lab7"))
