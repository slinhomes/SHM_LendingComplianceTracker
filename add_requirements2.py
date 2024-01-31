import streamlit as st
import pyodbc
import pandas as pd
from datetime import timedelta

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

# Function to create the SHMLendingCompliance table
def create_table(conn):
    try:
        sql = '''CREATE TABLE [dbo].[SHMLendingCompliance2] (
                [UID] UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
                [Dwelling_ID] NVARCHAR(50) NULL,
                [Asset_ID] NVARCHAR(50) NULL,
                [Asset_address] NVARCHAR(MAX) NULL,
                [Dwelling_address] NVARCHAR(MAX) NULL,
                [lender] NVARCHAR(50) NULL,
                [condition_title] NVARCHAR(100) NULL,
                [reference] NVARCHAR(100) NULL,
                [requirements] NVARCHAR(MAX) NULL,
                [action_req] NVARCHAR(MAX) NULL,
                [trigger_date] DATE NULL,
                [deadline_period] INT NULL,
                [deadline_date] DATE NULL,
                [fst_reminder] DATE NULL,
                [recurrence] NVARCHAR(50) NULL,
                [loc8me_contact] NVARCHAR(100) NULL,
                [shm_team] NVARCHAR(50) NULL,
                [shm_individual] NVARCHAR(100) NULL,
                [shm_bu] NVARCHAR(100) NULL,
                [added_by] NVARCHAR(50) NULL,
                [entry_date] DATE NULL
            );'''
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)


# Function to insert data into the SHMLendingCompliance table
def insert_data(conn, data):
    insert_sql = '''INSERT INTO SHMLendingCompliance (
                   Dwelling_ID, Asset_ID, Asset_address, Dwelling_address, lender, 
                   condition_title, reference, requirements, action_req, trigger_date,
                   deadline_period, deadline_date, fst_reminder, recurrence, loc8me_contact, 
                   shm_team, shm_individual, shm_bu, added_by, entry_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''

    cur = conn.cursor()
    cur.execute(insert_sql, data)
    conn.commit()

def show():
    #st.write("Welcome to the Add Requirements Page")
    st.markdown("---")  # Page breaker

    # Connect to the database and fetch property addresses and IDs
    conn = create_connection()
    cursor = conn.cursor()

    # Fetch distinct lender
    cursor.execute("SELECT DISTINCT lender FROM SHMLender")
    lenders = [row[0] for row in cursor.fetchall()]
    selected_lender = st.selectbox("Lender", ["Select a lender"] + lenders)

    # Fetch property addresses related to the selected lender
    if selected_lender and selected_lender != "Select a lender":
        query = """
                SELECT DI.Dwelling_ID, DI.Asset_ID, DI.flat_number, DI.property_address, DI.city, DI.propco
                FROM SHMDwellingInfo DI
                JOIN SHMLender L ON DI.Dwelling_ID = L.Dwelling_ID
                WHERE L.lender = ?
                """
        cursor.execute(query, (selected_lender,))
    else:
        # Fetch all properties if no lender is selected
        cursor.execute("SELECT Dwelling_ID, Asset_ID, flat_number, property_address, city, propco FROM SHMDwellingInfo")

    rows = cursor.fetchall()
    asset_address = {f'{row[3]}, {row[4]}': row[1] for row in rows} # Mapping asset address to AssetID
    all_addresses = {f'{row[2]} {row[3]}, {row[4]}': (row[0], row[1], row[5]) for row in rows}  # Mapping detailed address to DwellingID and propco

    # Dropdown for selecting asset address
    selected_asset_address = st.selectbox("Asset Address", ["Select property address"] + list(asset_address.keys()))

    dwelling_id = asset_id = propco = ""  # Initialize dwelling_id, asset_id and propco
    if selected_asset_address != "Select property address":
    # Display Asset ID and asset address if an asset address is selected
        asset_id, propco = asset_address[selected_asset_address]
        st.write(f"Asset ID: {asset_id}")
        st.write(f"Propco: {propco}")

    # Dropdown for selecting detailed property address
    selected_address = st.selectbox("Detailed Address", ["Select address at detailed dwelling level"] + list(all_addresses.keys()))
    # Check if a detailed address is selected
    if selected_address != "Select address at detailed dwelling level":
        # Display Dwelling ID and full address if a detailed address is selected
        dwelling_id, asset_id, propco = addresses[selected_address]
        st.write(f"Dwelling ID: {dwelling_id}")
        st.write(f"Asset ID: {asset_id}")
        st.write(f"Propco: {propco}")
    else:
        dwelling_id = 'N/A'

    

