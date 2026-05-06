import os
import pathlib
import pandas as pd
import streamlit as st

#---------Paths & helpers

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SCENARIOS_CSV = DATA_DIR / "scenarios.csv"

def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_scenarios() -> pd.DataFrame:
    ensure_data_dir()
    if SCENARIOS_CSV.exists():
        return pd.read_csv(SCENARIOS_CSV)
    else:
        #Creates an empty data frame with the wanted columns
        cols =  [
            "name",
            "path_type",
            "years_in_school",
            "tuition_per_year",
            "loan_amount",
            "loan_interest_rate",
            "loan_term_years",
            "starting_salary",
            "salary_growth_rate",
            "monthly_expenses",
            "training_cost",
            "simulation_years",
        ]
        return pd.DataFrame(columns=cols)
    
def save_scenarios(df: pd.DataFrame) -> None:
    ensure_data_dir()
    df.to_csv(SCENARIOS_CSV, index=False)

def simulate_scenario(row: pd.Series) -> pd.DataFrame:
    """Given a single scenario row, return a year-by-year projection."""
    path_type = row["path_type"].lower()
    years_in_school = int(row["years_in_school"])
    tuition_per_year = float(row["tuition_per_year"])
    loan_amount = float(row["loan_amount"])
    loan_interest_rate = float(row["loan_interest_rate"])
    loan_term_years = int(row["loan_term_years"])
    starting_salary = float(row["starting_salary"])
    salary_growth_rate = float(row["salary_growth_rate"])
    monthly_expenses = float(row["monthly_expenses"])
    training_cost = float(row["training_cost"])
    simulation_years = int(row["simulation_years"])
    
    # Basic assumptions
    years = list(range(simulation_years + 1))  # year 0 .. N
    salary = []
    expenses = []
    loan_balance = []
    savings = []
    
    # Loan payment (if any)
    if loan_amount > 0 and loan_term_years > 0 and loan_interest_rate >0:
        r = loan_interest_rate / 12  #monthly rate
        n = loan_term_years * 12  #toatl months
        monthly_payment = loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n -1)
    else:
        monthly_payment = 0.0
        
    current_loan = loan_amount
    current_savings = 0.0
    
    for year in years:
        # To determine annual income
        if path_type == "college":
            if year < years_in_school:
                # In school: assumes no full-time salary, but could have part-time income (not modeled here)
                annual_salary = 0.0
            else:
                working_year_index = year - years_in_school
                annual_salary = starting_salary * (1 + salary_growth_rate) ** working_year_index
        else:  # work path
            working_year_index = year #starts at year 0
            annual_salary = starting_salary * (1 + salary_growth_rate) ** working_year_index
            
        # Annual expense (12 months)
        annual_expense = monthly_expenses * 12.0
        
        # Apply one-time training or tuition cost in year 0 only 
        extra_cost = 0.0
        if year == 0:
            if path_type == "college":
                extra_cost += years_in_school * tuition_per_year
            else:
                extra_cost += training_cost
                
        # Loan payments of this year
        if current_loan > 0 and monthly_payment > 0:
            # Pay for up to 12 months or until loan is gone
            total_payment_year = 0.0
            for _ in range(12):
                if current_loan <= 0:
                    break
                interest = current_loan * (loan_interest_rate / 120)
                principle = monthly_payment - interest
                if principle > current_loan:
                    principle = current_loan
                    monthly_payment = interest + principle
                else:
                    monthly_payment_effective = interest + principle
                    current_loan -= principle
                    total_payment_year += monthly_payment_effective
        else:
            total_payment_year = 0.0
            
        # Net cash and savings
        net_cash = annual_salary - annual_expense - extra_cost - total_payment_year
        current_savings += net_cash
        
        salary.append(annual_salary)
        expenses.append(annual_expense + extra_cost)
        loan_balance.append(max(current_loan, 0.0))
        savings.append(current_savings)
        
    df = pd.DataFrame(
        {
            "year": years,
            "salary": salary,
            "total_expenses": expenses,
            "loan_balance": loan_balance,
            "savings": savings,
        }
    )
    return df
#---------Streamlit app---------

