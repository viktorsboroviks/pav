import pavcore
import pavui
import argparse
import sys
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate UML diagrams from PlantUML text files.')
    parser.add_argument(
        'text_file', default=None, nargs='?', help='PlantUML text file')
    args = parser.parse_args()

    project_path = os.path.dirname(__file__)
    plantuml_path = str("%s/plantuml.jar" % project_path)

    c = pavcore.Controller(plantuml_path)
    v = pavui.View(c, os.path.abspath(args.text_file))
    v.start()
