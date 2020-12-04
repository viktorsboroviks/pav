# PAV (PlantUML Ascetic Viewer)

PAV is a small offline GUI wrapper around PlantUML.
It allows you to see the resulting UML while editing the text file in your favourite editor.
PAV constantly watches your text file for changes and as soon as one is detected PAV generates and displays resulting UML diagram.

## How does it work?

1.  In PAV menu select text file or launch PAV from console:
```
pav [plantuml_file]
```
2.  In parallel make changes to the same file in any text editor and save.
3.  PAV will automatically detect file changes and will redraw UML.
4.  When done - save UML as .svg or .png.

## How to setup?

1. Download latest plantuml
2. Setup python virtual environment
3. Install requirements.txt
4. Run

```
wget http://sourceforge.net/projects/plantuml/files/plantuml.jar/download -O plantuml.jar
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## How to run?

1. Activate python virtual environment
2. Run

```
source venv/bin/activate
bin/pav example.plantuml
bin/pav example_mindmap.plantuml
```

## License

MIT

## Links

[Latest version of PlanUML][https://plantuml.com/download]
