import os
import pathlib
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Simple color palette

COLOR_SAVINGS = "#1f77b4"  # Blue
COLOR_LOAN = "#d62728"     # Red
COLOR_SCENARIO_A = "#1f77b4"     # Blue
COLOR_SCENARIO_B = "#ff7f0e"     # Orange


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
            "part_time_monthly_income",
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
    part_time_monthly_income = float(row.get("part_time_monthly_income", 0.0))
    
    # Basic assumptions
    years = list(range(simulation_years + 1))  # year 0 .. N
    salary = []
    expenses = []
    loan_balance = []
    savings = []
    
    # Loan payment (if any)
    if loan_amount > 0 and loan_term_years > 0 and loan_interest_rate >0:
        r = loan_interest_rate / 12.0  #monthly rate
        n = loan_term_years * 12  #toatl months
        monthly_payment = loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    else:
        monthly_payment = 0.0
        
    current_loan = loan_amount
    current_savings = 0.0
    
    for year in years:
        # ---Income ---
        if path_type == "college":
            if year < years_in_school:
                # Part-time income while in school
                annual_salary = part_time_monthly_income * 12.0
            else:
                working_year_index = year - years_in_school
                annual_salary = starting_salary * (1 + salary_growth_rate) ** working_year_index
        else:  # work path
            working_year_index = year #starts at year 0
            annual_salary = starting_salary * (1 + salary_growth_rate) ** working_year_index
            
        # ---Expenses ---
        base_annual_expense = monthly_expenses * 12.0
        
        # Tuition spread across school years only
        tuition_this_year = tuition_per_year if (path_type == "college" and year < years_in_school) else 0.0
        
        # Training cost for work path year 0 only 
        training_this_year = training_cost if (path_type == "work" and year == 0) else 0.0
        
        annual_expenses = base_annual_expense + tuition_this_year + training_this_year
                
        # ---Loan payments ---
        if current_loan > 0 and monthly_payment > 0:
            # Pay for up to 12 months or until loan is gone
            total_payment_year = 0.0
            for _ in range(12):
                if current_loan <= 0:
                    break
                interest = current_loan * (loan_interest_rate / 12.0)
                principle = monthly_payment - interest
                if principle > current_loan:
                    principle = current_loan
                    monthly_payment_effective = interest + principle
                else:
                    monthly_payment_effective = monthly_payment
                    current_loan -= principle
                    total_payment_year += monthly_payment_effective
        else:
            total_payment_year = 0.0
            
        # ---Net cash and savings ---
        net_cash = annual_salary - annual_expenses - total_payment_year
        current_savings += net_cash
        
        salary.append(annual_salary)
        expenses.append(annual_expenses)
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

