#!/usr/bin/env python3

# Generate a tikz graph based on a git commit log. Based on Michael Hauspie's
# Ruby script of the same name: https://gist.github.com/hauspie/2397222

# Author: Alexander Bauer <sasha@linux.com>

import sys
import os
import re
import json

try:
    import jinja2
except ImportError as e:
    print("Could not import jinja2, which is used for creating the final template: %s" % e)
    os.exit(1)

class Repository:
    _DEFAULT_PRIMARY_BRANCH = "master"
    _TIKZ_PICTURE_TEMPLATE = jinja2.Template("""

\\begin{tikzpicture}

{% for branch_index, branch_name in enumerate(branches) %}
{% if branches[branch_name].commit_ids %}
{% set ref_y_offset = ydist * (len(branches[branch_name].commit_ids) + 1) %}
\\node[git_ref] ({{branch_name}}) at ({{branch_index}}, {{ref_y_offset}}) {\\verb+{{branch_name}}+};

{% for index, commit_id in enumerate(branches[branch_name].commit_ids) %}
{% set commit = commits[commit_id] %}
\\node[git_commit] ({{commit.id}}) at ({{branch_index}},{{ydist * (index + 1)}}) {\\verb+{{commit.id}}+};
\\node[git_commit_message,right] (message_{{commit.id}}) at ({{branch_index + 2}},{{ydist * (index + 1)}}) {\\verb+{{commit.message}}+};
{% endfor %}

{% endif %}
{% endfor %}



{% for branch_name in branches %}
{% if branches[branch_name].commit_ids %}
\\draw[git_ref_arrow] ({{branch_name}}) -- ({{branches[branch_name].commit_ids[-1]}});
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
        self.commits = {}
        self.branches = {}

    def add_commit(self, commit, branch=_DEFAULT_PRIMARY_BRANCH):
        self.commits[commit.id] = commit
        self.branches[branch].commit_ids.append(commit.id)
    def add_branch(self, branch):
        self.branches[branch.name] = branch

    def to_tikz(self):
        return self._TIKZ_PICTURE_TEMPLATE.render(commits = self.commits,
                branches = self.branches,
                primary_branch_name = self._DEFAULT_PRIMARY_BRANCH,
                ydist = 2,
                enumerate = enumerate, len = len)

class Branch:
    def __init__(self, name):
        self.name = name
        self.commit_ids = []

class Commit:
    # COMMIT_ID PARENT0 PARENT1... (REF0, REF1...) Commit message
    _COMMIT_ID = re.compile('^[a-f0-9]{7}[a-f0-9]*$')
    # _COMMIT_MARKER = re.compile('^\*$')
    # _TREE_SPACER = re.compile('^[|\/\\\\]$')
    class MalformedCommitLineError(Exception): pass

    def __init__(self, id, message, children=[], parents=[], refs=[]):
        self.id = id
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
        return json.dumps(self.__dict__)

    @classmethod
    def parse(cls, line):
        commit = cls(None, None, [], [])
        message_words = []

        for position, word in enumerate(line.split()):
            # Match the commit ID before anything else
            if commit.id == None:
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



if __name__ == "__main__":
    repo = Repository()
    repo.add_branch(Branch("master"))
    repo.add_branch(Branch("f.graph-branches"))
    for line in sys.stdin:
        repo.add_commit(Commit.parse(line), branch="master")
    print(repo.to_tikz())
