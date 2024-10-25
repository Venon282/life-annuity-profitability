from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                             QVBoxLayout, QPushButton, QProgressBar)

import numpy as np
import pandas as pd
import time

def precompute_lifespans(table):
    """Precompute lifespan probability arrays for each age and gender."""
    male_mortality = table['mq'].values / 100000  # Male mortality rate
    female_mortality = table['fq'].values / 100000  # Female mortality rate
    return male_mortality, female_mortality

def simulate_lifespan_vectorized(age, mortality_rates):
    """Simulate lifespan using precomputed mortality rates in a vectorized manner."""
    lifespan = 0
    while age < len(mortality_rates):
        if np.random.rand() < mortality_rates[age]:  # Check if death occurs this year
            break
        lifespan += 1
        age += 1

    return lifespan

def simulate_for_person(age, gender, male_mortality, female_mortality):
    """Simulate the survival duration for one person."""
    mortality_rates = male_mortality if gender == 0 else female_mortality
    return simulate_lifespan_vectorized(age, mortality_rates)

# Move simulate_one_iteration outside
def simulate_one_iteration(peoples, male_mortality, female_mortality):
    """Run a single simulation iteration for all people."""
    max_lifespan_simulation = 0
    for gender, age in peoples:
        lifespan = simulate_for_person(age, gender, male_mortality, female_mortality)
        max_lifespan_simulation = max(max_lifespan_simulation, lifespan)
    return max_lifespan_simulation

def GetSurvivalDurations(housing_value, bunch, rent, peoples, table, num_simulations=1000):
    # Precompute mortality rates for faster simulation
    male_mortality, female_mortality = precompute_lifespans(table)

    # Monte Carlo simulations

    results = []
    n = time.time()
    for i in range(num_simulations):
        if time.time() >= n+1:
            print(i, end='\r')
            n+=1
        results.append(simulate_one_iteration(peoples, male_mortality, female_mortality))

    return np.array(results)

# Worker thread for the simulation
class SimulationThread(QThread):
    progress = pyqtSignal(int)  # Signal to update progress
    finished = pyqtSignal(np.ndarray)  # Signal when done with results

    def __init__(self, housing_value, bunch, rent, peoples, table, num_simulations):
        super().__init__()
        self.housing_value = housing_value
        self.bunch = bunch
        self.rent = rent
        self.peoples = peoples
        self.table = table
        self.num_simulations = num_simulations

    def run(self):
        # Simulate durations as before, with progress updates
        male_mortality, female_mortality = precompute_lifespans(self.table)
        results = []
        for i in range(self.num_simulations):
            results.append(simulate_one_iteration(self.peoples, male_mortality, female_mortality))
            if i % (self.num_simulations // 100) == 0:
                self.progress.emit(int((i / self.num_simulations) * 100))  # Emit progress
        self.finished.emit(np.array(results))  # Emit results when finished
