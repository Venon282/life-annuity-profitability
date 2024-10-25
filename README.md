# life-annuity-profitability

This application allows you to simulate the profitability of a life annuity based on a Monte-Carlo algorithm.

## Disclaimer
This application is intended solely for simulation and informational purposes and should not be interpreted as financial or investment advice. While it can provide helpful indicators for understanding viager profitability scenarios, please be aware of the following limitations:
- **Use of Pseudo-Random Number Generation:** The application employs pseudo-random number generators for simulations, which, while robust for modeling, may not fully capture all possible variations in real-life outcomes.
- **Reliance on Historical Mortality Tables:** This application relies on historical french mortality data, which may not accurately reflect current or future mortality trends, healthcare advancements, or socioeconomic factors. The tables used are intended to provide an approximation and should be considered accordingly.
- **Indicative Results, Not Guarantees:** This simulation’s results serve as a potential guide, not an assurance. Actual viager profitability may differ significantly due to unforeseen factors and market changes. Results should be interpreted as an indicator, not a precise prediction of future performance.
- **No Liability for Use:** This application is provided "as-is," with no warranties regarding its accuracy, completeness, or suitability for any particular purpose. The creator holds no responsibility for any financial decisions or investments made based on the use of this application. Users bear full responsibility for any investment outcomes, including potential financial loss.

By using this application, you acknowledge and accept these limitations and agree to use the information solely at your own risk. For personalized financial advice, please consult with a certified professional.

## Algorithme
This application uses a Monte Carlo algorithm to simulate the expected lifespans of viager occupants and assess investment profitability. Here’s the high-level process:

- **Simulation of Lifespan:** The app runs thousands of random simulations to estimate how long the viager might last. Each run considers the lifespan of every occupant, based on historical mortality rates for different ages and genders.

- **Mortality Data:** Mortality probabilities from historical French statistics are used to determine the likelihood of survival year by year.

- **Group Duration:** Each simulation records the lifespan of the longest-living occupant since payments continue until the last occupant passes away.

- **Probabilistic Results:** By repeating this process, the app provides average, median, and potential high-lifespan scenarios, giving a range of possible outcomes for profitability.

## Input Parameters
Housing Value: Market value of the property.
Initial Payment (Bouquet): Upfront payment amount.
Monthly Rent: Monthly rent or annuity paid to the occupant(s).
People: A list of tuples with each occupant's age and gender (e.g., [(age1, gender1), (age2, gender2)] where gender is 0 for male and 1 for female).
Mortality Table: Year of the mortality data to use. Options depend on available data (e.g., 2022).
Number of Simulations: Number of Monte Carlo simulations to run (higher values yield more accurate statistical outcomes).

## Todo
- When the result appear, get a windows bigger
- Download the lifespans list as a txt
- Add a header menu with:
  - About with this ReadMe
  - Page for modify the config.json safely
- Add a slider for see the result at year N

## License
This project is licensed under the MIT License.