# Custom CSS
st.markdown(
    """
    <style>
    /* Page background gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #020617 100%);
        color: #f9fafb;
    }
    
    /* Card-like sections */
    .scenario-card {
        background-color: rgba(15, 23, 42, 0.85);
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid rgba(148, 163, 184, 0.35);
        margin-bottom: 1.5rem;
    }
    
    /* Section titles */
    .section-title {
        font-size: 1.3rem;
        font-wieght: 600;
        margin-bottom: 0.5rem;
        color: #e5e7eb;
    }
        
    /* Make dataframe headers pop a bit */
    .dataframe th {
        background-color: #111827 !important;
        color: #e5e7eb !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("College vs Work - Financial Planning Simulator")
st.write(
    "Build college and work scenarios, simulate your finances over time,"
    "and visually compare which path fits your situation better."
)

# Loads scenarios ONCE
scenarios_df = load_scenarios()

#--- Scenario overview card ---
st.markdown('<div class="scenario-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Saved scenarios</div>',
            unsafe_allow_html=True)

st.dataframe(scenarios_df, use_container_width=True)
st.write("Number of scenarios:", len(scenarios_df))

#--- Delete scenario controls ---
if len(scenarios_df) > 0:
    st.markdown('### Delete a Scenario')
    
    scenario_to_delete = st.selectbox(
        "Select a scenario to delete",
        options=scenarios_df["name"].tolist(),
        key="delete_select",
    )
    
    if st.button("Delete selected scenario"):
        #Drop the selected scenario by name
        updated_df = scenarios_df[scenarios_df["name"] != scenario_to_delete].reset_index(drop=True)
        save_scenarios(updated_df)
        st.success(f"Scenario '{scenario_to_delete}' deleted.")
        st.rerun()
else:
    st.info("No scenarios saved yet. Add one below.")

st.markdown('</div>', unsafe_allow_html=True)

#--- Add scenario card ---
st.markdown('<div class="scenario-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Add a new scenario</div>',
            unsafe_allow_html=True)

with st.form("add_scenario_form"):
    name= st.text_input("Scenario name", value="My Scenario")
    
    path_type = st.radio(
        "Path Type",
        options=["college", "work"],
        index=0,
        help="Choose 'college' if this scenario includes tuition and loans, or 'work' if you start working immediately."
    )
    
    #---- College-only fields ----
    if path_type == "college": 
        years_in_school = st.number_input("Years in school (only for college path)",
                                          min_value=0,
                                          max_value=10,
                                          value=4,
        )
        tuition_per_year = st.number_input("Tuition per year (only for college path)",
                                           min_value=0, value=20000, step=1000
        )
   
    loan_amount = st.number_input("Total loan amount",
                                  min_value=0, value=30000, step=1000
    )
    loan_interest_rate = st.number_input("Loan interest rate (e.g., 0.05 for 5%)",
                                         min_value=0.0000,
                                         max_value=1.0000,
                                         value=0.0500,    # 5% default
                                         step=0.0001      # 0.01% increments 
    )
    loan_term_years = st.number_input("Loan term in years",
                                      min_value=0, max_value=40, value=10
    )
    part_time_monthly_income = st.number_input("Part-time monthly income during college (for college path)",
                                               min_value=0, value=800, step=100
    )  
       
    starting_salary = st.number_input("Starting full-time Salary",
                                      min_value=0, value=60000, step=1000
    )
    salary_growth_rate = st.number_input("Annual salary growth rate (e.g., 0.03 for 3%)",
                                         min_value=0.0000,
                                         max_value=1.0000,
                                         value=0.0300,     # 3% default
                                         step=0.0001       # 0.01% increments
    )
    
    monthly_expenses = st.number_input("Monthly living expenses",
                                       min_value=0, value=1500, step=100
    )
    training_cost = st.number_input("Cost of any additional training or certifications",
                                    min_value=0, value=0, step=500
        )

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
        "part_time_monthly_income": part_time_monthly_income,
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
    
st.markdown('<div class="scenario-card">', unsafe_allow_html=True)

#--- Single scenario simulation card ---
st.markdown('<div class="section-title">Analyze a single scenario</div>', 
            unsafe_allow_html=True)

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
    
    #---Savings Chart---
    st.markdown("#### Savings over time")
    fig1, ax1 = plt.subplots()
    ax1.plot(projection_df["year"], projection_df["savings"], color=COLOR_SAVINGS, label="Savings")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Amount ($)")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    st.pyplot(fig1)
    
    
    #---Loan Balance Chart---
    st.markdown("#### Loan balance over time")
    fig2, ax2 = plt.subplots()
    ax2.plot(projection_df["year"], projection_df["loan_balance"], color=COLOR_LOAN, label="Loan balance")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Amount ($)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    st.pyplot(fig2)
    
    
    # Summary metrics
    final_row = projection_df.iloc[-1]
    st.metric("Savings at end of simulation", f"${final_row['savings']:,.0f}")
    st.metric("Remaining loan balance", f"${final_row['loan_balance']:,.0f}")
    
st.markdown('</div>', unsafe_allow_html=True)

st.subheader("Saved Scenarios")
st.dataframe(scenarios_df)

st.write("Number of scenarios:", len(scenarios_df))


#--- Comparison card ---
st.markdown('<div class="scenario-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Compare two scenarios</div>',
            unsafe_allow_html=True)

if len(scenarios_df) < 2:
    st.info("You need at least two saved scenarios to compare. Add more above.")
else:
    # A multiselect to choose 2 scenarios to compare
    selected_names = st.multiselect(
        "Choose two scenarios to compare",
        options=scenarios_df["name"].tolist(),
        default=scenarios_df["name"].tolist()[:2],  #first two by default
    )
    
    if len(selected_names) != 2:
        st.warning("Please select exactly two scenarios.")
    else:
        name_a, name_b = selected_names
        
        row_a = scenarios_df[scenarios_df["name"] == name_a].iloc[0]
        row_b = scenarios_df[scenarios_df["name"] == name_b].iloc[0]
        
        proj_a = simulate_scenario(row_a)
        proj_b = simulate_scenario(row_b)
        
        # Aligns to the same number of years (shortest of the two)
        max_years = min(proj_a["year"].max(), proj_b["year"].max())
        proj_a = proj_a[proj_a["year"] <= max_years]
        proj_b = proj_b[proj_b["year"] <= max_years]
        
        # BUilds a comparison data frame
        compare_df = pd.DataFrame({
            "year": proj_a["year"],
            f"savings_{name_a}": proj_a["savings"].values,
            f"savings_{name_b}": proj_b["savings"].values,
        }).set_index("year")
        
        st.markdown("#### Savings comparison")
        
        fig3, ax3 = plt.subplots()
        ax3.plot(
            compare_df.index,
            compare_df.iloc[:, 0],
            color=COLOR_SCENARIO_A, label=name_a)
        ax3.plot(
            compare_df.index,
            compare_df.iloc[:, 1],
            color=COLOR_SCENARIO_B, label=name_b)
        
        ax3.set_xlabel("Year")
        ax3.set_ylabel("Savings ($)")
        ax3.grid(True, alpha=0.3)
        ax3.legend(title="Scenario")
        st.pyplot(fig3)
        
        # Summary table
        final_a = proj_a.iloc[-1]
        final_b = proj_b.iloc[-1]
        
        st.write("Summary after final simulated year:")
        
        summary_df = pd.DataFrame(
            {
                "scenario": [name_a, name_b],
                "path_type": [row_a["path_type"], row_b["path_type"]],
                "final_savings": [final_a["savings"], final_b["savings"]],
                "final_loan_balance": [
                    final_a["loan_balance"],
                    final_b["loan_balance"],
                    ],
            }
        )
        st.dataframe(summary_df)
        
st.markdown("</div>", unsafe_allow_html=True)