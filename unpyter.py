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
                         'version': sys.version.split()[0] } },
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
            source = cells[-1]["source"]
            while source[-1].strip() == "":
                del source[-1]
            if source[-1][-1] == "\n":
                source[-1] = source[-1][:-1]
        except IndexError:
            pass

    def is_empty(line):
        return line == "" or re.match("^# *$", line)

    def implicit_codecell(line):
        if celltype == "code":
            return False
        l_0 = line.strip()[:1]
        if l_0 and l_0 != "#":
            return True
        return False

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
    regex_newcell = re.compile("^ *###+ *([a-z]+) +cell *###+ *$")
    for line in py:
        if regex_newcell.match(line):
            remove_trailing_newlines(cells)
            celltype = regex_newcell.match(line).groups()[0]
            cells.append(new_cell(celltype))
        elif implicit_codecell(line):
            remove_trailing_newlines(cells)
            celltype = "code"
            cells.append(new_cell("code"))
            cells[-1]["source"].append(line+"\n")
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
    usage = "Usage: unpyter [--help] [FILE]"
    if "-h" in sys.argv or "--help" in sys.argv:
        print(usage)
        exit(0)
    elif len(sys.argv) > 2:
        print("Only one FILE may be specified", file=sys.stderr)
        exit(1)

    infilename = "-" if len(sys.argv) == 1 else sys.argv[1]
    if infilename == "-":
        doc = sys.stdin.read()
    else:
        with open(infilename) as f:
            doc = f.read()
    if doc.startswith("{"):
        print(ipynb_to_py(doc))
    elif doc.startswith("#!/usr/bin/env python3"):
        print(py_to_ipynb(doc))
    else:
        print("Input format not recognized. Input files must either "
              "start with an\nopening curly brace if they are in ipynb "
              "format, or with a shebang\nof '#!/usr/bin/env python3'. "
              "Other file formats and shebangs are\nnot supported.")
        exit(1)
