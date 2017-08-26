"""UI"""

import os
import sys
import pavcore
from PyQt5 import QtCore, QtSvg, QtWidgets


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
    """View provides GUI and communicates with Controlled."""

    def __init__(self, controller, file_path=None):
        """Init application with its main window, connect the Controller.

        Arguments:
        controller - instance of pavcore.Controller
        file_path - absolute path to PlantUML text file to be processed at
                startup (optional, can later be selected from GUI)"""
        self._mw = _MainWindow()
        self._c = controller
        self._mw.sig_save_img_file.connect(self._c.save_img_file)
        self._mw.sig_set_txt_file.connect(self._c.set_txt_file)
        self._c.sig_img_generated.connect(self._mw.set_svg_img)
        self._c.sig_show_loading.connect(self._mw.show_loading)
        self._c.sig_set_status_msg.connect(self._mw.set_status_msg)
        self._startup_file_path = file_path

    def start(self):
        """Launch the View and the associated Controller.

        If startup file was provided at init - process it and display.
        Otherwise display the welcome message."""
        self._mw.show()
        self._c.start()
        if self._startup_file_path is not None:
            self._mw.load_img_from_txt(self._startup_file_path)
        else:
            self._mw.set_welcome_msg(HELP_MSG)


class _MainWindow(QtWidgets.QMainWindow):
    _img_file = None
    _txt_file = None
    _img_format = None

    """Signal to save image file.

        Arguments:
        img_format -    image file format ("svg" or "png")
        file_path -     path to the new image file
                        (if file exists it will be overwritten)"""
    sig_save_img_file = QtCore.pyqtSignal(str, str)

    """Signal to select text file for watching.

        Arguments:
        file_path -     path to the file"""
    sig_set_txt_file = QtCore.pyqtSignal(str)

    def __init__(self):
        super(_MainWindow, self).__init__()
        self._status_msg = None
        self._init_ui()
        self._init_menus()

    def load_img_from_txt(self, file_path):
        """Generate and displey UML diagram from PlantUML text file."""
        if not os.access(file_path, os.R_OK):
            self._txt_file = None
            self.set_status_msg('File not found: {0}'.format(file_path))
            return
        self._txt_file = file_path
        self.sig_set_txt_file.emit(self._txt_file)
        self.set_status_msg(str("Watching: {0}".format(self._txt_file)))

    def set_svg_img(self, byte_array):
        """Display SVG image from byte array."""
        self._view.set_svg_img(byte_array)

    def set_welcome_msg(self, msg):
        """Set welcome message. Message is not displayed by this function."""
        self._view.set_welcome_msg(msg)

    def show_loading(self, show):
        """Show/hide loading indicator.

        Arguments:
        show    -   True -> show loading indicator,
                    False -> hide loading indicator."""
        if show:
            self.statusBar().clearMessage()
        else:
            self.statusBar().showMessage(self._status_msg, 0)
        self._loading.setVisible(show)

    def set_status_msg(self, msg):
        self._status_msg = msg
        self.statusBar().showMessage(self._status_msg, 0)

    def _watch_txt(self):
        self._txt_file = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Watch selected text file for changes',
            self._txt_file)[0]
        self.load_img_from_txt(self._txt_file)

    def _save_img(self):
        if not self._img_file:
            self._save_img_as()
        else:
            self.sig_save_img_file.emit(self._img_format, self._img_file)

    def _save_img_as(self):
        self._img_file, self._img_format = \
            QtWidgets.QFileDialog.getSaveFileName(
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
        self.sig_save_img_file.emit(self._img_format, self._img_file)

    def _init_ui(self):
        self.setWindowTitle('%s %s' % (pavcore.NAME, pavcore.VERSION))
        self.statusBar()
        self.resize(500, 300)
        self._view = _GraphicsViewWidget()
        self.setCentralWidget(self._view)
        # Init Loading bar
        self._loading = QtWidgets.QProgressBar()
        self._loading.setTextVisible(False)
        self.statusBar().addWidget(self._loading)
        self._loading.setMaximumWidth(150)
        self._loading.setValue(0)
        self._loading.setMaximum(0)
        self._loading.setMinimum(0)
        self._loading.setVisible(False)

    def _init_menus(self):
        # Setup actions
        action_watch_txt = QtWidgets.QAction('&Watch text file', self)
        action_watch_txt.setShortcut('Ctrl+w')
        action_watch_txt.triggered.connect(self._watch_txt)

        action_save_img = QtWidgets.QAction('&Save image', self)
        action_save_img.setShortcut('Ctrl+s')
        action_save_img.triggered.connect(self._save_img)

        action_save_img_as = QtWidgets.QAction('&Save image as...', self)
        action_save_img_as.setShortcut('Ctrl+Shift+s')
        action_save_img_as.triggered.connect(self._save_img_as)

        # Setup menu bar
        menu_bar = self.menuBar()
        menu_file = menu_bar.addMenu('&File')
        menu_file.addAction(action_watch_txt)
        menu_file.addSeparator()
        menu_file.addAction(action_save_img)
        menu_file.addAction(action_save_img_as)


class _GraphicsViewWidget(QtWidgets.QGraphicsView):
    """Main graphical widget."""
    _item_help_msg = None

    def __init__(self):
        self._scene = QtWidgets.QGraphicsScene()
        super(_GraphicsViewWidget, self).__init__(self._scene)
        # Enable image movement with the mouse
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self._image = QtSvg.QGraphicsSvgItem()
        self._image_renderer = QtSvg.QSvgRenderer()
        self._scene.addItem(self._image)

    def set_welcome_msg(self, msg):
        """Display welcome message."""
        self._item_help_msg = QtWidgets.QGraphicsTextItem(msg)
        self._scene.addItem(self._item_help_msg)

    def remove_welcome_msg(self):
        """No longer display welcome message."""
        self._scene.removeItem(self._item_help_msg)
        self._item_help_msg = None

    def set_svg_img(self, byte_array):
        """Display SVG image from byte array."""
        if self._item_help_msg:
            # Remove text item from scene
            self.remove_welcome_msg()
            # Init image item on scene
        self._image_renderer.load(byte_array)
        # Change scene size to image size
        self._scene.setSceneRect(
            0,
            0,
            self._image_renderer.defaultSize().width(),
            self._image_renderer.defaultSize().height())
        self._image.setSharedRenderer(self._image_renderer)

    def wheelEvent(self, event):
        """Enable mouse wheel zoom."""
        scale = event.angleDelta().y() / 1000.0
        if scale:
            scale += 1.0
            self.scale(scale, scale)
