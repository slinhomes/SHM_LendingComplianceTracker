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

    # Connect to the database and fetch property addresses
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT flat_number, property_address, city FROM SHMDwellingInfo")
    rows = cursor.fetchall()
    property_addresses = [' '.join(map(str, row)) for row in rows]  # Concatenating the address components

    # Dropdown for selecting property address
    property_address = st.selectbox("Property Address", property_addresses)

    # Additional code for the page goes here
