"""Main file. Does argument parsing and launches the program."""

import os
import sys
import argparse
import pavcore
import pavui
from PyQt5 import QtWidgets


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate UML diagrams from PlantUML text files.')
    parser.add_argument(
        'txt_file', default=None, nargs='?', help='PlantUML text file')
    args = parser.parse_args()

    project_path = os.path.dirname(__file__)
    plantuml_path = os.path.join(project_path, "plantuml.jar")
    txt_file_path = args.txt_file
    if (txt_file_path):
        txt_file_path = os.path.abspath(args.txt_file)

    app = QtWidgets.QApplication(sys.argv)
    c = pavcore.Controller(plantuml_path)
    v = pavui.View(c, txt_file_path)
    v.start()
    sys.exit(app.exec_())
