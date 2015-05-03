#!/usr/bin/env python3

# Generate a tikz graph based on a git commit log. Based on Michael Hauspie's
# Ruby script of the same name: https://gist.github.com/hauspie/2397222

# Author: Alexander Bauer <sasha@linux.com>

import sys
import os
import subprocess
import datetime
import re
import json
import argparse
import collections

try:
    import jinja2
except ImportError as e:
    print("Could not import jinja2, which is used for creating the final template: %s" % e)
    os.exit(1)


_TEST_ = False
_TEST_OBJ_ = None
_MAKETEST_ = False

class Repository:
    _DEFAULT_PRIMARY_BRANCH = "master"
    _TIKZ_PICTURE_TEMPLATE = jinja2.Template("""

\\begin{tikzpicture}

{% for branch_index, branch_name in enumerate(branches) %}
{% if branches[branch_name].commit_ids %}
{% set branch = branches[branch_name] %}
{% set branch_offset = branch_index * 2 %}
\\node[git_ref] ({{branch_name | replace('.', '_')}})
    at ({{branch_offset}},
    {{ydist * len(commits) + ydist/3 * (len(branches) - branch_index - 1)}})
    {\\verb+{{branch_name}}+};

{% for index, commit_id in enumerate(branch.commit_ids) %}
{% set commit = commits[commit_id] %}
{% set commit_ypos = ydist * commit.history_index %}
\\node[git_commit] ({{commit.id}}) at
    ({{branch_offset}},{{commit_ypos}})
    {\\verb+{{commit.id}}+};
\\node[git_commit_message,right] (message_{{commit.id}})
    at ({{len(branches)*2}},{{commit_ypos}})
    {\\verb+{{commit.message}}+};
{% endfor %}

{% endif %}
{% endfor %}

{% for branch_name in branches %}
{% if branches[branch_name].commit_ids %}
\\draw[git_ref_arrow] ({{branch_name | replace('.', '_')}}) -- ({{branches[branch_name].commit_ids[-1]}});
{% endif %}
{% endfor %}

{% for commit in commits.values() %}
{% for parent in commit.parents %}
\\draw[git_arrow] ({{commit.id}}) -- ({{parent}});
{% endfor %}
{% endfor %}


\\end{tikzpicture}
""", trim_blocks=True)
    def __init__(self):
        self.commits = collections.OrderedDict()
        self.branches = collections.OrderedDict()

    def add_commit(self, commit, branch=_DEFAULT_PRIMARY_BRANCH, allow_duplicate=False):
        self.branches[branch].total_commits += 1
        if not allow_duplicate and commit.id in self.commits:
            return
        self.commits[commit.id] = commit
        self.branches[branch].commit_ids.append(commit.id)

    def add_branch(self, branch):
        self.branches[branch.name] = branch

    def load_all(self):
        "Uses git commands to read commits from the repository."
        # Read all commits from known branches.
        for branch in self.branches:
            self.read_branch(branch)

        # Sort the commits by their timestamp.
        self.commits = collections.OrderedDict(sorted(
            self.commits.items(), key=lambda pair: pair[1].time
            ))

        # Assign a history index to each commit, now that they're sorted.
        for index, commit in enumerate(self.commits.values()):
            commit.history_index = index

    def read_branch(self, branchname):
        if _TEST_:
            output = _TEST_OBJ_["branches"][branchname]
        else:
            output = subprocess.check_output(
                    ["git", "log", "--reverse", "--format='%at %h %p %s'", "--no-color",
                        branchname, "--"], universal_newlines=True)
        branch = self.branches[branchname]
        for line in output.split('\n'):
            line = line.strip('\'')
            try:
                commit = Commit.parse(line)
                if commit:
                    if _MAKETEST_:
                        self.add_commit(commit, branch=branchname,
                                allow_duplicate=True)
                    else:
                        self.add_commit(commit, branch=branchname)
            except Commit.MalformedCommitLineError as e:
                print("Skipping line in output: %s" % e)

    def to_testfile(self):
        test_obj = {"branches": {}}
        for branchname, branch in self.branches.items():
            test_obj["branches"][branchname] = '\n'.join(str(self.commits[commit_id]) for commit_id
                    in branch.commit_ids)

        return test_obj

    def to_tikz(self):
        return self._TIKZ_PICTURE_TEMPLATE.render(commits = self.commits,
                branches = self.branches,
                primary_branch_name = self._DEFAULT_PRIMARY_BRANCH,
                greatest_branch_length = max(branch.total_commits for branch in
                    self.branches.values()),
                ydist = 2,
                enumerate = enumerate, len = len)

class Branch:
    def __init__(self, name):
        self.name = name
        self.commit_ids = []
        self.total_commits = 0
    def __repr__(self):
        return self.__dict__

class Commit:
    # COMMIT_ID PARENT0 PARENT1... (REF0, REF1...) Commit message
    _COMMIT_ID = re.compile('^[a-f0-9]{7}[a-f0-9]*$')
    # _COMMIT_MARKER = re.compile('^\*$')
    # _TREE_SPACER = re.compile('^[|\/\\\\]$')
    class MalformedCommitLineError(Exception): pass

    def __init__(self, id, time, message, children=[], parents=[], refs=[]):
        self.id = id
        self.time = time
        self.message = message

        # Wrap elements in a list if they are not already.
        if type(children) != list:
            children = [children]
        self.children = children
        if type(parents) != list:
            parents = [parents]
        self.parents = parents
        if type(refs) != list:
            refs = [refs]
        self.refs = refs

        self.node_position = 0
        self.message_pos = 0

    def __str__(self):
        return "%d %s %s %s" % (self.time, self.id, " ".join(self.parents),
                self.message)

    @classmethod
    def parse(cls, line):
        commit = cls(None, None, None, [], [])
        message_words = []

        for position, word in enumerate(line.split()):
            # Match the time before anything else
            if commit.time == None:
                try:
                    commit.time = int(word)
                except ValueError:
                    raise cls.MalformedCommitLineError("Could not match commit time: %s" % word)
            # Next match the commit id
            elif commit.id == None:
                if cls._COMMIT_ID.match(word):
                    commit.id = word
                else:
                    raise cls.MalformedCommitLineError("Could not match commit ID: %s" % word)

            # Match any parent IDs
            elif cls._COMMIT_ID.match(word):
                commit.parents.append(word)

            # Otherwise, add the words as a message
            else:
                message_words.append(word)

        commit.message = ' '.join(message_words)
        if commit.id == None:
            return None
        else:
            return commit

def main(args):
    if args.testfile:
        global _TEST_
        global _TEST_OBJ_
        _TEST_ = True
        print(args.testfile)
        with open(args.testfile, 'r') as f:
            _TEST_OBJ_ = json.load(f)
    if args.maketest:
        global _MAKETEST_
        _MAKETEST_ = True
    repo = Repository()
    for branch in args.branches:
        repo.add_branch(Branch(branch))
    # for line in sys.stdin:
    #     repo.add_commit(Commit.parse(line), branch="master")
    repo.load_all()
    if _MAKETEST_:
        print(repo.to_testfile())
    else:
        print(repo.to_tikz())

def parse(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('branches', type=str, nargs='+')
    parser.add_argument('--maketest', action='store_true')
    parser.add_argument('--testfile', action='store')
    return parser.parse_args(args)

if __name__ == "__main__":
    sys.exit(main(parse(sys.argv[1:])))
