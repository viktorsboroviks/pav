import pavcore
import pavui
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate UML diagrams from PlantUML text files.')
    parser.add_argument(
        'text_file', default=None, nargs='?', help='PlantUML text file')
    args = parser.parse_args()

    c = pavcore.Controller()
    v = pavui.View(c, args.text_file)
    v.start()
