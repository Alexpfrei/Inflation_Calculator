# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 12:13:24 2024

@author: Alexander.Frei
"""
import streamlit as st
import pandas as pd
import altair as alt

# Load the dataset
data = pd.read_csv('June2024_Full_City.csv')

# Ensure the 'Date' column is parsed as datetime
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

def get_june_data(year):
    """Filter the dataset for June of a specific year and drop rows with NaN values."""
    return data[(data['Date'].dt.year == year) & (data['Date'].dt.month == 6)]

def calculate_percentage_change(old_value, new_value):
    """Calculate the percentage change from old_value to new_value."""
    if old_value == 0:
        return float('inf')
    return ((new_value - old_value) / old_value) * 100

def calculate_inflation(selected_items, amounts, base_year, comparison_date):
    """Calculate the inflation for the selected items and amounts between two dates."""
    base_year_data = get_june_data(base_year).select_dtypes(include='number').mean()
    comparison_year_data = data[data['Date'] == comparison_date].select_dtypes(include='number').mean()
    
    inflation_data = {}
    total_base_year_cost = 0
    total_comparison_year_cost = 0
    
    for item, amount in zip(selected_items, amounts):
        base_year_price = base_year_data.get(item)
        comparison_year_price = comparison_year_data.get(item)
        
        if base_year_price is None or comparison_year_price is None:
            continue
        
        base_year_cost = base_year_price * amount
        comparison_year_cost = comparison_year_price * amount
        
        inflation_data[item] = {
            'amount': amount,
            'base_year_price': base_year_price,
            'comparison_year_price': comparison_year_price,
            'base_year_cost': base_year_cost,
            'comparison_year_cost': comparison_year_cost
        }
        
        total_base_year_cost += base_year_cost
        total_comparison_year_cost += comparison_year_cost
    
    inflation_data['total_base_year_cost'] = total_base_year_cost
    inflation_data['total_comparison_year_cost'] = total_comparison_year_cost
    inflation_data['cost_difference'] = total_comparison_year_cost - total_base_year_cost
    inflation_data['percentage_change'] = calculate_percentage_change(total_base_year_cost, total_comparison_year_cost)
    
    return inflation_data

def plot_total_basket_cost(selected_items, amounts):
    """Plot the total basket cost of selected items over the years using Altair."""
    # Filter the data for selected items and drop rows with NaN values
    item_data = data[['Date'] + list(selected_items)].dropna()
    
    # Calculate the total cost of the basket for each month
    item_data['TotalCost'] = 0
    for item, amount in zip(selected_items, amounts):
        item_data['TotalCost'] += item_data[item] * amount
    
    # Group by month and sum the total cost
    item_data = item_data.groupby(item_data['Date'].dt.to_period('M')).sum(numeric_only=True)
    item_data.index = item_data.index.to_timestamp()
    
    # Create a DataFrame for the total cost over time
    total_cost_df = item_data[['TotalCost']].reset_index()
    
    # Plot the total basket cost over time using Altair
    chart = alt.Chart(total_cost_df).mark_line(point=True).encode(
        x=alt.X('Date:T', axis=alt.Axis(format='%Y', title='Date')),
        y=alt.Y('TotalCost:Q', title='Total Cost', scale=alt.Scale(zero=False), axis=alt.Axis(format='$,.2f')),
        tooltip=[alt.Tooltip('Date:T', title='Date', format='%Y-%m'), alt.Tooltip('TotalCost:Q', title='Total Cost', format='$,.2f')]
    ).properties(
        width=800,
        height=400
    )
    
    st.altair_chart(chart)

# Streamlit App
st.title('Personal Inflation Calculator')
st.write("Developed by Alexander Frei")

# Select Base Year
base_year = st.selectbox('Select Base Year', range(2014, 2024))

# Get the latest date in the dataset for comparison (June of the latest year)
latest_date = data['Date'].max()
latest_year = latest_date.year if latest_date is not pd.NaT else 2024  # Default to 2024 if date parsing fails
latest_date = f"{latest_year}-06-01"

# Filter items based on the presence of data for the selected base year
base_year_data = get_june_data(base_year)
available_items = base_year_data.dropna(axis=1).columns[1:]  # Drop columns with NaN values and exclude the 'Date' column

# Initialize session state for selected items and amounts
if 'selected_items' not in st.session_state:
    st.session_state.selected_items = []
if 'amounts' not in st.session_state:
    st.session_state.amounts = []

# Display "Average Bundle" and "Redo" buttons in a single row
col1, col2 = st.columns(2)


# This line of code is there To create the example Bundles
with col1:
    if st.button("Average Bundle"):
        st.session_state.selected_items = [
            "APU0000708111 - Eggs, grade A, large, per doz.",
            "APU0000709112 - Milk, fresh, whole, fortified, per gal. (3.8 lit)",
            "APU0000702111 - Bread, white, pan, per lb. (453.6 gm)",
            "APU0000FF1101 - Chicken breast, boneless, per lb. (453.6 gm)",
            "APU0000701312 - Rice, white, long grain, uncooked, per lb. (453.6 gm)",
            "APU0000712112 - Potatoes, white, per lb. (453.6 gm)",
            "APU0000703112 - Ground beef, 100% beef, per lb. (453.6 gm)",
            "APU0000711311 - Oranges, Navel, per lb. (453.6 gm)",
            "APU0000711211 - Bananas, per lb. (453.6 gm)",
            "APU0000712311 - Tomatoes, field grown, per lb. (453.6 gm)",
            "APU000072610 - Electricity per KWH",
            "APU000072620 - Utility (piped) gas per therm",
            "APU000074714 - Gasoline, unleaded regular, per gallon/3.785 liters",
            "APU0000710212 - Cheddar cheese, natural, per lb. (453.6 gm)",
            "APU0000720111 - Malt beverages, all types, all sizes, any origin, per 16 oz. (473.2 ml)",
            "APU0000720311 - Wine, red and white table, all sizes, any origin, per 1 liter (33.8 oz)",
            "APU0000702421 - Cookies, chocolate chip, per lb. (453.6 gm)",
            "APU0000717311 - Coffee, 100%, ground roast, all sizes, per lb. (453.6 gm)",
            "APU0000710411 - Ice cream, prepackaged, bulk, regular, per 1/2 gal. (1.9 lit)",
            "APU0000713111 - Orange juice, frozen concentrate, 12 oz. can, per 16 oz. (473.2 ml)"
        ]
        st.session_state.amounts = [6, 12, 8, 10, 8, 15, 10, 10, 12, 8, 1000, 30, 80, 4, 48, 4, 4, 4, 4, 8]

with col2:
    if st.button('Redo'):
        st.session_state.selected_items = []
        st.session_state.amounts = []
        st.experimental_rerun()

# Display the multi-select box with the selected items, allowing users to add more items
selected_items = st.multiselect('Select Items', available_items, default=st.session_state.selected_items)

# Input amounts for the selected items
amounts = []
for item in selected_items:
    default_amount = st.session_state.amounts[st.session_state.selected_items.index(item)] if item in st.session_state.selected_items else 1
    amount = st.number_input(f'Enter amount for {item}', min_value=0, value=default_amount, step=1)
    amounts.append(amount)

# Only update session state when the "Calculate Inflation" button is clicked
if st.button('Calculate Inflation'):
    # Update session state with selected items and amounts
    st.session_state.selected_items = selected_items
    st.session_state.amounts = amounts

    # Display the summary
    inflation_data = calculate_inflation(st.session_state.selected_items, st.session_state.amounts, base_year, latest_date)
    
    st.markdown("### Summary")
    st.write(f"**Total June {base_year} Cost:** ${inflation_data['total_base_year_cost']:.2f}")
    st.write(f"**Total June {latest_year} Cost:** ${inflation_data['total_comparison_year_cost']:.2f}")
    st.write(f"**Cost Difference:** ${inflation_data['cost_difference']:.2f}")
    st.write(f"**Percentage Change:** {inflation_data['percentage_change']:.2f}%")
    
    # Plot the total basket cost over time
    st.markdown("### Total Cost of Selected Basket Over Time")
    plot_total_basket_cost(st.session_state.selected_items, st.session_state.amounts)
    
    # Display individual items
    st.write('### Individual Items:')
    
    for item, values in inflation_data.items():
        if item not in ['total_base_year_cost', 'total_comparison_year_cost', 'cost_difference', 'percentage_change']:
            item_name = item.split(' - ')[1] if ' - ' in item else item
            st.markdown(f"**{item_name}**")
            st.write(f" - June {base_year} Price: ${values['base_year_price']:.2f}")
            st.write(f" - June {latest_year} Price: ${values['comparison_year_price']:.2f}")
            st.write(f" - June {base_year} Cost: ${values['base_year_cost']:.2f}")
            st.write(f" - June {latest_year} Cost: ${values['comparison_year_cost']:.2f}")
            st.write("---")
