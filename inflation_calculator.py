# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 12:13:24 2024

@author: Alexander.Frei
"""
import streamlit as st
import pandas as pd

# Load the dataset
data = pd.read_csv('May2020_Full_City.csv')

# Ensure the 'Date' column is parsed as datetime
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

def get_may_data(year):
    """Filter the dataset for May of a specific year."""
    return data[(data['Date'].dt.year == year) & (data['Date'].dt.month == 5)]

def calculate_percentage_change(old_value, new_value):
    """Calculate the percentage change from old_value to new_value."""
    if old_value == 0:
        return float('inf')
    return ((new_value - old_value) / old_value) * 100

def calculate_inflation(selected_items, amounts, base_year, comparison_date):
    """Calculate the inflation for the selected items and amounts between two dates."""
    base_year_data = get_may_data(base_year).select_dtypes(include='number').mean()
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

# Streamlit App
st.title('Personal Inflation Calculator')
st.write("Devoloped by Alexander Frei")

# Select Base Year
base_year = st.selectbox('Select Base Year', range(2014, 2024))

# Get the latest date in the dataset for comparison (May of the latest year)
latest_date = data['Date'].max()
latest_year = latest_date.year if latest_date is not pd.NaT else 2024  # Default to 2024 if date parsing fails
latest_date = f"{latest_year}-05-01"

# List of Items
items = data.columns[1:]
selected_items = st.multiselect('Select Items', items)

# Input Amounts
amounts = []
for item in selected_items:
    amount = st.number_input(f'Enter amount for {item}', min_value=0, value=1, step=1)
    amounts.append(amount)

if st.button('Calculate Inflation'):
    inflation_data = calculate_inflation(selected_items, amounts, base_year, latest_date)
    
    st.markdown("### Summary")
    st.write(f"**Total May {base_year} Cost:** ${inflation_data['total_base_year_cost']:.2f}")
    st.write(f"**Total May {latest_year} Cost:** ${inflation_data['total_comparison_year_cost']:.2f}")
    st.write(f"**Cost Difference:** ${inflation_data['cost_difference']:.2f}")
    st.write(f"**Percentage Change:** {inflation_data['percentage_change']:.2f}%")
    
    st.write('### Individual Items:')
    
    for item, values in inflation_data.items():
        if item not in ['total_base_year_cost', 'total_comparison_year_cost', 'cost_difference', 'percentage_change']:
            item_name = item.split(' - ')[1] if ' - ' in item else item
            st.markdown(f"**{item_name}**")
            st.write(f" - May {base_year} Price: ${values['base_year_price']:.2f}")
            st.write(f" - May {latest_year} Price: ${values['comparison_year_price']:.2f}")
            st.write(f" - May {base_year} Cost: ${values['base_year_cost']:.2f}")
            st.write(f" - May {latest_year} Cost: ${values['comparison_year_cost']:.2f}")
            st.write("---")
    
    

