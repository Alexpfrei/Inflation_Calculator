import streamlit as st
import pandas as pd
import altair as alt

# Load the dataset
data = pd.read_csv('test1.csv')

# Ensure the 'Date' column is parsed as datetime
data['Date'] = pd.to_datetime(data['Date'], format='%m/%d/%y', errors='coerce')

# Get the latest date in the dataset for comparison (June of the latest year)
latest_date = data['Date'].max()
latest_year = latest_date.year if latest_date is not pd.NaT else 2024  # Default to 2024 if date parsing fails
latest_date = f"{latest_year}-06-01"

goods_to_series_id = {
    "Eggs - doz.": "APU0000708111",
    "Orange juice - 16 oz.": "APU0000713111",
    "Gasoline, all types - gallon": "APU00007471A",
    "Gasoline, regular - gallon": "APU000074714",
    "Gasoline, premium - gallon": "APU000074716",
    "Gasoline, midgrade - gallon": "APU000074715",
    "Automotive diesel - gallon": "APU000074717",
    "Sugar - lb.": "APU0000715211",
    "Fuel oil #2 - gallon": "APU000072511",
    "Chocolate Chip Cookies - lb.": "APU0000702421",
    "All soft drinks, 12 pk - 12 oz.": "APU0000FN1102",
    "Yogurt - 8 oz.": "APU0000FJ4101",
    "Potato chips - 16 oz.": "APU0000718311",
    "All soft drinks - 2 liters": "APU0000FN1101",
    "All Ham - lb.": "APU0000FD2101",
    "Coffee - lb.": "APU0000717311",
    "Beef Steaks - lb.": "APU0000FC3101",
    "Ground beef - lb.": "APU0000703112",
    "Chuck roast - lb.": "APU0000703213",
    "Electricity - KWH": "APU000072610",
    "Flour - lb.": "APU0000701111",
    "Round roast - lb.": "APU0000703311",
    "White Bread - lb.": "APU0000702111",
    "Beef Roasts - lb.": "APU0000FC2101",
    "Steak, round - lb.": "APU0000703511",
    "Wheat Bread - lb.": "APU0000702212",
    "Steak, Sirloin - lb.": "APU0000703613",
    "Chicken breast - lb.": "APU0000FF1101",
    "Whole Chicken - lb.": "APU0000706111",
    "White Rice - lb.": "APU0000701312",
    "Butter - lb.": "APU0000FS1101",
    "All Other Beef - lb.": "APU0000FC4101",
    "All Other Pork - lb.": "APU0000FD4101",
    "Ground chuck, 100% beef - lb.": "APU0000703111",
    "All uncooked Ground beef - lb.": "APU0000FC1101",
    "Potatoes - lb.": "APU0000712112",
    "Ham - lb.": "APU0000704312",
    "Utility (piped) gas - therm": "APU000072620",
    "Beef for stew - lb.": "APU0000703432",
    "Ground beef, extra lean - lb.": "APU0000703113",
    "Ice cream - 1/2 gal.": "APU0000710411",
    "All Pork Chops - lb.": "APU0000FD3101",
    "Beans - lb.": "APU0000714233",
    "Malt beverages - 16 oz.": "APU0000720111",
    "Oranges - lb.": "APU0000711311",
    "Bacon - lb.": "APU0000704111",
    "Milk, low-fat - gal.": "APU0000FJ1101",
    "Chops, center cut, bone-in - lb.": "APU0000704211",
    "American processed cheese - lb.": "APU0000710211",
    "Chicken legs, bone-in - lb.": "APU0000706212",
    "Milk, whole - gal.": "APU0000709112",
    "Chops, boneless - lb.": "APU0000704212",
    "Wine - 1 liter": "APU0000720311",
    "Spaghetti and macaroni - lb.": "APU0000701322",
    "Bananas - lb.": "APU0000711211",
    "Cheddar cheese - lb.": "APU0000710212",
    "Tomatoes - lb.": "APU0000712311",
    "Strawberries - 12 oz.": "APU0000711415"
}

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

def generate_citation(selected_items):
    series_ids = [goods_to_series_id[item] for item in selected_items if item in goods_to_series_id]
    series_ids_str = ", ".join(series_ids)
    citation = f"""
    Source: U.S. Bureau of Labor Statistics, Average Price Data, Series {series_ids_str}, accessed July 15, 2024, 
    <a href='https://download.bls.gov/pub/time.series/ap/ap.series' target='_blank' style='color: #222944 !important;'>https://download.bls.gov/pub/time.series/ap/ap.series</a>
    """
    return citation

