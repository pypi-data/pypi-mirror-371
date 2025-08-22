from PyQt5.QtWidgets import (
    QComboBox, QTreeWidget, QTreeWidgetItem, QProgressBar,
    QTabWidget, QWidget, QColorDialog, QFontDialog, QMessageBox
)
from PyQt5.QtCore import Qt

# ------------------------------
class Combobox(QComboBox):
    def __init__(self, parent, x=0, y=0, w=120, h=30, values=None):
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        if values:
            self.addItems(values)
        self.show()

    def get(self):
        return self.currentText()

    def set(self, value):
        index = self.findText(value)
        if index >= 0:
            self.setCurrentIndex(index)

    def add_values(self, values):
        self.addItems(values)

# ------------------------------
class Treeview(QTreeWidget):
    def __init__(self, parent, x=0, y=0, w=200, h=200, headers=None):
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        if headers:
            self.setHeaderLabels(headers)
        self.show()

    def insert(self, parent_item, text):
        item = QTreeWidgetItem([text])
        if parent_item:
            parent_item.addChild(item)
        else:
            self.addTopLevelItem(item)
        return item

    def clear_items(self):
        self.clear()

    def get_selected(self):
        items = self.selectedItems()
        if items:
            return items[0].text(0)
        return None

# ------------------------------
class ProgressBar(QProgressBar):
    def __init__(self, parent, x=0, y=0, w=200, h=20, minimum=0, maximum=100):
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        self.setRange(minimum, maximum)
        self.setValue(minimum)
        self.show()

    def set_value(self, value):
        self.setValue(value)

    def get_value(self):
        return self.value()

# ------------------------------
class TabControl(QTabWidget):
    def __init__(self, parent, x=0, y=0, w=300, h=200):
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        self.show()

    def add_tab(self, widget, title):
        self.addTab(widget, title)

# ------------------------------
class ColorPicker:
    @staticmethod
    def get_color(initial=None):
        color = QColorDialog.getColor(initial)
        if color.isValid():
            return color.name()
        return None

# ------------------------------
class FontPicker:
    @staticmethod
    def get_font():
        font, ok = QFontDialog.getFont()
        if ok:
            return font
        return None

# ------------------------------
class MessageBox:
    @staticmethod
    def show_info(title, text):
        QMessageBox.information(None, title, text)

    @staticmethod
    def show_warning(title, text):
        QMessageBox.warning(None, title, text)

    @staticmethod
    def show_error(title, text):
        QMessageBox.critical(None, title, text)
