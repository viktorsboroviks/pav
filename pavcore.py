"""Provides services for the UI"""

import subprocess
from PyQt5 import QtCore


NAME = 'PAV (PlantUML Ascetic Viewer)'
VERSION = '1.0.3'

# TODO: Fix image autoupdate
# TODO: Implement correct MVC structure
# TODO: Add config file for cross-platform support


class Controller(object):
    """Provide services for the View.

    Controller watches selected text file for changes. When file is changed
    (edited in any text redactor and saved) Controller generates UML
    diagram from the file's content using PlantUML. Controller provides the
    diagram to the View and requests for it to be displayed."""

    def __init__(self, plantuml_path):
        """Initialize Controller, but do not start it"""
        self._txt_file_path = None
        self._img_txt = None
        self._fw = _FileWatcher()
        self._fw.fileChanged.connect(self._update_img)
        self._ig = _ImageGenerator(plantuml_path)
        self.sig_img_generated = self._ig.sig_img_generated
        self.sig_show_loading = self._ig.sig_show_loading

    def start(self):
        """Start Controller.

        Call once after Controller is created."""
        self._ig.start()

    def set_txt_file(self, file_path):
        """Set PlantUML text file to be watched for changes.

        1)  Controller reads the PlantUML text file provided under
            file_path, generates UML diagram from it and request the
            View to display the result.
        2)  file_path is remembered. After Controller is started with
            start() -> the file will be watched for changes. Change in
            the file will result in generating UML diagram from file
            content and requesting the View to display it."""
        self._fw.set_file(file_path)
        self._txt_file_path = file_path
        self._update_img()

    def save_img_file(self, img_format, file_path):
        """Generate UML diagram and save it as an image file.

        Use text from previously provided text file to generate image file.
        Arguments:
        img_format -    image file format ("svg" or "png")
        file_path -     path to the new image file
                        (if file exists it will be overwritten)"""
        img_bytes = self._ig.run_plantuml(img_format, self._img_txt)
        with open(file_path, 'wb') as f:
            f.write(img_bytes)

    def _update_img(self):
        with open(self._txt_file_path) as f:
            self._img_txt = f.read()
        self._ig.request_img_gen(self._img_txt)


class _FileWatcher(QtCore.QFileSystemWatcher):
    """Watch file on the filesystem for change."""
    _file_path = None

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

    """Signal to show loading message.

    sig_show_loading(True) - show loading message.
    sig_show_loading(False) - do not show loading message."""
    sig_show_loading = QtCore.pyqtSignal(bool)

    """Signal for returning result of image generation."""
    sig_img_generated = QtCore.pyqtSignal(QtCore.QByteArray)

    def __init__(self, plantuml_path):
        """Initialize image generator, but do not run it.

        Arguments:
        plantuml_path - absolute path to plantum .jar file."""
        super(_ImageGenerator, self).__init__()
        self._img_txt = None
        self._plantuml_path = plantuml_path
        self._mutex_req_img_gen = QtCore.QMutex()
        self._mutex_req_img_gen.lock()

    def run(self):
        """Daemon thread. Wait for image generation requests and process them.

        Indefinitely wait for image generation request. When request received -
        generate image.
        Only one request can be processed at a time.
        Emit signal to display loading message when generation starts.
        Emit signal to stop displying loading message when generation stops."""
        while True:
            self._mutex_req_img_gen.lock()
            self.sig_show_loading.emit(True)
            byte_array = self.run_plantuml('svg', self._img_txt)
            self.sig_img_generated.emit(byte_array)
            self.sig_show_loading.emit(False)

    def request_img_gen(self, img_txt):
        """Send request for generate UML diagram image from text.

        ImageGenerator can generate only one diagram at a time. Request is
        processed as soon as image is generated.
        Requests do not stack.
        Arguments:
        img_txt -  text in PlantUML format"""
        self._img_txt = img_txt
        self._mutex_req_img_gen.unlock()

    def run_plantuml(self, img_format, img_txt):
        """Run PlantUML.

        This method overrides request mechanism of the ImageGenerator and runs
        PlantUML directly."""
        format_arg = '-t' + img_format
        command = ['java', '-splash:no', '-jar', self._plantuml_path,
                   '-pipe', format_arg]
        proc = subprocess.Popen(command, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        proc.stdin.write(img_txt.encode())
        img_bytes = proc.communicate()[0]
        return QtCore.QByteArray(img_bytes)
