from PyQt6.QtWidgets import QListView, QWidget, QAbstractItemView, QVBoxLayout
from PyQt6.QtGui import QValidator, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView

import markdown

class QList(QListView):
    def __init__(self, flow=QListView.Flow.TopToBottom, parent=None):
        super().__init__(parent)
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.setFlow(flow)

        #F Enable item selection
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # Enable wrapping (useful when the flow is LeftToRight)
        if flow == QListView.Flow.LeftToRight:
            self.setWrapping(True)

         # Set size to adjust dynamically based on content
        self.setSizeAdjustPolicy(QAbstractItemView.SizeAdjustPolicy.AdjustToContents)

        # Disable scrollbars for a wrapping effect
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def addItem(self, item):
        new_item = QStandardItem(item)
        self.model.appendRow(new_item)
        self.setSizeAdjustPolicy(QAbstractItemView.SizeAdjustPolicy.AdjustToContents)

    def addItems(self, items):
        for item in items:
            new_item = QStandardItem(item)
            self.model.appendRow(new_item)
        self.setSizeAdjustPolicy(QAbstractItemView.SizeAdjustPolicy.AdjustToContents)

    def DeleteItems(self, indexes):
         # Remove the selected item from the model
        for index in indexes:
            self.model.removeRow(index.row())

        # Resize the list view after deletion
        self.setSizeAdjustPolicy(QAbstractItemView.SizeAdjustPolicy.AdjustToContents)

    def GetItems(self):
        items = []
        for row in range(self.model.rowCount()):  # Iterate through all rows in the model
            item = self.model.item(row)  # Get the item at the specified row
            items.append(item.text())  # Retrieve the item's text
        return items

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            if self.selectedIndexes():
                self.DeleteItems(self.selectedIndexes())
            else:
                super().keyPressEvent(event)


class QInt64Validator(QValidator):
    def __init__(self, bottom=-9223372036854775808, top=9223372036854775807, parent=None):
        super().__init__(parent)
        self.min_value = bottom  # Minimum 64-bit integer value
        self.max_value = top   # Maximum 64-bit integer value

    def validate(self, input_str, pos):
        # Check if the input is empty
        if input_str == "":
            return (QValidator.State.Intermediate, input_str, pos)

        # Check if input is a valid integer
        try:
            value = int(input_str)
        except ValueError:
            return (QValidator.State.Invalid, input_str, pos)

        # Check if the integer is within the specified range
        if self.min_value <= value <= self.max_value:
            return (QValidator.State.Acceptable, input_str, pos)
        else:
            return (QValidator.State.Invalid, input_str, pos)

    def bottom(self):
        return self.min_value

    def top(self):
        return self.max_value

class MarkdownViewer(QWidget):
    def __init__(self, markdown_text):
        super().__init__()

        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_text)

        # Set up the web view
        self.web_view = QWebEngineView()

        # Add custom CSS styling to improve appearance
        html_with_style = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; margin: 20px; }}
                    h1, h2, h3 {{ color: #2c3e50; }}
                    p {{ line-height: 1.6; }}
                    code {{ background-color: #f3f4f5; padding: 2px 4px; border-radius: 4px; }}
                </style>
            </head>
            <body>{html_content}</body>
        </html>
        """

        self.web_view.setHtml(html_with_style)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.web_view)
        self.setLayout(layout)
