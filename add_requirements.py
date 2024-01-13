import streamlit as st
import pyodbc

# Function to connect to the Azure SQL database
def create_connection():
    server = 'studenthomesmgmt.database.windows.net'
    database = 'PortfolioManagement'
    username = st.secrets['db_username']
    password = st.secrets['db_password']
    driver = '{ODBC Driver 17 for SQL Server}'  # Adjust the driver if needed
    conn = pyodbc.connect(
        f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
    return conn

def show():
    st.write("Welcome to the Add Requirements Page")

    # Connect to the database and fetch property addresses and IDs
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Dwelling_ID, flat_number, property_address, city FROM SHMDwellingInfo")
    rows = cursor.fetchall()
    addresses = {f'{row[1]} {row[2]}, {row[3]}': row[0] for row in rows}  # Mapping address to DwellingID

    # Dropdown for selecting property address
    selected_address = st.selectbox("Property Address", list(addresses.keys()))

    # Display Dwelling ID and full address
    dwelling_id = addresses[selected_address]
    st.write(f"Dwelling ID: {dwelling_id}")
    st.write(f"Full Address: {selected_address}")

    # Additional code for the page goes here
