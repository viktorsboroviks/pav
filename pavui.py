"""UI"""

import pavcore
import sys
import os
from PyQt4 import QtCore, QtGui, QtSvg


HELP_MSG = """\
Quick start:
    1) Select text file to be watched (Ctrl + w)
    2) Open the same text file in your favourite text editor
    3) In text editor write PlantUML code to file and save it
    4) PAV will detect file change and display the resulting UML diagram
    5) Repeat from step (3)
    ...
    6) Save image with (Ctrl + s)

PlantUML file example:\t<pav_directory>/example.txt
PlantUML reference:\thttp://plantuml.com/
"""


class View(object):
    def __init__(self, controller, file_path=None):
        """Init application with its main window, connect the Controller.

        Arguments:
        controller - instance of pavcore.Controller
        file_path - PlantUML text file to be processed at startup
                    (optional, can later be selected from GUI)"""
        self._app = QtGui.QApplication(sys.argv)
        self._mw = _MainWindow()
        self._c = controller
        self._mw.set_cb_save_img_file(self._c.save_img_file)
        self._mw.set_cb_set_text_file(self._c.set_text_file)
        self._c.set_cb_img_generated(self._mw.set_svg_img)
        self._c.show_loading.connect(self._mw.show_loading)
        self._startup_file_path = file_path

    def start(self):
        """Launch the View and the associated Controller.

        If startup file was provided at init - process it and display.
        Otherwise display the welcome message."""
        self._mw.show()
        self._c.start()
        if self._startup_file_path is not None:
            self._mw.load_img_from_text(
                os.path.abspath(self._startup_file_path))
        else:
            self._mw.set_welcome_msg(HELP_MSG)
        sys.exit(self._app.exec_())


class _MainWindow(QtGui.QMainWindow):
    _img_file = None
    _text_file = None
    _img_format = None

    def __init__(self):
        super(_MainWindow, self).__init__()
        self._init_ui()
        self._init_menus()

    def load_img_from_text(self, file_path):
        """Generate and displey UML diagram from PlantUML text file."""
        self._text_file = file_path
        self._cb_set_text_file(self._text_file)
        self._status_msg = str("Watching: %s" % self._text_file)
        self.statusBar().showMessage(self._status_msg, 0)

    def set_svg_img(self, byteArray):
        """Display SVG image from byteArray."""
        self._view.set_svg_img(byteArray)

    def set_welcome_msg(self, msg):
        """Set welcome message. Message is not displayed by this function."""
        self._view.set_welcome_msg(msg)

    def set_cb_save_img_file(self, callback):
        """Set function to be called when user attempts to save image."""
        self._cb_save_img_file = callback

    def set_cb_set_text_file(self, callback):
        """Set function to be called when user attempts to select text file."""
        self._cb_set_text_file = callback

    def show_loading(self, boolean):
        """Show/hide loading indicator.

        Arguments:
        boolean -   True -> show loading indicator,
                    False -> hide loading indicator."""
        if boolean:
            self.statusBar().clearMessage()
        else:
            self.statusBar().showMessage(self._status_msg, 0)
        self._loading.setVisible(boolean)

    def _watch_text(self):
        self._text_file = QtGui.QFileDialog.getOpenFileName(
            self,
            'Watch selected text file for changes',
            self._text_file)
        self.load_img_from_text(self._text_file)

    def _save_img(self):
        if not self._img_file:
            self._save_img_as()
        else:
            self._cb_save_img_file(self._img_format, self._img_file)

    def _save_img_as(self):
        self._img_file, self._img_format = \
            QtGui.QFileDialog.getSaveFileNameAndFilter(
                self,
                'Save file as...',
                self._img_file,
                'Scalable Vector Graphics (*.svg);;\
                    Portable Network Graphics (*.png)')
        if 'svg' in self._img_format:
            self._img_format = 'svg'
        else:
            self._img_format = 'png'
        if not self._img_file.lower().endswith(self._img_format):
            self._img_file = self._img_file + '.' + self._img_format
        self._cb_save_img_file(self._img_format, self._img_file)

    def _init_ui(self):
        self.setWindowTitle('%s %s' % (pavcore.NAME, pavcore.VERSION))
        self.statusBar()
        self.resize(500, 300)
        self._view = _GraphicsViewWidget()
        self.setCentralWidget(self._view)
        # Init Loading bar
        self._loading = QtGui.QProgressBar()
        self._loading.setTextVisible(False)
        self.statusBar().addWidget(self._loading)
        self._loading.setMaximumWidth(150)
        self._loading.setValue(0)
        self._loading.setMaximum(0)
        self._loading.setMinimum(0)
        self._loading.setVisible(False)

    def _init_menus(self):
        # Setup actions
        action_watch_text = QtGui.QAction('&Watch text file', self)
        action_watch_text.setShortcut('Ctrl+w')
        action_watch_text.triggered.connect(self._watch_text)

        action_save_img = QtGui.QAction('&Save image', self)
        action_save_img.setShortcut('Ctrl+s')
        action_save_img.triggered.connect(self._save_img)

        action_save_img_as = QtGui.QAction('&Save image as...', self)
        action_save_img_as.setShortcut('Ctrl+Shift+s')
        action_save_img_as.triggered.connect(self._save_img_as)

        # Setup menu bar
        menu_bar = self.menuBar()
        menu_file = menu_bar.addMenu('&File')
        menu_file.addAction(action_watch_text)
        menu_file.addSeparator()
        menu_file.addAction(action_save_img)
        menu_file.addAction(action_save_img_as)


class _GraphicsViewWidget(QtGui.QGraphicsView):
    """Main graphical widget."""
    _helpMsgItem = None

    def __init__(self):
        self._scene = QtGui.QGraphicsScene()
        super(_GraphicsViewWidget, self).__init__(self._scene)
        # Enable image movement with the mouse
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self._image = QtSvg.QGraphicsSvgItem()
        self._image_renderer = QtSvg.QSvgRenderer()
        self._scene.addItem(self._image)

    def set_welcome_msg(self, msg):
        """Display welcome message."""
        self._helpMsgItem = QtGui.QGraphicsTextItem(msg)
        self._scene.addItem(self._helpMsgItem)

    def remove_welcome_msg(self):
        """No longer display welcome message."""
        self._scene.removeItem(self._helpMsgItem)
        self._helpMsgItem = None

    def set_svg_img(self, byteArray):
        """Display SVG image from byteArray."""
        if self._helpMsgItem:
            # Remove text item from scene
            self.remove_welcome_msg()
            # Init image item on scene
        self._image_renderer.load(QtCore.QByteArray(byteArray))
        # Change scene size to image size
        self._scene.setSceneRect(
            0,
            0,
            self._image_renderer.defaultSize().width(),
            self._image_renderer.defaultSize().height())
        self._image.setSharedRenderer(self._image_renderer)

    def wheelEvent(self, event):
        # Enable mouse wheel zoom
        scale = event.delta()/100
        if scale < 0:
            scale = -1 / scale
        self.scale(scale, scale)