# Your plotting function with citation display
def plot_total_basket_cost(selected_items, amounts):
    """Plot the total basket cost of selected items over the years using Altair."""
    # Filter the data for selected items and drop rows with NaN values
    item_data = data[['Date'] + list(selected_items)].dropna()
    
    # Convert all selected item columns to numeric, coerce errors to NaN, then fill NaNs with 0
    item_data[selected_items] = item_data[selected_items].apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # Calculate the total cost of the basket for each month
    item_data['TotalCost'] = 0
    for item, amount in zip(selected_items, amounts):
        item_data['TotalCost'] += item_data[item] * amount
    
    # Group by month and sum the total cost
    item_data = item_data.groupby(item_data['Date'].dt.to_period('M')).sum(numeric_only=True)
    item_data.index = item_data.index.to_timestamp()
    
    # Create a DataFrame for the total cost over time
    total_cost_df = item_data[['TotalCost']].reset_index()
    
    # Define the chart background color and text properties
    chart_background_color = '#F3F5F8'
    text_color = '#222944'
    font_family = 'Gotham'
    font_size = 16
    font_weight = 'bold'
    title_font_size = 20
    title_font_weight = 'bold'
    chart_title = 'Total Cost of Selected Basket Over Time'

    # Plot the total basket cost over time using Altair
    chart = alt.Chart(total_cost_df).mark_line(point=True).encode(
        x=alt.X('Date:T', axis=alt.Axis(format='%Y', title='', tickCount='year', grid=True, tickSize=10, labelFontSize=font_size, labelFontWeight=font_weight)),
        y=alt.Y('TotalCost:Q', title='Total Cost', scale=alt.Scale(zero=False), axis=alt.Axis(
            format='$,.0f',
            titleFontSize=title_font_size,
            titleFontWeight=title_font_weight,
            labelFontSize=font_size,
            labelFontWeight=font_weight
        )),
        tooltip=[alt.Tooltip('TotalCost:Q', title='Total Cost', format='$,.2f')]
    ).properties(
        title=chart_title,
        width=800,
        height=400,
        background=chart_background_color
    ).configure_view(
        fill=chart_background_color,
        stroke=text_color,  # Set the border color
        strokeWidth=2  # Set the border width
    ).configure_axis(
        labelFont=font_family,
        titleFont=font_family,
        labelColor=text_color,
        titleColor=text_color,
        labelFontSize=font_size,
        titleFontSize=title_font_size,
        labelFontWeight=font_weight,
        titleFontWeight=title_font_weight
    ).configure_title(
        font=font_family,
        fontSize=title_font_size,
        fontWeight=title_font_weight,
        anchor='middle',  # Center the title
        color=text_color
    ).configure_legend(
        labelFont=font_family,
        titleFont=font_family,
        labelColor=text_color,
        titleColor=text_color,
        labelFontSize=font_size,
        titleFontSize=title_font_size,
        labelFontWeight=font_weight,
        titleFontWeight=title_font_weight
    )

    st.altair_chart(chart)
    
    # Display the citation with proper styling
    citation = generate_citation(selected_items)
    
    st.markdown(f"""
    <div style='text-align: left; font-family: Gotham, sans-serif !important; color: #222944;  margin-top: -25px;;'>
        <span style='font-size: 10px;'>{citation}</span>
    </div>
    """, unsafe_allow_html=True)


