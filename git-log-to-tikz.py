#!/usr/bin/env python3

# Generate a tikz graph based on a git commit log. Based on Michael Hauspie's
# Ruby script of the same name: https://gist.github.com/hauspie/2397222

# Author: Alexander Bauer <sasha@linux.com>

import sys
import re
import json

class Commit:
    # * COMMIT_ID PARENT0 PARENT1... (REF0, REF1...) Commit message
    _COMMIT_ID = re.compile('^[a-f0-9]{7}[a-f0-9]*$')
    _COMMIT_MARKER = re.compile('^\*$')
    _TREE_SPACER = re.compile('^[|\/\\\\]$')

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
            if cls._COMMIT_ID.match(word):
                # If we match something that looks like an ID, try to add it as
                # the commit ID.
                if commit.id == None:
                    commit.id = word
                # If the ID is already set, then add it as a parent. A commit
                # may have multiple parents.
                else:
                    commit.parents.append(word)
            elif cls._COMMIT_MARKER.match(word):
                # If we match something that identifies a 'node' in the graph,
                # mark its position down.
                commit.node_position = position
            elif cls._TREE_SPACER.match(word):
                # If we encounter a spacer, ignore it.
                pass
            else:
                message_words.append(word)

        commit.message = ' '.join(message_words)
        if commit.id == None:
            return None
        else:
            return commit

if __name__ == "__main__":
    for line in sys.stdin:
        print(Commit.parse(line))
