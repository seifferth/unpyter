#!/usr/bin/env python3
# Copyright (C) 2018    Frank Seifferth
# SPDX-License-Identifier: GPL-3.0+
"""Convert between jupyter notebook and pure python code"""

import sys, os, json, re


def ipynb_to_py(doc: str) -> str:
    """Convert ipynb to pure python"""
    ipynb = json.loads(doc)
    py = ["#!/usr/bin/env python3"]
    for cell in ipynb["cells"]:
        py.append("\n\n")
        if cell["cell_type"] == "code":
            py.append("### code cell ###\n")
            py += cell["source"]
        else:
            py.append("### {} cell ###\n".format(cell["cell_type"]))
            for line in cell["source"]:
                py.append("# "+line)
    return "".join(py)


def py_to_ipynb(doc: str) -> str:
    """Convert pure python to ipynb"""
    def new_ipynb():
        return { "cells": [],
                 "metadata": {
                     'kernelspec': {
                         'display_name': 'Python 3',
                         'language': 'python',
                         'name': 'python3' },
                     'language_info': {
                         'codemirror_mode': {
                             'name': 'ipython',
                             'version': 3 },
                         'file_extension': '.py',
                         'mimetype': 'text/x-python',
                         'name': 'python',
                         'nbconvert_exporter': 'python',
                         'pygments_lexer': 'ipython3',
                         'version': '3.7.1' } },
                 "nbformat": 4, "nbformat_minor": 2 }

    def new_cell(celltype):
        if celltype == "code":
            return { "cell_type": "code",
                     "execution_count": None,
                     "metadata": {},
                     "outputs": [],
                     "source": [] }
        else:
            return { "cell_type": celltype,
                     "metadata": {},
                     "source": [] }

    def remove_trailing_newlines(cells):
        try:
            while cells[-1]["source"][-1] == "\n":
                del cells[-1]["source"][-1]
            if cells[-1]["source"][-1][-1] == "\n":
                cells[-1]["source"][-1] = cells[-1]["source"][-1][:-1]
        except IndexError:
            pass

    def is_empty(line):
        return line == "" or re.match("^# *$", line)

    py = doc.splitlines()
    ipynb = new_ipynb()
    cells = ipynb["cells"]
    # Remove shebang line (if any) and initial newlines
    if py[0].startswith("#!"):
        del py[0]
    if is_empty(py[0]):
        del py[0]
    # Process all cells
    celltype = "code"
    regex_newcell = re.compile("###+ *([a-z]+) +cell *###+")
    for line in py:
        if regex_newcell.match(line):
            remove_trailing_newlines(cells)
            celltype = regex_newcell.match(line).groups()[0]
            cells.append(new_cell(celltype))
        elif cells and not cells[-1]["source"] and is_empty(line):
            pass    # Remove initial newlines
        else:
            if not cells:   # Handle python code before cell specification
                cells.append(new_cell(celltype))
            if celltype == "code":
                cells[-1]["source"].append(line+"\n")
            else:
                cells[-1]["source"].append(re.sub("^# ?", "", line+"\n"))
    remove_trailing_newlines(cells)
    return json.dumps(ipynb, indent=1)


if __name__ == "__main__":
    usage = "Usage: unpyter <filename>"
    if len(sys.argv) == 2:
        if sys.argv[1] in ["-h", "--help"]:
            print(usage)
            exit(0)
        elif os.path.isfile(sys.argv[1]):
            with open(sys.argv[1]) as f:
                doc = f.read()
            if sys.argv[1].endswith(".ipynb"):
                print(ipynb_to_py(doc))
            elif sys.argv[1].endswith(".py"):
                print(py_to_ipynb(doc))
    else:
        print(usage)
        exit(1)
