git-tags
========

> A git extension to print a list of tags with detailed information.

tl;dr
-----

```bash
$ git tags
v0.0.1 590b240 2021-05-21 initial release
v0.0.3 920ac2b 2021-07-05 bugfix: allow multiple highlights on one line
```

```bash
$ git tags --count 1
v0.0.1 590b240 2021-05-21 initial release
```

Usage
-----

    git-tags [-h] [-v] [-V]

    options:
    -h, --help     show this help message and exit
    -v, --version  show program's version number and exit
    -V, --verbose  print git command

    Remaining options are forwarded to git. See: git help for-each-ref.

Status
------

**Pre-Alpha**

A kinda buggy personal project.

Install
-------

```bash
git clone https://github.com/alissa-huskey/git-tags.git && cd git-tags
pip install dist/*.whl
```

Meta
----

* Github: [alissa-huskey/git-tags/][github]
* License: MIT

[github]: https://github.com/alissa-huskey/git-tags
