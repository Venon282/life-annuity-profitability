import sys
from PyQt6.QtGui import QColor, QPalette, QAction, QIcon, QKeySequence, QIntValidator, QDoubleValidator, QValidator, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QSize, QEvent, QUrl, QObject
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedLayout, QPushButton, QTabWidget, QLabel, QToolBar, QStatusBar, QCheckBox,
    QLineEdit, QTextEdit, QComboBox, QProgressBar, QListWidget, QMessageBox, QListView, QStyledItemDelegate, QAbstractItemView )
import numpy as np
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtNetwork import QNetworkRequest
# internal
from mortality_table import GetTables
from simulation import GetSurvivalDurations, SimulationThread
from results import Results
import markdown


class MainWindow(QMainWindow):
    def __init__(self, margin_v = 20):
        super().__init__()
        self.setWindowTitle("Does this viager is profitable simulation ?")
        self.margin_v = margin_v
        self.GetDatas()
        self.simulation_windows = []

        # Create the central widget for the window
        central_widget = QWidget()

        # Create the main vertical layout
        layout_main = QVBoxLayout()

        # Create the horizontal layout for info (purple section)
        layout_info = self.LayoutInfo()
        layout_main.addLayout(layout_info)  # Add layout_info to the main layout



        # Set the layout to the central widget
        central_widget.setLayout(layout_main)

        # Set the central widget for the main window
        self.setCentralWidget(central_widget)

    def GetDatas(self):
        self.tables = GetTables()

    def LayoutInfo(self):
        layout = QVBoxLayout()

        layout_inputs = self.LayoutInputs()
        layout.addLayout(layout_inputs)

        layout_persons = self.LayoutPersons()
        layout.addLayout(layout_persons)

        bt_simulation = QPushButton('Start the simulation')
        bt_simulation.clicked.connect(self.StartSimulation)
        layout.addWidget(bt_simulation)

        # Layout design
        layout_inputs.setContentsMargins(0, 0, 0, self.margin_v)
        layout_persons.setContentsMargins(0, 0, 0, self.margin_v)
        bt_simulation.setContentsMargins(0, 0, 0, self.margin_v)

        return layout


    def StartSimulation(self):
        if self.VerifyInputs() is False:
            return

        peoples_list = []
        for person in self.peoples:
            infos = person.split(' ')
            gender = 0 if self.genders[0] == infos[0][1:] else 1
            peoples_list.append((gender,int(infos[2])))

        #survival_durations = GetSurvivalDurations(300000, 61000, 647, [(0,71),(0,71)], self.tables['2022'], num_simulations=50000)
        progress_window = SimulationWindow(int(self.le_housing_value.text()), int(self.le_bunch.text()), float(self.le_rent.text().replace(',','.')), peoples_list, self.table, self.cb_mortality_table.currentText(), int(self.le_iterations.text()))
        # Add window to the list
        self.simulation_windows.append(progress_window)

        # Override close event to handle cleanup directly in SimulationWindow
        progress_window.closeEvent = lambda event: self.CleanupWindow(progress_window)

        progress_window.show()

    def CleanupWindow(self, window):
        # Remove the window from the list if it is still in it
        if window in self.simulation_windows:
            self.simulation_windows.remove(window)


    def VerifyInputs(self):
        if self.le_housing_value.hasAcceptableInput() is False:
            QMessageBox.warning(self,'Invalid Input', f'Housing value must be between {self.le_housing_value.validator().bottom()} and {self.le_housing_value.validator().top()}')
            return False
        elif self.le_bunch.hasAcceptableInput() is False:
            QMessageBox.warning(self,'Invalid Input', f'The bunch must be between {self.le_bunch.validator().bottom()} and {self.le_bunch.validator().top()}')
            return False
        elif self.le_rent.hasAcceptableInput() is False:
            QMessageBox.warning(self,'Invalid Input', f'The rent must be between {self.le_rent.validator().bottom()} and {self.le_rent.validator().top()}')
            return False
        elif self.le_iterations.hasAcceptableInput() is False:
            QMessageBox.warning(self,'Invalid Input', f'The iteration number must be between {self.le_iterations.validator().bottom()} and {self.le_iterations.validator().top()}')
            return False

        self.peoples = self.l_people.GetItems()
        if len(self.peoples) == 0:
            QMessageBox.warning(self,'Invalid Input', f'At least one person must be add')
            return False


        return True

    def CbMortalityTableChanged(self):
        self.table = self.tables[self.cb_mortality_table.currentText()]
        self.age_max = int(self.table.iloc[-1]['age'] -1)
        self.le_age.setPlaceholderText(f'Enter age (0-{self.age_max})')

    def LayoutInputs(self):
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
        self.le_rent = QLineEdit(placeholderText="649,69")
        self.le_iterations = QLineEdit(text='50000', placeholderText="50000")
        self.cb_mortality_table = QComboBox()

        self.cb_mortality_table.addItems(sorted(list(self.tables.keys()), reverse=True))
        self.cb_mortality_table.currentTextChanged.connect(self.CbMortalityTableChanged)

        # Set the validator
        self.le_housing_value.setValidator(QInt64Validator(0, 999999999999))
        self.le_bunch.setValidator(QInt64Validator(0, 999999999999))
        self.le_rent.setValidator(QDoubleValidator(0.0, 999999999.0, 2))
        self.le_iterations.setValidator(QIntValidator(1, 2147483647))

        # Edit the layouts
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

        # Construct hierarchie
        layout.addLayout(layout_housing_value)
        layout.addLayout(layout_bunch)
        layout.addLayout(layout_rent)
        layout.addLayout(layout_iterations)
        layout.addLayout(layout_mortality_table)

        return layout

    def LayoutPersons(self):
        # Init layout
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        # List widget to display people
        self.l_people = QList(flow=QListView.Flow.LeftToRight)#QListView() #QListWidget()
        self.l_people
        layout.addWidget(self.l_people)

        # Button to delete the selected person from the list
        delete_button = QPushButton("Delete Person")
        delete_button.clicked.connect(self.DeletePerson)
        form_layout.addWidget(delete_button)

        # Button to add person to the list
        add_button = QPushButton("Add Person")
        add_button.clicked.connect(self.AddPerson)
        form_layout.addWidget(add_button)

        # ComboBox for gender selection
        self.cb_gender = QComboBox()
        self.genders = ["Male", "Female"]
        self.cb_gender.addItems(self.genders)
        form_layout.addWidget(QLabel("Gender:"))
        form_layout.addWidget(self.cb_gender)

        # LineEdit for age input
        self.table = self.tables[self.cb_mortality_table.currentText()]
        self.age_max = int(self.table.iloc[-1]['age'] -1)
        self.le_age = QLineEdit(placeholderText=f'Enter age (0-{self.age_max})')
        self.le_age.setValidator(QIntValidator(0, self.age_max))
        # self.prev = self.le_age.keyPressEvent
        # self.le_age.keyPressEvent = self.LeAgeKeyPressEvent
        self.le_age.installEventFilter(self)
        form_layout.addWidget(QLabel("Age:"))
        form_layout.addWidget(self.le_age)

        # Add the form layout to the main layout
        layout.addLayout(form_layout)

        return layout


    def eventFilter(self, source, event):
        # Check if the event source is the QLineEdit
        if source is self.le_age:
            # Check if the event is a key press event
            if event.type() == QEvent.Type.KeyPress:  # QEvent.KeyPress
                # Check if the pressed key is the Enter key
                if event.key() == Qt.Key.Key_Return:  # Key code for Enter key
                    self.AddPerson()
                    return True  # Ignore the event to prevent default behavior

        # Call the base class method for all other events
        return super().eventFilter(source, event)
    def AddPerson(self):
        # Get gender and age input
        gender = self.cb_gender.currentText()
        age = self.le_age.text()

        # Validate the age input
        if not age.isdigit() or int(age) <= 0 or int(age) >= self.age_max:
            QMessageBox.warning(self, "Invalid Input", f'Please enter a valid positive age under {self.age_max}.')
            return

        # Add the person to the list
        self.l_people.addItem(f"({gender} of {age} years)")

        # Clear the input fields
        self.le_age.clear()

    def DeletePerson(self):
        selected_indexes = self.l_people.selectedIndexes()

        if not selected_indexes:
            # If no item is selected, show a warning
            QMessageBox.warning(self, "No Selection", "Please select a person to delete.")
            return

        self.l_people.DeleteItems(selected_indexes)

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
# Progress window to show simulation progress
class SimulationWindow(QWidget):
    def __init__(self, housing_value, bunch, rent, peoples, table, table_year, num_simulations):
        super().__init__()
        self.setWindowTitle("Simulation Progress")

        # Initialize layout and progress bar
        self.layout = QVBoxLayout()
        self.label = QLabel("Simulation in progress...")
        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress_bar)
        self.setLayout(self.layout)

        self.housing_value = housing_value
        self.bunch = bunch
        self.rent = rent
        self.peoples = peoples
        self.table = table
        self.table_year = table_year
        self.num_simulations = num_simulations

        # Start simulation thread
        self.simulation_thread = SimulationThread(housing_value, bunch, rent, peoples, table, num_simulations)
        self.simulation_thread.progress.connect(self.update_progress)
        self.simulation_thread.finished.connect(self.display_results)
        self.simulation_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_results(self, results):
        # Once simulation is finished, replace progress with results
        self.label.setText("Simulation complete! Displaying results...")
        self.progress_bar.hide()
        # "table":self.table,
        results_calculates = Results(results, inputs={
            "housing_value":self.housing_value,
            "bunch":self.bunch,
            "rent":self.rent,
            "num_simulations":self.num_simulations,
            "table_year":self.table_year,
            "peoples":self.peoples
        })
        # text_edit = QTextEdit()
        # text_edit.setReadOnly(True)
        # text_edit.setMarkdown(results_calculates)
        # self.layout.addWidget(text_edit)
        view = MarkdownViewer(results_calculates)
        view.resize(600, 400)
        # view.show()
        self.layout.addWidget(view)

        self.label.hide()


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
