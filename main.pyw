"""Main file. Does argument parsing and launches the program."""

import os
import sys
import argparse
import platform
import pavcore
import pavui
from PyQt5 import QtWidgets


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate UML diagrams from PlantUML text files.')
    parser.add_argument(
        'txt_file', default=None, nargs='?', help='PlantUML text file')
    args = parser.parse_args()

    if platform.system() is 'Windows':
        java_exe = 'java.exe'
    else:
        java_exe = 'java'

    project_path = os.path.dirname(__file__)
    plantuml_path = os.path.join(project_path, "plantuml.jar")
    if (args.txt_file):
        txt_file_path = os.path.abspath(args.txt_file)
    else:
        txt_file_path = None

    app = QtWidgets.QApplication(sys.argv)
    c = pavcore.Controller(java_exe, plantuml_path)
    v = pavui.View(c, txt_file_path)
    v.start()
    sys.exit(app.exec_())
