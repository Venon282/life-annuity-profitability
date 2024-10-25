import pandas as pd
import numpy as np
import sys
from PyQt6.QtWidgets import QApplication

# internal
from app import MainWindow

def RentValue(property_value, bunch, annuitant_life_expectancy):
    return (property_value - bunch) / annuitant_life_expectancy

def MortalityTable(year):
    try:
        table = getattr(mortabilityTables, f'MortalityTable{year}')
        return table()
    except Exception as e:
        raise AttributeError(f'The year {year} is not validate. {e}')

def Rentability(housing_value, bunch, rent, peoples, mortality_table=2022):
    if not isinstance(peoples, list) or len(peoples) == 0:
        raise TypeError('peoples should be a list of tuples not empty. Each tuple representing the person age and its gender (0 man, 1 female)')

    # Get the mortality table for the specified year
    table = MortalityTable(mortality_table)

    total_rentability_amount = 0
    total_years_of_rent = 0

    # Calculate the expected lifespan and total rent from each person
    for age, gender in peoples:
        if age < 0 or age >= len(table):
            raise ValueError(f'Age {age} is out of bounds for the mortality table.')

        expected_lifespan = table[age][gender]  # Get the expected lifespan for the person
        years_of_rent = max(0, expected_lifespan - age)  # Calculate how many years they are expected to rent

        total_years_of_rent += years_of_rent
        total_rentability_amount += years_of_rent * rent  # Total rent income from this person

    # Total amount received from the bouquet plus the rent
    total_income = total_rentability_amount + bunch

    # Calculate metrics
    rentability_rate = (total_income / housing_value) * 100  # Rentability rate as a percentage of the housing value
    profitability_percentage = ((total_income - housing_value) / housing_value) * 100  # Profitability

    # Create a results tuple
    return (
        profitability_percentage,
        rentability_rate,
        total_rentability_amount,
        total_years_of_rent
    )

# def GetTables(path='./tables_fr.xlsx'):
#     return pd.read_excel(path, engine="openpyxl", sheet_name=None)

# # Main function for viager calculations
# def Main(housing_value, bunch, rent, peoples, mortality_table=2022):
#     tables = mt.GetTables()

#     try:
#         table = tables[str(mortality_table)]
#     except KeyError as ke:
#         raise AttributeError(f'The {mortality_table} mortality table is not available.\n'
#                              f'Possibilities: {list(tables.keys())}')

#     total_rent_cost = 0
#     lifespans = []

#     # For each person in the viager, calculate expected remaining lifespan and total rent cost
#     for age, gender in peoples:
#         if gender == 0:  # Male
#             remaining_life = get_life_expectancy(table, age, 'me')
#         elif gender == 1:  # Female
#             remaining_life = get_life_expectancy(table, age, 'fe')
#         else:
#             raise ValueError("Gender should be 0 (male) or 1 (female).")

#         # Add lifespan to the list for future statistics
#         lifespans.append(remaining_life)


#     # Take the maximum lifespan, as rent is paid until the last survivor
#     longest_lifespan = max(lifespans)

#     # Calculate total rent payments over the longest lifespan
#     total_rent_cost = rent * 12 * longest_lifespan  # Monthly rent, so multiply by 12 for annual

#     total_investment = bunch + total_rent_cost
#     profit_or_loss = housing_value - total_investment
#     profitability_percentage = (profit_or_loss / total_investment) * 100

#     # Generate a detailed report
#     report = {
#         "Housing Value": housing_value,
#         "Initial Payment (Bouquet)": bunch,
#         "Total Rent Cost": total_rent_cost,
#         "Total Investment": total_investment,
#         "Profit or Loss": profit_or_loss,
#         "Profitability Percentage": profitability_percentage,
#         "Expected Lifespans (years)": lifespans,
#         "Break-even Point (years)": total_investment / (rent * 12) if rent > 0 else None
#     }

#     return report

# # Helper function to calculate life expectancy based on the mortality table
# def get_life_expectancy(table, age, column_prefix):
#     # Select the row in the table corresponding to the person's age
#     row = table[table['age'] == age]

