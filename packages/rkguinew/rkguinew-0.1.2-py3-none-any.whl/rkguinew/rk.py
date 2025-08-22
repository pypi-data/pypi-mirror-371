from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QCheckBox,
    QRadioButton, QFrame, QScrollBar, QSlider, QSpinBox, QListWidget,
    QComboBox, QSplitter, QTextEdit, QMessageBox, QDateTimeEdit
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl
import sys

# ------------------------------
# Глобальный QApplication
_app = None
def _ensure_app():
    global _app
    if _app is None:
        _app = QApplication(sys.argv)
    return _app

# ------------------------------
class Window(QWidget):
    def __init__(self, title="Window", width=400, height=300):
        _ensure_app()
        super().__init__()
        self.setWindowTitle(title)
        self.resize(width, height)
        self.show()

    def mainloop(self):
        app = _ensure_app()
        app.exec_()

# ------------------------------
class LabelFrame(QFrame):
    def __init__(self, parent, text="", x=0, y=0, w=100, h=30):
        _ensure_app()
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setGeometry(x, y, w, h)
        self.show()
        if text:
            label = QLabel(text, self)
            label.move(5,0)

class Toplevel(Window):
    def __init__(self, title="Toplevel", width=300, height=200):
        _ensure_app()
        super().__init__(title, width, height)

class PanedWindow(QSplitter):
    def __init__(self, parent, x=0, y=0, w=200, h=200, orientation=Qt.Horizontal):
        _ensure_app()
        super().__init__(orientation, parent)
        self.setGeometry(x, y, w, h)
        self.show()

class Radiobutton(QRadioButton):
    def __init__(self, parent, text="", x=0, y=0, command=None):
        _ensure_app()
        super().__init__(text, parent)
        self.move(x, y)
        if command:
            self.toggled.connect(command)
        self.show()

class Checkbutton(QCheckBox):
    def __init__(self, parent, text="", x=0, y=0, command=None):
        _ensure_app()
        super().__init__(text, parent)
        self.move(x, y)
        if command:
            self.stateChanged.connect(lambda _: command())
        self.show()

class Button(QPushButton):
    def __init__(self, parent, text="", x=0, y=0, w=100, h=30, command=None):
        _ensure_app()
        super().__init__(text, parent)
        self.setGeometry(x, y, w, h)
        if command:
            self.clicked.connect(command)
        self.show()

class Entry(QLineEdit):
    def __init__(self, parent, x=0, y=0, w=100, h=30):
        _ensure_app()
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        self.show()
    def get(self):
        return self.text()
    def set(self, text):
        self.setText(text)

class Scrollbar(QScrollBar):
    def __init__(self, parent, x=0, y=0, w=100, h=20, orientation=Qt.Vertical):
        _ensure_app()
        super().__init__(orientation, parent)
        self.setGeometry(x, y, w, h)
        self.show()

class Slider(QSlider):
    def __init__(self, parent, x=0, y=0, w=100, h=20, orientation=Qt.Horizontal):
        _ensure_app()
        super().__init__(orientation, parent)
        self.setGeometry(x, y, w, h)
        self.show()

class Spinbox(QSpinBox):
    def __init__(self, parent, x=0, y=0, w=100, h=30, minimum=0, maximum=100):
        _ensure_app()
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        self.setRange(minimum, maximum)
        self.show()

class Listbox(QListWidget):
    def __init__(self, parent, x=0, y=0, w=100, h=100):
        _ensure_app()
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        self.show()

class OptionMenu(QComboBox):
    def __init__(self, parent, x=0, y=0, w=120, h=30, values=None):
        _ensure_app()
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        if values:
            self.addItems(values)
        self.show()

class Canvas(QFrame):
    def __init__(self, parent, x=0, y=0, w=200, h=200):
        _ensure_app()
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        self.setStyleSheet("background-color: white;")
        self.show()

class HTMLView(QTextEdit):
    def __init__(self, parent, x=0, y=0, w=300, h=200):
        _ensure_app()
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        self.setReadOnly(True)
        self.show()

class WebView(QWebEngineView):
    def __init__(self, parent, x=0, y=0, w=400, h=300):
        _ensure_app()
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        self.show()

class MenuButton(QPushButton):
    def __init__(self, parent, text="", menu=None, x=0, y=0, w=100, h=30):
        _ensure_app()
        super().__init__(text, parent)
        self.setGeometry(x, y, w, h)
        if menu:
            self.setMenu(menu)
        self.show()

class Message(QLabel):
    def __init__(self, parent, text="", x=0, y=0, w=200, h=50):
        _ensure_app()
        super().__init__(text, parent)
        self.setGeometry(x, y, w, h)
        self.show()

class Dialogs:
    @staticmethod
    def show_info(title, text):
        _ensure_app()
        QMessageBox.information(None, title, text)

class DateTime(QDateTimeEdit):
    def __init__(self, parent, x=0, y=0, w=150, h=30):
        _ensure_app()
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        self.show()

class Time(QDateTimeEdit):
    def __init__(self, parent, x=0, y=0, w=150, h=30):
        _ensure_app()
        super().__init__(parent)
        self.setDisplayFormat("HH:mm:ss")
        self.setGeometry(x, y, w, h)
        self.show()

# ------------------------------
# Media Widgets
class ImageView(QLabel):
    def __init__(self, parent, x=0, y=0, w=200, h=200, image_path=None):
        _ensure_app()
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        self.setStyleSheet("background-color: white;")
        if image_path:
            pixmap = QPixmap(image_path)
            self.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio))
        self.show()

    def set_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.setPixmap(pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio))

class VideoPlayer(QVideoWidget):
    def __init__(self, parent, x=0, y=0, w=400, h=300, video_path=None):
        _ensure_app()
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        self.show()
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self)
        if video_path:
            self.set_video(video_path)

    def set_video(self, video_path):
        url = QUrl.fromLocalFile(video_path)
        self.player.setMedia(QMediaContent(url))
        self.player.play()

class AudioPlayer:
    def __init__(self, audio_path=None):
        _ensure_app()
        self.player = QMediaPlayer()
        if audio_path:
            self.set_audio(audio_path)

    def set_audio(self, audio_path):
        url = QUrl.fromLocalFile(audio_path)
        self.player.setMedia(QMediaContent(url))

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()
