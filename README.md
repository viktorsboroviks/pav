# PAV (PlantUML Ascetic Viewer)

PAV is a small offline GUI wrapper around PlantUML.
It allows you to see the resulting UML while editing the text file in your favourite editor.
PAV constantly watches your text file for changes and as soon as one is detected PAV generates and displays resulting UML diagram.

## Fast start

1.  In PAV menu select text file or launch PAV from console:
    $ pav [your_text_file]
2.  Make changes to the same file in any text editor and save.
3.  PAV will detect changes in file and will redraw UML.
4.  When done - save UML as .svg or .png.

## How to install and run?
1.  Install Python3 and PyQt5.
2.  Linux: From PAV project directory run:
    $ ./bin/pav
    Windows: Launch main.pyw

## Example

1.  From PAV project directory run:
    $ ./bin/pav example.txt
2.  Edit example.txt in any text editor and save.

## Author

**Victor Borovik**

## License

MIT

## Based on

PlantUML:
http://plantuml.com/
