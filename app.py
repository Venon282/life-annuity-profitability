from PyQt6.QtGui import QIntValidator, QDoubleValidator
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QProgressBar, QListWidget, QMessageBox, QListView
import json

# internal
from mortality_table import GetTables
from simulation import GetSurvivalDurations, SimulationThread
from results import Results
from PyQt6_custom import *


class MainWindow(QMainWindow):
    def __init__(self, margin_v = 20):
        super().__init__()
        self.setWindowTitle("Does this viager is profitable simulation ?")
        self.margin_v = margin_v        # Margin between the sections vertically
        self.tables = GetTables()
        self.simulation_windows = []

        # Create the central widget for the window
        widget = QWidget()

        # Create the main vertical layout
        layout = QVBoxLayout()

        # Create the horizontal layout for info
        layout.addLayout(self.LayoutInfo())

        # Set the layout to the central widget
        widget.setLayout(layout)

        # Set the central widget for the main window
        self.setCentralWidget(widget)

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
        self.le_iterations = QLineEdit(text='100000', placeholderText="100000")
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
        self.le_age.installEventFilter(self)
        form_layout.addWidget(QLabel("Age:"))
        form_layout.addWidget(self.le_age)

        # Add the form layout to the main layout
        layout.addLayout(form_layout)

        return layout

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


# Progress window to show simulation progress
class SimulationWindow(QWidget):
    def __init__(self, housing_value, bunch, rent, peoples, table, table_year, num_simulations):
        super().__init__()
        self.setWindowTitle("Simulation Progress")

        with open('config.json', 'r') as file:
            self.datas = json.load(file)

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
        self.simulation_thread = SimulationThread(housing_value, bunch, rent, peoples, table, num_simulations, self.datas['loading_bar_update_rate'])
        self.simulation_thread.progress.connect(self.update_progress)
        self.simulation_thread.finished.connect(self.display_results)
        self.simulation_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_results(self, results):
        # Once simulation is finished, replace progress with results
        self.label.setText("Simulation complete! Displaying results...")
        self.progress_bar.hide()

        results_calculates = Results(self.datas, results, inputs={
            "housing_value":self.housing_value,
            "bunch":self.bunch,
            "rent":self.rent,
            "num_simulations":self.num_simulations,
            "table_year":self.table_year,
            "peoples":self.peoples
        })

        view = MarkdownViewer(results_calculates)
        self.resize(650, 800)
        self.layout.addWidget(view)

        self.label.hide()