######################################################################################## Custom style portion ########################################################################################
######################################################################################################################################################################################################
# This creates custom Formatting for dropdown menus and buttons 
def generate_custom_css(button_bg_color, button_font_color, dropdown_bg_color, dropdown_font_color, number_input_bg_color, number_input_font_color, label_color, highlight_color, background_color):
    custom_css = f'''
    <style>
    /* Button Styling */
    .stButton > button {{
        background-color: {button_bg_color} !important;
        color: {button_font_color} !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 10px 20px !important;
        font-family: 'Gotham', sans-serif !important;
    }}

    .stButton > button:hover {{
        background-color: {highlight_color} !important;
    }}

    /* General dropdown styling */
    div[data-baseweb="select"] {{
        background-color: {dropdown_bg_color} !important;
        color: {dropdown_font_color} !important;
        font-family: 'Gotham', sans-serif !important;
    }}

    /* Styling the control (input field) */
    div[data-baseweb="select"] > div {{
        background-color: {dropdown_bg_color} !important;
        color: {dropdown_font_color} !important;
        font-family: 'Gotham', sans-serif !important;
    }}

    /* Styling the selected value */
    div[data-baseweb="select"] .css-1uccc91-singleValue {{
        color: {dropdown_font_color} !important;
        font-family: 'Gotham', sans-serif !important;
    }}

    /* Styling the input field */
    div[data-baseweb="select"] input {{
        background-color: {dropdown_bg_color} !important;
        color: {dropdown_font_color} !important;
        font-family: 'Gotham', sans-serif !important;
    }}

    /* Styling the dropdown indicator (arrow) */
    div[data-baseweb="select"] .css-1okebmr-indicatorSeparator {{
        background-color: {dropdown_bg_color} !important;
    }}

    div[data-baseweb="select"] .css-tlfecz-indicatorContainer {{
        color: {dropdown_font_color} !important;
    }}

    /* Styling the dropdown menu */
    ul[data-testid="stVirtualDropdown"] {{
        background-color: {dropdown_bg_color} !important;
        color: {dropdown_font_color} !important;
        font-family: 'Gotham', sans-serif !important;
    }}

    /* Styling the list of options */
    ul[data-testid="stVirtualDropdown"] > div {{
        background-color: {dropdown_bg_color} !important;
        color: {dropdown_font_color} !important;
        font-family: 'Gotham', sans-serif !important;
    }}

    /* Styling individual options */
    ul[data-testid="stVirtualDropdown"] li {{
        background-color: {dropdown_bg_color} !important;
        color: {dropdown_font_color} !important;
        font-family: 'Gotham', sans-serif !important;
    }}

    /* Hover effect for options */
    ul[data-testid="stVirtualDropdown"] li:hover {{
        background-color: {highlight_color} !important;
        color: {button_font_color} !important; /* Changed to button font color */
    }}

    /* Styling for the options when selected */
    ul[data-testid="stVirtualDropdown"] li[aria-selected="true"] {{
        background-color: {highlight_color} !important;
        color: {button_font_color} !important; /* Changed to button font color */
    }}

    /* General number input styling */
    div[data-testid="stNumberInput"] input {{
        background-color: {number_input_bg_color} !important;
        color: {number_input_font_color} !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 10px !important;
        font-family: 'Gotham', sans-serif !important;
    }}

    /* Hover effect for the number input */
    div[data-testid="stNumberInput"] input:hover {{
        background-color: {highlight_color} !important;
    }}

    /* Focus effect for the number input */
    div[data-testid="stNumberInput"] input:focus {{
        background-color: {highlight_color} !important;
        outline: none !important;
    }}

    /* Label styling */
    label {{
        color: {label_color} !important;
        font-family: 'Gotham', sans-serif !important;
    }}

    /* Custom label styling for select boxes */
    .stSelectbox label {{
        color: {label_color} !important;
        font-family: 'Gotham', sans-serif !important;
    }}

    /* Styling the highlighted buttons and selected items */
    .st-ar.st-br.st-bq.st-ed.st-ee.st-af {{
        background-color: {highlight_color} !important;
        color: {dropdown_font_color} !important;
        font-family: 'Gotham', sans-serif !important;
    }}

    /* Specific styling for the close buttons within selected items */
    div.st-ak.st-al.st-bd.st-be.st-bf.st-as.st-bg.st-ct.st-ar.st-c4.st-c5.st-bk.st-c7 > span {{
        background-color: {highlight_color} !important;
        color: {dropdown_font_color} !important;
        font-family: 'Gotham', sans-serif !important;
    }}

    /* Background color */
    .stApp {{
        background-color: {background_color} !important;
        font-family: 'Gotham', sans-serif !important;
    }}

    /* Align input fields */
    .stNumberInput {{
        margin-bottom: 10px;
    }}
    </style>
    '''
    return custom_css

# Applying the custom styles
st.markdown(generate_custom_css(
    button_bg_color="#8CB2CD",  
    button_font_color="#222944",
    dropdown_bg_color="#426172",  # Heritage Cyan
    dropdown_font_color="white",
    number_input_bg_color="#426172",  # Heritage Blue
    number_input_font_color="white",
    label_color="#222944",  # Heritage Navy
    highlight_color="#3b8797",  # Selected Item color (previously Orange)
    background_color="#F3F5F8"  # Glacier Blue for a light background
), unsafe_allow_html=True)

######################################################################################################################################################################################################

# Initialize session state for selected items and amounts
if 'selected_items' not in st.session_state:
    st.session_state.selected_items = []
