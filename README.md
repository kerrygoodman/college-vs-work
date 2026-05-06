This project is a Streamlit web app that helps users compare the long‑term financial impact of going to college versus entering the workforce immediately. It lets you define scenarios (tuition, loans, salaries, living costs, part‑time work, etc.), simulate year‑by‑year finances, and visualize savings and loan balance over time.

Features
Scenario manager

Create, view, and delete named scenarios.

Two path types:

college – includes years in school, tuition, and loans.

work – starts working immediately, optionally with a training cost.

All scenarios are saved to and loaded from data/scenarios.csv.

Customizable assumptions per scenario

Years in school.

Tuition per year (college path).

Total loan amount, interest rate, and loan term (years).

Starting salary and annual salary growth rate.

Monthly living expenses.

Part‑time monthly income during college (college path).

One‑time training cost (work path).

Number of years to simulate.

Year‑by‑year financial simulation

Calculates annual:

Income (part‑time during college, full‑time after).

Total expenses (living expenses + tuition or training cost).

Loan balance, using a fixed monthly payment formula.

Net savings / “net worth” over time.

Displays results in a table and line charts:

Savings over time.

Loan balance over time.

Scenario comparison

Select two scenarios (e.g., “College – CS Degree” vs “Work – Trade Job”).

See both savings lines on a single chart.

View a summary table with:

Scenario name.

Path type (college or work).

Final savings at the end of the simulation.

Final remaining loan balance.

How the calculations work (high‑level)
For each scenario, the app simulates finances from year 0 up to simulation_years:

Income

College path:

During school years: income is part_time_monthly_income × 12.

After graduation: salary starts at starting_salary and grows annually by salary_growth_rate.

Work path:

Starts full‑time work at year 0 with starting_salary, growing annually by salary_growth_rate.

Expenses

Base expenses are monthly_expenses × 12 each year.

College path adds tuition_per_year for each school year.

Work path can add a one‑time training_cost in year 0.

Loans

If there is a loan amount, interest rate, and term, the app computes a fixed monthly payment using a standard loan amortization formula.

Each year, it applies monthly interest and principal payments for up to 12 months (or until the loan is paid off).

The remaining loan balance is tracked over time.

Savings

For each year:
net_cash = income − expenses − loan_payments
savings_t = savings_(t−1) + net_cash

Savings start at 0 and accumulate over the simulation period.

This is a simplified model designed for educational “what‑if” exploration, not professional financial advice.

Project structure
Typical layout:

text
college-vs-work-streamlit/
  .venv/                 # Python virtual environment (not committed)
  data/
    scenarios.csv        # Scenario data (created/updated by the app)
  src/
    main.py              # Streamlit app
  .gitignore
  README.md
src/main.py contains:

File path helpers and CSV read/write logic.

simulate_scenario() which performs the year‑by‑year financial projection.

Streamlit UI for managing, simulating, comparing, and deleting scenarios.

Getting started
Prerequisites
Python 3.10+ installed and on your PATH.

Git (if you’re using GitHub).

Recommended: VS Code with the Python and Git extensions.

1. Clone the repo (or open the project folder)
bash
git clone https://github.com/<your-username>/college-vs-work-streamlit.git
cd college-vs-work-streamlit
Or, if you already have the folder locally, just cd into it.

2. Create and activate a virtual environment
On Windows (Command Prompt):

bash
python -m venv .venv
.venv\Scripts\activate.bat
You should see (.venv) at the beginning of your terminal prompt.

3. Install dependencies
With the virtual environment activated:

bash
pip install streamlit pandas
4. Run the app
From the project root:

bash
cd src
streamlit run main.py
Or from the root using the relative path:

bash
streamlit run src\main.py
Then open your browser to:

text
http://localhost:8501
if it doesn’t open automatically.

How to use the app
View current scenarios

At the top of the page, you’ll see a table of all saved scenarios and a count.

Add a new scenario

Fill in the form under “Add a New Scenario”.

Choose a path type (college or work).

Enter the financial assumptions.

Click Save scenario.

The scenario is appended to data/scenarios.csv and appears in the table.

Delete a scenario

Under “Delete a Scenario”, pick a scenario by name.

Click Delete selected scenario.

The scenario is removed from the CSV and from all dropdowns.

Run a simulation for one scenario

In “Run Simulation for a Scenario”, select a scenario by name.

The app runs the projection and shows:

A table of year‑by‑year values.

A line chart of savings (net worth) over time.

A line chart of loan balance over time.

Key metrics for final savings and remaining loan balance.

Compare two scenarios

-In “Compare Two Scenarios (Savings Over Time)”, select exactly two scenarios.

-The app draws both savings curves on the same chart.

-A summary table shows final savings and loan balance for each scenario.

Limitations and possible improvements
-Assumes a fixed salary growth rate and fixed monthly expenses.

-Tuition is modeled as a simple per‑year cost, not by semester or credit.

-Loan model assumes a single loan with constant interest rate and fixed payment.

-Taxes, inflation, and investment returns are not included.

Potential future enhancements:

-Add separate expense categories (rent, food transportation, etc.).

-Model multiple loans or changing interest rates.

-Include tax estimates or inflation adjustments.

-Export simulation results to CSV for further analysis.

AI usage disclosure
Portions of the project structure and wording were developed with assistance from an AI coding assistant (Perplexity, powered by GPT‑5.1). All code has been reviewed and understood by the author, and the final design decisions, parameters, and logic were chosen by the author to meet course requirements.

