import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
st.set_page_config(page_title="Total Indent Calculator")


# Load data

filenames = []
uploaded_files = st.file_uploader("Upload a Dataset", type=["csv", "txt" , "excel"], accept_multiple_files=True)
if uploaded_files: 
    for uploaded_file in uploaded_files:
       filenames.append(uploaded_file)
       st.write("Filename: ", uploaded_file.name)


def indent_calculator(df):
    # Filter for only delivered orders
    df = df[df['status'] == 'Delivered']

    # Group by SKU and aggregate quantity and price
    df = df.groupby('sku').agg({'quantity': 'sum', 'price': 'sum', 'name': 'first'})

    # Define default parameter values
    defaults = {'weekend_multiplier': 1.2,
                'marketing_spend_variable': 1.08,
                'retention_projection': 1.0,
                'festival_offer': 1.0,
                'offer_on_product': 1.0,
                'market_closure': 1.0,
                'buffer': 1.05,
                'shortfall': 4.0,
                'closing_stock': 0.0}

    # Define Streamlit app layout
    st.header("Total Indent Calculator")

    # Create sliders for input parameters
    params = {}
    for key, val in defaults.items():
        params[key] = st.sidebar.slider(key, min_value=0.0, max_value=20.0, value=val, step=0.01)

    # Calculate total indent with updated parameter values
    df['total_indent'] = ((df['quantity'] * params['weekend_multiplier'] * params['marketing_spend_variable'] * params['retention_projection'] * params['festival_offer'] * params['offer_on_product'] * params['market_closure'] * params['buffer']) - params['closing_stock']) + params['shortfall']

    # Sort DataFrame by total_indent in ascending order and reset index
    df = df.sort_values('total_indent').reset_index()

    df['sku_name'] = df['sku'] + ' - ' + df['name']
    
    # Create bar chart of total indent for each SKU
    fig = px.bar(df, x='total_indent', y='sku_name', orientation='h', 
                text='total_indent', title='Total Indent by SKU',
                labels={'total_indent':'Total Indent', 'sku':'SKU - Product Name'},
                width=800, height=4000)

    # Add text labels to bar chart showing total indent values
    fig.update_traces(texttemplate='%{text:.2f}', textposition='inside')

    # Display bar chart with text labels
    st.plotly_chart(fig)

    # Add a download button for the updated DataFrame
    csv = df.to_csv().encode('utf-8')
    st.download_button(
        label="Download updated DataFrame as CSV",
        data=csv,
        file_name="updated_dataframe.csv",
        mime="text/csv"
    )


if filenames is not None:
    df = pd.concat([pd.read_csv(filename) for filename in filenames])
    indent_calculator(df)
# df = pd.read_csv("orders (3).csv")