if 'amounts' not in st.session_state:
    st.session_state.amounts = []

# New titles with custom CSS
st.markdown('<h1 style="color:#222944;font-family:\'Gotham\';">Personal Inflation Calculator</h1>', unsafe_allow_html=True)

with st.container():
    # Text to display
    #text_to_display = "Welcome to the Personal Inflation Calculator, an advanced tool designed to provide insights into how inflation impacts the cost of a selected basket of goods over time. This application allows users to choose from a variety of commonly purchased items, enter custom amounts, and compare the total cost from a chosen base year to the most recent available data. You can also add your own goods or select a predefined basket modeled after the average consumption of a family of four. Our data stems from the U.S. Bureau of Labor Statistics' Average Price Data series, offering reliable and up-to-date pricing information for a wide range of consumer goods. The tool generates detailed item cost breakdowns and visualizes them in a comprehensive graph, which users can download for further analysis. The Personal Inflation Calculator is ideal for researchers, policymakers, and anyone interested in understanding the nuances of inflation and its effect on household expenses. Explore the tool and gain valuable insights into your financial planning and research."
    text_to_display = """
    Welcome to the Personal Inflation Calculator, an advanced tool designed to provide insights into how inflation impacts the cost of a selected basket of goods over time.<br><br>
    This application allows users to choose from a variety of commonly purchased items, enter custom amounts, and compare the total cost from a chosen base year to the most recent available data.
    One can also add your own goods or select a predefined basket modeled after the average consumption of a family of four.<br><br>
    Our data stems from the U.S. Bureau of Labor Statistics' Average Price Data series, offering reliable and up-to-date pricing information for a wide range of consumer goods.
    The tool generates detailed item cost breakdowns and visualizes them in a comprehensive graph, which users can download for further analysis.
    The Personal Inflation Calculator is ideal for researchers, policymakers, and anyone interested in understanding the nuances of inflation and its effect on household expenses.<br><br>
    Explore the tool and gain valuable insights into your financial planning and research.
    """
    # Add custom CSS for styling the container
    st.markdown(
        """
        <style>
        .custom-box {
            border: 2px solid #222944;
            padding: 10px;
            border-radius: 5px;
            background-color: #f9f9f9;
            margin-top: -20px;
            margin-bottom: 20px;
            color: #222944; /* Text color */
            font-family: 'Gotham', sans-serif; /* Font family */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display the text within the styled container
    st.markdown(f"<div class='custom-box'>{text_to_display}</div>", unsafe_allow_html=True)    

# Display "Average Bundle" and "Calculate Inflation" and "Redo" buttons in a single row
upper_col1, upper_col2, upper_col3 = st.columns(3)

with upper_col1:
    if st.button("Average Bundle"):
        st.session_state.selected_items = [
            "Eggs - doz.",
            "Milk, whole - gal.",
            "White Bread - lb.",
            "Chicken breast - lb.",
            "White Rice - lb.",
            "Potatoes - lb.",
            "Ground beef - lb.",
            "Oranges - lb.",
            "Bananas - lb.",
            "Tomatoes - lb.",
            "Electricity - KWH",
            "Utility (piped) gas - therm",
            "Gasoline, regular - gallon",
            "Cheddar cheese - lb.",
            "Malt beverages - 16 oz.",
            "Wine - 1 liter",
            "Chocolate Chip Cookies - lb.",
            "Coffee - lb.",
            "Ice cream - 1/2 gal.",
            "Orange juice - 16 oz."
        ]
        st.session_state.amounts = [6, 12, 8, 10, 8, 15, 10, 10, 12, 8, 1000, 30, 80, 4, 48, 4, 4, 4, 4, 8]

with upper_col2:
    calculate_button = st.button('Calculate Inflation')

with upper_col3:
    if st.button('Redo'):
        st.session_state.selected_items = []
        st.session_state.amounts = []
        st.experimental_rerun()

# Display "Select Base Year" and "Select Items" dropdowns next to each other
col1, col2 = st.columns([0.55, 3])  # Adjust the ratio to make col1 narrower and col2 wider

with col1:
    base_year = st.selectbox('Select Base Year', range(2014, 2024))

with col2:
    # Filter items based on the presence of data for the selected base year
    base_year_data = get_june_data(base_year)
    available_items = base_year_data.dropna(axis=1).columns[1:]  # Drop columns with NaN values and exclude the 'Date' column
    selected_items = st.multiselect('Select Items', available_items, default=st.session_state.selected_items)

if selected_items:
    st.markdown('<h4 style="color:#222944;font-family:\'Gotham\';">Enter Custom Amounts</h4>', unsafe_allow_html=True)


# Input amounts for the selected items
amounts = []
cols = st.columns(4)  # Create four columns for the number inputs
for idx, item in enumerate(selected_items):
    col = cols[idx % 4]  # Rotate through the four columns
    with col:
        default_amount = st.session_state.amounts[st.session_state.selected_items.index(item)] if item in st.session_state.selected_items else 1
        amount = st.number_input(f'{item}', min_value=0, value=default_amount, step=1)
        amounts.append(amount)


# Only update session state when the "Calculate Inflation" button is clicked
if calculate_button:
    # Update session state with selected items and amounts
    st.session_state.selected_items = selected_items
    st.session_state.amounts = amounts

    # Display the summary and plot the total basket cost over time
    inflation_data = calculate_inflation(st.session_state.selected_items, st.session_state.amounts, base_year, latest_date)

    st.markdown('<h2 style="color:#222944;font-family:\'Gotham\';">Summary</h2>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="border: 2px solid #222944; border-radius: 10px; padding: 10px; width: 100%; font-family: 'Gotham'; color: #222944;">
        <table style="width:100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #222944;">
                <td style="padding: 8px;"><strong>Total June {base_year} Cost:</strong></td>
                <td style="padding: 8px;">${inflation_data['total_base_year_cost']:.2f}</td>
            </tr>
            <tr style="border-bottom: 1px solid #222944;">
                <td style="padding: 8px;"><strong>Total June {latest_year} Cost:</strong></td>
                <td style="padding: 8px;">${inflation_data['total_comparison_year_cost']:.2f}</td>
            </tr>
            <tr style="border-bottom: 1px solid #222944;">
                <td style="padding: 8px;"><strong>Cost Difference:</strong></td>
                <td style="padding: 8px;">${inflation_data['cost_difference']:.2f}</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><strong>Percentage Change:</strong></td>
                <td style="padding: 8px;">{inflation_data['percentage_change']:.2f}%</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.write("")

    plot_total_basket_cost(st.session_state.selected_items, st.session_state.amounts)

    # Display individual items
    st.markdown('<h2 style="color:#222944;font-family:\'Gotham\';">Individual Items:</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    for idx, (item, values) in enumerate(inflation_data.items()):
        if item not in ['total_base_year_cost', 'total_comparison_year_cost', 'cost_difference', 'percentage_change']:
            quantity = st.session_state.amounts[st.session_state.selected_items.index(item)]
            
            # Select the column to place the content in
            with col1 if idx % 2 == 0 else col2:
                st.markdown(f"""
                <div style="border: 2px solid #222944; border-radius: 10px; padding: 10px; margin-bottom: 10px; width: 100%; font-family: 'Gotham'; color: #222944;">
                    <h3 style='color:#222944;font-family:Gotham; text-decoration: underline;'>{item}</h3>
                    <p style='color:#222944;font-family:Gotham;'><strong>June {base_year} Price per Unit:</strong> ${values['base_year_price']:.2f}</p>
                    <p style='color:#222944;font-family:Gotham;'><strong>June {latest_year} Price per Unit:</strong> ${values['comparison_year_price']:.2f}</p>
                    <p style='color:#222944;font-family:Gotham;'><strong>Total Cost for June {base_year}:</strong> ${values['base_year_cost']:.2f} ({quantity} units x ${values['base_year_price']:.2f} per unit)</p>
                    <p style='color:#222944;font-family:Gotham;'><strong>Total Cost for June {latest_year}:</strong> ${values['comparison_year_cost']:.2f} ({quantity} units x ${values['comparison_year_price']:.2f} per unit)</p>
                </div>
                """, unsafe_allow_html=True)

# Footer section with a solid line
st.markdown("<hr style='border: 1px solid #222944;'>", unsafe_allow_html=True)


st.markdown("""
<style>
.footer {
    font-family: 'Gotham', sans-serif;
    font-size: 14px;
    color: #222944;
    text-align: left;
    margin-top: -20px;
}
.footer a {
    color: #0073e6;
    text-decoration: none;
}
.footer a:hover {
    text-decoration: underline;
}
</style>

<div class="footer">
    <strong>DESIGN AND DEVELOPMENT:</strong> Calculator produced by 
    <a href="https://www.heritage.org/staff/alexander-frei" target="_blank">Alexander Frei</a>
</div>
""", unsafe_allow_html=True)
