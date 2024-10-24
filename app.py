import sys
from PyQt6.QtGui import QColor, QPalette, QAction, QIcon, QKeySequence, QIntValidator, QDoubleValidator, QValidator
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedLayout, QPushButton, QTabWidget, QLabel, QToolBar, QStatusBar, QCheckBox,
    QLineEdit, QComboBox, QListWidget, QMessageBox )

# internal
from mortality_table import GetTables

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Does this viager is profitable simulation ?")

        self.GetDatas()

        # Create the central widget for the window
        central_widget = QWidget()

        # Create the main vertical layout
        layout_main = QVBoxLayout()

        # Create the horizontal layout for info (purple section)
        layout_info = self.LayoutInfo(self)
        layout_main.addLayout(layout_info)  # Add layout_info to the main layout
        layout_main.addLayout(self.Test())

        # Create the tabs
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        tabs.setMovable(False)

        # Add tabs with different colors
        for color in ["red", "green", "blue", "yellow"]:
            tabs.addTab(Color(color), color)

        layout_main.addWidget(tabs)  # Add the tabs to the main layout

        # Set the layout to the central widget
        central_widget.setLayout(layout_main)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def GetDatas(self):
        self.tables = GetTables()

    def LayoutInfo(self, layout_info):
        layout = QHBoxLayout()

        # Set the layouts
        layout_housing_value = QVBoxLayout()
        layout_bunch = QVBoxLayout()
        layout_rent = QVBoxLayout()
        layout_iterations = QVBoxLayout()
        layout_mortality_table = QVBoxLayout()

        # Set the elements
        self.le_housing_value = QLineEdit(placeholderText="300000")
        self.le_bunch = QLineEdit(placeholderText="61000")
        self.le_rent = QLineEdit(placeholderText="649")
        self.le_iterations = QLineEdit(text='1000', placeholderText="1000")
        self.cb_mortality_table = QComboBox()

        self.cb_mortality_table.addItems(sorted(list(self.tables.keys()), reverse=True))

        # Set the validator
        self.le_housing_value.setValidator(QInt64Validator(0, 999999999999))
        self.le_bunch.setValidator(QInt64Validator(0, 999999999999))
        self.le_rent.setValidator(QDoubleValidator(0.0, 999999999.0, 2))
        self.le_iterations.setValidator(QIntValidator(1, 10000))

        # Edit the layours
        layout_housing_value.addWidget(QLabel('Housing value'))
        layout_bunch.addWidget(QLabel('Bunch'))
        layout_rent.addWidget(QLabel('Monthly rent'))
        layout_iterations.addWidget(QLabel('Number of iteration'))
        layout_mortality_table.addWidget(QLabel('Mortality table'))

        layout_housing_value.addWidget(self.le_housing_value)
        layout_bunch.addWidget(self.le_bunch)
        layout_rent.addWidget(self.le_rent)
        layout_iterations.addWidget(self.le_iterations)
        layout_mortality_table.addWidget(self.cb_mortality_table)

        # Update Info layout
        layout.addLayout(layout_housing_value)
        layout.addLayout(layout_bunch)
        layout.addLayout(layout_rent)
        layout.addLayout(layout_iterations)
        layout.addLayout(layout_mortality_table)

        # Layout design
        layout.setContentsMargins(0,0,0,20)

        return layout

    def Test(self):
        # Main layout
        main_layout = QVBoxLayout()

        # List widget to display people
        self.people_list = QListWidget()
        main_layout.addWidget(self.people_list)

        # Form layout to add new people (gender and age)
        form_layout = QHBoxLayout()

        # ComboBox for gender selection
        self.gender_combobox = QComboBox()
        self.gender_combobox.addItems(["Male", "Female"])
        form_layout.addWidget(QLabel("Gender:"))
        form_layout.addWidget(self.gender_combobox)

        # LineEdit for age input
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Enter age")
        form_layout.addWidget(QLabel("Age:"))
        form_layout.addWidget(self.age_input)

        # Add the form layout to the main layout
        main_layout.addLayout(form_layout)

        # Button to add person to the list
        add_button = QPushButton("Add Person")
        add_button.clicked.connect(self.add_person)
        main_layout.addWidget(add_button)

        return main_layout
    def add_person(self):
        # Get gender and age input
        gender = self.gender_combobox.currentText()
        age = self.age_input.text()

        # Validate the age input
        if not age.isdigit() or int(age) <= 0:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid positive age.")
            return

        # Add the person to the list
        self.people_list.addItem(f"{gender}, Age: {age}")

        # Clear the input fields
        self.age_input.clear()

        # self.Menu()
        # tabs = QTabWidget()
        # tabs.setTabPosition(QTabWidget.TabPosition.North)
        # tabs.setMovable(True)

        # for color in ["red", "green", "blue", "yellow"]:
        #     tabs.addTab(Color(color), color)

        # self.setCentralWidget(tabs)

        # layout1 = QHBoxLayout()
        # layout2 = QVBoxLayout()
        # layout3 = QVBoxLayout()

        # layout2.addWidget(Color("red"))
        # layout2.addWidget(Color("yellow"))
        # layout2.addWidget(Color("purple"))

        # layout1.setContentsMargins(0,0,0,0)
        # layout1.setSpacing(20)

        # layout1.addLayout(layout2)

        # layout1.addWidget(Color("green"))

        # layout3.addWidget(Color("red"))
        # layout3.addWidget(Color("purple"))

        # layout1.addLayout(layout3)

    #     pagelayout = QVBoxLayout()
    #     button_layout = QHBoxLayout()
    #     self.stacklayout = QStackedLayout()

    #     pagelayout.addLayout(button_layout)
    #     pagelayout.addLayout(self.stacklayout)

    #     btn = QPushButton("red")
    #     btn.pressed.connect(self.activate_tab_1)
    #     button_layout.addWidget(btn)
    #     self.stacklayout.addWidget(Color("red"))

    #     btn = QPushButton("green")
    #     btn.pressed.connect(self.activate_tab_2)
    #     button_layout.addWidget(btn)
    #     self.stacklayout.addWidget(Color("green"))

    #     btn = QPushButton("yellow")
    #     btn.pressed.connect(self.activate_tab_3)
    #     button_layout.addWidget(btn)
    #     self.stacklayout.addWidget(Color("yellow"))

    #     widget = QWidget()
    #     widget.setLayout(pagelayout)
    #     self.setCentralWidget(widget)

    # def activate_tab_1(self):
    #     self.stacklayout.setCurrentIndex(0)

    # def activate_tab_2(self):
    #     self.stacklayout.setCurrentIndex(1)

    # def activate_tab_3(self):
    #     self.stacklayout.setCurrentIndex(2)

    # tabs = QTabWidget()
    # tabs.setDocumentMode(True)
    def Menu(self):
        label = QLabel("Hello!")

        # The `Qt` namespace has a lot of attributes to customize
        # widgets. See: http://doc.qt.io/qt-5/qt.html
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(label)

        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        button_action = QAction(QIcon("bug.png"), "&Your button", self)
        button_action.setStatusTip("This is your button")
        button_action.triggered.connect(self.onMyToolBarButtonClick)
        button_action.setCheckable(True)
        # You can enter keyboard shortcuts using key names (e.g. Ctrl+p)
        # Qt.namespace identifiers (e.g. Qt.CTRL + Qt.Key_P)
        # or system agnostic identifiers (e.g. QKeySequence.StandardKey.Print)
        button_action.setShortcut(QKeySequence("Ctrl+p"))
        toolbar.addAction(button_action)

        toolbar.addSeparator()

        button_action2 = QAction(QIcon("bug.png"), "Your &button2", self)
        button_action2.setStatusTip("This is your button2")
        button_action2.triggered.connect(self.onMyToolBarButtonClick)
        button_action2.setCheckable(True)
        toolbar.addAction(button_action2)

        toolbar.addWidget(QLabel("Hello"))
        toolbar.addWidget(QCheckBox())

        self.setStatusBar(QStatusBar(self))

        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_action)

        file_menu.addSeparator()

        file_submenu = file_menu.addMenu("Submenu")

        file_submenu.addAction(button_action2)

    def onMyToolBarButtonClick(self, s):
        print("click", s)

class Color(QWidget):
    def __init__(self, color, height=None):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

        # Optional: Set a fixed height for the Color widget if provided
        if height:
            self.setFixedHeight(height)

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

    def fixup(self, input_str):
        # Optionally fix the input (can customize this method)
        return ""
