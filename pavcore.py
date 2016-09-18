"""Provides services for the UI"""

import threading
import subprocess

from PyQt4 import QtCore


NAME = 'PAV (PlantUML Ascetic Viewer)'
VERSION = '1.0.1'


class Controller(object):
    """Provide services for the View.

    Controller watches selected text file for changes. When file is changed
    (edited in any text redactor and saved) Controller generates UML
    diagram from the file's content using PlantUML. Controller provides the
    diagram to the View and requests for it to be displayed."""

    def __init__(self, plantuml_path):
        """Initialize Controller, but do not start it"""
        self._fw = _FileWatcher()
        self._ig = _ImageGenerator(plantuml_path)
        self._fw.set_cb_file_changed(self._updateImg)
        self.show_loading = self._ig.show_loading

    def start(self):
        """Start Controller.

        Call once after Controller is created."""
        self._ig.start()

    def set_text_file(self, file_path):
        """Set PlantUML text file to be watched for changes.

        1)  Controller reads the PlantUML text file provided under
            file_path, generates UML diagram from it and request the
            View to display the result.
        2)  file_path is remembered. After Controller is started with
            start() -> the file will be watched for changes. Change in
            the file will result in generating UML diagram from file
            content and requesting the View to display it."""
        self._fw.set_file(file_path)
        self._text_file_path = file_path
        self._updateImg()

    def save_img_file(self, img_format, file_path):
        """Generate UML diagram and save it as an image file.

        Use text from previously provided text file to generate image file.
        Arguments:
        img_format -    image file format ("svg" or "png")
        file_path -     path to the new image file
                        (if file exists it will be overwritten)"""
        img_bytes = self._ig.run_plantuml(img_format, self._img_text)
        with open(file_path, 'wb') as f:
            f.write(img_bytes)

    def set_cb_img_generated(self, callback):
        """Set function to be called when the image was generated.

        The callback must take SVG byte array with the resulting image."""
        self._ig.set_cb_img_generated(callback)

    def _updateImg(self):
        with open(self._text_file_path) as f:
            self._img_text = f.read()
        self._ig.request_img_gen(self._img_text)


class _FileWatcher(QtCore.QFileSystemWatcher):
    """Watch file on the filesystem for change."""
    _file_path = None

    def set_cb_file_changed(self, callback):
        """Set function to be called when file change was detected.

        The callback takes no arguments."""
        self.fileChanged.connect(callback)

    def set_file(self, file_path):
        """Set file to be watched for changes."""
        if self._file_path != file_path:
            if self._file_path:
                self.removePath(self._file_path)
            self._file_path = file_path
            self.addPath(file_path)


# QThread is used for pyqtSignal support for comunication with the View
# through the Controller.
class _ImageGenerator(QtCore.QThread):
    """Generate UML diagram images from text using PlantUML.

    Runs as a separate generator thread, so only one image generation request
    is processed at a time."""

    show_loading = QtCore.pyqtSignal(bool)
    """Signal to show loading message.

    show_loading(True) - show loading message.
    show_loading(False) - do not show loading message."""

    def __init__(self, plantuml_path):
        """Initialize image generator, but do not run it.

        Arguments:
        plantuml_path - absolute path to plantum .jar file."""
        super(_ImageGenerator, self).__init__()
        self._plantuml_path = plantuml_path
        self._e = threading.Event()

    def run(self):
        """Daemon thread. Wait for image generation requests and process them.

        Indefinitely wait for image generation request. When request received -
        generate image.
        Only one request can be processed at a time.
        Emit signal to display loading message when generation starts.
        Emit signal to stop displying loading message when generation stops."""
        while(True):
            self._e.wait()
            self._e.clear()
            self.show_loading.emit(True)
            byteArray = self.run_plantuml('svg', self._img_text)
            self._cb_img_generated(byteArray)
            self.show_loading.emit(False)

    def request_img_gen(self, img_text):
        """Send request for generate UML diagram image from text.

        ImageGenerator can generate only one diagram at a time. Request is
        processed as soon as image is generated.
        Requests do not stack.
        Arguments:
        img_text -  text in PlantUML format"""
        self._img_text = img_text.encode()
        self._e.set()

    def run_plantuml(self, img_format, img_text):
        """Run PlantUML.

        This method overrides request mechanism of the ImageGenerator and runs
        PlantUML directly."""
        format_arg = '-t' + img_format
        command = ['java', '-splash:no', '-jar', self._plantuml_path,
                   '-pipe', format_arg]
        proc = subprocess.Popen(command, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        proc.stdin.write(self._img_text)
        self._img_bytes = proc.communicate()[0]
        return self._img_bytes

    def set_cb_img_generated(self, callback):
        """Set function to be called when image was generated.

        Pass generated SVG as a byte array to Controller."""
        self._cb_img_generated = callback