#     if row.empty:
#         raise ValueError(f"No data available for age {age} in the mortality table.")

#     # Return the life expectancy (e.g., 'me' for men, 'fe' for women)
#     return row[f'{column_prefix}'].values[0]

# Main function for viager calculations with probability-based lifespan estimations
def Main(housing_value, bunch, rent, peoples, mortality_table=2022, num_simulations=1000):


    try:
        table = tables[str(mortality_table)]
    except KeyError as ke:
        raise AttributeError(f'The {mortality_table} mortality table is not available.\n'
                             f'Possibilities: {list(tables.keys())}')

    # Run Monte Carlo simulations to estimate how long the viager will last
    survival_durations = []
    for i in range(num_simulations):
        print(f'{i}/{num_simulations}')
        max_lifespan_simulation = 0
        for age, gender in peoples:
            if gender == 0:  # Male
                lifespan = simulate_lifespan(table, age, 'mq')  # Use male mortality quotient
            elif gender == 1:  # Female
                lifespan = simulate_lifespan(table, age, 'fq')  # Use female mortality quotient
            else:
                raise ValueError("Gender should be 0 (male) or 1 (female).")

            max_lifespan_simulation = max(max_lifespan_simulation, lifespan)

        survival_durations.append(max_lifespan_simulation)

    # Calculate total rent cost using the average lifespan from the simulations
    lifespans = {
        "mean":np.mean(survival_durations),
        "median": np.quantile(survival_durations, 0.5),
        "95":np.quantile(survival_durations, 0.95),
        "min":np.min(survival_durations),
        "max":np.max(survival_durations),
        "all":np.array(survival_durations)
        }

    a_year_of_rent = rent * 12

    # Generate a detailed report
    report = {
        "Housing Value": housing_value,
        "Initial Payment (Bouquet)": bunch,
        "A year of rent":a_year_of_rent,
        #"Simulated Lifespans (years)": survival_durations,

    }

    for key, value in lifespans.items():
        report[key]['Total Rent Cost']              = value * a_year_of_rent
        report[key]['Total Investment']             = report[key]['Total Rent Cost'] + bunch
        report[key]['Profit']                       = housing_value - report[key]['Total Investment']
        report[key]['Profitability Percentage']     = (report[key]['Profit'] / report[key]['Total Investment']) * 100
        report[key]['Simulated Lifespan in years']  = value


    report.update({
        "Break-even Point (years)": (housing_value - bunch) / (rent * 12) if rent > 0 else None,
        "Profitability Chance (%)":len(report['all']['Profit'][report['all']['Profit']>0]) / num_simulations * 100,
        "Profitability Chance (>10% of the housing value)":len(report['all']['Profit'][report['all']['Profit']>(housing_value*0.1)]) / num_simulations * 100
    })

    return report

# Helper function to simulate lifespan based on mortality quotients (probability of death)
def simulate_lifespan(table, age, mortality_column):
    lifespan = 0
    while True:
        # Get the mortality rate (quotient de mortalité) for the current age
        row = table[table['age'] == age]
        if row.empty:
            break  # If the table doesn't have data for the age, break out of the loop

        mortality_rate = row[mortality_column].values[0] / 100000  # Quotient de mortalité
        if np.random.rand() < mortality_rate:  # Simulate whether the person dies this year
            break

        # If the person survives this year, increase the lifespan and move to the next year
        lifespan += 1
        age += 1

    return lifespan


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QPushButton {
            padding: 3px 7px 3px 7px;
        }
    """)

    window = MainWindow()
    window.show()
    app.exec()
    # result = Rentability(200000, 30000, 800, [(70, 0), (65, 1)])
    #result = Main(200000, 30000, 800, [(70, 0), (65, 1)], mortality_table=2022) ,(71, 0),(71, 0),(71, 0),(71, 0),(71, 0),(71, 0),(71, 0)
    # result = Main(300000, 61000, 649, [(71, 0)], mortality_table=2022)
    # for key, value in result.items():
    #     print(f"{key}: {value}")
