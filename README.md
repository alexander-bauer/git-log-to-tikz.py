# Git Log to TIKZ

This is an updated Python rewrite of Michael Hauspie's original [git-log-to-tikz.rb][]. This version
uses Jinja2 for templating logic, and supports a handful of arguments. Graphs may also be easily
restyled using `tikzset` in the TeX document which includes figures generated by this code. An
example invocation is available in the `Makefile`, as well as below.

### Examples

```
git-log-to-tikz.py master feature-branch > repository-snapshot.tex
```

This will store as a `tikzpicture` the state of the two branches, `master` and `feature-branch` in
from the current directory, using `master` as the primary branch. All commits going back to the root
will be included, and commits in parallel branches will be interlaced according to their chronology.
Any number of branches may be inspected.

```
git-log-to-tikz.py --maketest master feature-branch > repository-snapshot.json
```

This will capture the state of the two branches and store them as a JSON object which
`git-log-to-tikz.py` is capable of reading, and rendering later into a TIKZ picture. This feature
was originally envisioned for easy testing, but may also be used for hand-preparing a specification
for a figure, without having to actually create a matching repository. The snapshot may then be used
instead of the current working directory as follows.

```
git-log-to-tikz.py --testfile repository-snapshot.json master feature-branch
```

Furthermore, one may capture (using `--maketest`) as many branches as desired, and then use any
subset of those branches with `--testfile`.

### Disclaimer

This software was written as a handy tool to simplify figure creation, and is very likely to fail
under certain circumstances. If you encounter such a circumstance, please see the [issues
page][issues] and report the omission. Pull requests are welcome!

[git-log-to-tikz.rb]: https://gist.github.com/hauspie/2397222
[issues]: https://github.com/alexander-bauer/git-log-to-tikz.py/issues