st.set_page_config(page_title= "College vs Work Simulator", page_icon=":mortar_board:")

st.title("College vs Work - Scenario Manager (Starter)")
st.write("This is the starter view. We are just loading and displaying scenarios for now.")

#Loading Scenarios
scenarios_df = load_scenarios()

st.subheader("Saved Scenarios")
st.dataframe(scenarios_df)

st.write("Number of scenarios:", len(scenarios_df))

st.markdown("---")
st.subheader("Add a New Scenario")

with st.form("add_scenario_form"):
    name= st.text_input("Scenario name", value="My Scenario")
    
    path_type = st.radio(
        "Path Type",
        options=["college", "work"],
        index=0,
        help="Choose 'college' if this scenario includes tuition and loans, or 'work' if you start working immediately."
    )
    
    years_in_school = st.number_input("Years in school (only for college path)", min_value=0, max_value=10, value=4)
    tuition_per_year = st.number_input("Tuition per year (only for college path)", min_value=0, value=20000, step=1000)
    
    loan_amount = st.number_input("Total loan amount", min_value=0, value=30000, step=1000)
    loan_interest_rate = st.number_input("Loan interest rate (e.g., 0.05 for 5%)", min_value=0.0, max_value=1.0, value=0.05, step=0.01)
    loan_term_years = st.number_input("Loan term in years", min_value=0, max_value=40, value=10)
    
    starting_salary = st.number_input("Starting Salary", min_value=0, value=60000, step=1000)
    salary_growth_rate = st.number_input("Annual Salary Growth Rate (e.g., 0.03 for 3%)", min_value=0.0, max_value=1.0, value=0.03, step=0.01)
    
    monthly_expenses = st.number_input("Monthly living expenses", min_value=0, value=1500, step=100)
    training_cost = st.number_input("Cost of any additional training or certifications", min_value=0, value=0, step=500)
    part_time_monthly_income = st.number_input("Part-time monthly income during college (for college path)",
                                               min_value=0, value=800, step=100)
    simulation_years = st.number_input("Years to simulate", min_value=1, max_value=50, value=15)
    
    submitted = st.form_submit_button("Save scenario")
    
if submitted:
    #Creates a new row as a dict
    new_row = {
        "name":name,
        "path_type": path_type,
        "years_in_school": years_in_school,
        "tuition_per_year": tuition_per_year,
        "loan_amount": loan_amount,
        "loan_interest_rate": loan_interest_rate,
        "loan_term_years": loan_term_years,
        "starting_salary": starting_salary,
        "salary_growth_rate": salary_growth_rate,
        "monthly_expenses": monthly_expenses,
        "training_cost": training_cost,
        "simulation_years": simulation_years,
    }
    
    #Append the new row to the data frame
    scenarios_df = pd.concat(
        [scenarios_df, pd.DataFrame([new_row])],
        ignore_index=True
    )
    
    #Saves to CSV
    save_scenarios(scenarios_df)
    
    st.success(f"Scenario '{name}' saved!")
    st.rerun()
    
st.markdown("---")
st.subheader("Run Simulation for a Scenario")

if len(scenarios_df) == 0:
    st.info("No scenario saved yet. Add a scenario above to run a simulation.")
else:
    # Lets the user pick a scenario by name to simulate
    selected_name = st.selectbox("Choose a scenario to simulate", 
                                    options=scenarios_df["name"].tolist(),
    )
    
    # Find the selected scenario row
    selected_row = scenarios_df[scenarios_df["name"] == selected_name].iloc[0]
    
    # Run the simulation
    projection_df = simulate_scenario(selected_row)
    
    st.write(f"Simulation resuts for **{selected_name}**")
    
    st.dataframe(projection_df)
    
    # Charts
    st.line_chart(
        projection_df.set_index("year")[["savings"]],
        height=300,
    )
    
    st.line_chart(
        projection_df.set_index("year")[["loan_balance"]],
        height=300,
    )
    
    # Summary metrics
    final_row = projection_df.iloc[-1]
    st.metric("Savings at end of simulation", f"${final_row['savings']:,.0f}")
    st.metric("Remaining loan balance", f"${final_row['loan_balance']:,.0f}")