import requests
import pandas as pd
import streamlit as st

# Fetch the AMFI mutual fund NAV data
def fetch_amfi_nav_data():
    """Fetch the latest mutual fund NAV data from AMFI."""
    url = 'https://www.amfiindia.com/spages/NAVAll.txt'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.text
            return data
        else:
            st.write("Error fetching AMFI NAV data.")
            return None
    except Exception as e:
        st.write(f"Error: {e}")
        return None

# Parse the AMFI NAV data
def parse_amfi_nav_data(data):
    """Parse the NAV data and return a DataFrame with mutual fund details."""
    lines = data.splitlines()
    parsed_data = []

    for line in lines[1:]:
        columns = line.split(';')
        if len(columns) >= 6:
            # Extract relevant columns
            scheme_code = columns[0]
            scheme_name = columns[3]
            nav = columns[4]
            parsed_data.append([scheme_code, scheme_name, nav])
    
    # Create a DataFrame
    df = pd.DataFrame(parsed_data, columns=["Scheme Code", "Scheme Name", "NAV"])
    df['NAV'] = pd.to_numeric(df['NAV'], errors='coerce')  # Convert NAV to numeric
    return df.dropna()

# Filter mutual funds based on user criteria
def recommend_mutual_funds(df, monthly_investment, target_amount, investment_horizon):
    """Recommend mutual funds based on user inputs."""
    recommendations = []
    
    for _, row in df.iterrows():
        avg_return = 0.12  # Placeholder for annual return (12%), you can refine this
        time_to_target = calculate_time_to_target(0, monthly_investment, target_amount, avg_return)
        
        if time_to_target <= investment_horizon:
            recommendations.append({
                'scheme_name': row['Scheme Name'],
                'nav': row['NAV'],
                'time_to_target': time_to_target
            })
    
    # Sort by time to target
    recommendations = sorted(recommendations, key=lambda x: x['time_to_target'])
    return recommendations

# Helper function to calculate time to reach the target
def calculate_time_to_target(initial_investment, monthly_investment, target_amount, avg_return):
    months = 0
    total_investment = initial_investment

    while total_investment < target_amount:
        total_investment += monthly_investment
        total_investment *= (1 + avg_return / 12)  # Monthly compounding
        months += 1

    return months / 12  # Convert months to years

# Streamlit App
def app():
    st.title("Mutual Fund Recommendation Tool (AMFI Data)")
    
    # Fetch and parse the mutual fund NAV data from AMFI
    amfi_data = fetch_amfi_nav_data()
    
    if amfi_data:
        df = parse_amfi_nav_data(amfi_data)
        st.write(f"Loaded {len(df)} mutual funds from AMFI.")

        # User inputs
        monthly_investment = st.number_input("Enter Monthly Investment Amount (INR)", min_value=100, value=10000)
        target_return = st.number_input("Enter Target Amount (INR)", min_value=1000, value=1000000)
        investment_horizon = st.slider("Investment Horizon (years)", min_value=1, max_value=30, value=10)

        if st.button("Get Recommendations"):
            # Fetch recommendations based on user input
            recommendations = recommend_mutual_funds(df, monthly_investment, target_return, investment_horizon)
            
            if recommendations:
                st.write("Recommended Mutual Funds:")
                for rec in recommendations:
                    st.write(f"Scheme Name: {rec['scheme_name']}, NAV: {rec['nav']:.2f}, Time to Target: {rec['time_to_target']:.2f} years")
            else:
                st.write("No suitable mutual funds found for the given criteria.")

# Run the Streamlit app
if __name__ == "__main__":
    app()
