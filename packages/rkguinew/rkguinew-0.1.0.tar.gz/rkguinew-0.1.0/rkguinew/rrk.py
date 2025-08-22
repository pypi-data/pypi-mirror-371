from PyQt5.QtWidgets import QComboBox, QTreeWidget, QTreeWidgetItem

class Combobox(QComboBox):
    def __init__(self, parent, x=0, y=0, w=120, h=30, values=None):
        super().__init__(parent)
        self.setGeometry(x, y, w, h)
        if values:
            self.addItems(values)
        self.show()

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
