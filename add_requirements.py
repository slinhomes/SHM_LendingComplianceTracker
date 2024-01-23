import streamlit as st
import pyodbc
# import re
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
        sql = '''CREATE TABLE [dbo].[SHMLendingCompliance] (
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
    insert_sql = '''INSERT INTO SHMLendingCompliance (Dwelling_ID, Asset_ID, Asset_address, Dwelling_address, lender, condition_title, reference, requirements, 
                   action_req, trigger_date, deadline_period, deadline_date, fst_reminder, recurrence, 
                   loc8me_contact, shm_team, shm_individual, shm_bu, added_by, entry_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''

    cur = conn.cursor()
    cur.execute(insert_sql, data)
    conn.commit()

# Function to validate email
# def is_valid_email(email):
#     # Regular expression for validating an email
#     regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
#     if re.fullmatch(regex, email):
#         return True
#     else:
#         return False

def show():
    #st.write("Welcome to the Add Requirements Page")
    st.markdown("---")  # Page breaker

    # Connect to the database and fetch property addresses and IDs
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Dwelling_ID, Asset_ID, flat_number, property_address, city, propco FROM SHMDwellingInfo")
    rows = cursor.fetchall()
    asset_address =  {f'{row[3]}, {row[4]}': (row[1], row[5]) for row in rows}  # Mapping asset address to AssetID and propco
    addresses = {f'{row[2]} {row[3]}, {row[4]}': (row[0], row[1], row[5]) for row in rows}  # Mapping detailed address to DwellingID and propco

    st.caption("Select property address or detailed asset below.")

    # Dropdown for selecting asset address
    selected_asset_address = st.selectbox("Asset Address", ["Select property address"] + list(asset_address.keys()))

    dwelling_id = asset_id = propco = ""  # Initialize dwelling_id, asset_id and propco

    if selected_asset_address != "Select property address":
        # Display Asset ID and asset address if an asset address is selected
        asset_id, propco = asset_address[selected_asset_address]
        st.write(f"Asset ID: {asset_id}")
        st.write(f"Propco: {propco}")

    # Dropdown for selecting detailed property address
    selected_address = st.selectbox("Detailed Address", ["Select address at detailed dwelling level"] + list(addresses.keys()))

    # Check if a detailed address is selected
    if selected_address != "Select address at detailed dwelling level":
        # Display Dwelling ID and full address if a detailed address is selected
        dwelling_id, asset_id, propco = addresses[selected_address]
        st.write(f"Dwelling ID: {dwelling_id}")
        st.write(f"Asset ID: {asset_id}")
        st.write(f"Propco: {propco}")
    else:
        dwelling_id = 'N/A'

    # Dropdown for selecting a Lender and Requirements
    lender = st.selectbox("Lender", ["Santander", "Aburthnott"])
    # Dropdown for selecting a requirements or condition
    condition_title = st.selectbox("Requirements / Condition",
                                   ['HMO Licence','Asbestos Survey','Refurb Compliance',
                                    'Refurb Inspectors (incl. Building Certificates and HMO variations)',
                                    'Arrange valuer / lender inspection and building surveys',
                                    'Other conditions'])

    # Text input for Reference in facility agreement
    reference = st.text_input("Reference in facility agreement",
                              placeholder="Please submit reference number from the facilities agreement. For example: 'Schedule 10 - 1.0'")

    # Text input for Reference in facility agreement
    requirements = st.text_area("Requirements as per the facility agreement",
                                 placeholder="Please copy and paste the original requirement wording from the facility agreement.",
                                 height=100)
   
    # Text input for Reference in facility agreement
    action_req = st.text_area("Action required",
                                placeholder="Please summarise action/task required as per the facility agreement.",
                                height=100)
    
    # Date input for Trigger Date
    trigger_date = st.date_input("Requirement Trigger Date")

    # Numeric input for Deadline, period
    deadline_period = st.number_input("Deadline (days)", min_value=0, value=0, step=1,
                                    format="%d",
                                    help="If action is required to be completed by X days following the trigger date. Input if applicable.")
    # Calculate the default deadline date
    default_deadline_date = trigger_date + timedelta(days=deadline_period)
    default_fst_reminder_date = deadline_date - timedelta(days=14)
    # Date input for Deadline and Reminders
    deadline_date = st.date_input("Deadline", value=default_deadline_date)
    fst_reminder = st.date_input("Reminder starts on", value=default_fst_reminder_date)
    st.caption("Note: Daily reminders will be sent to individual responsible via email, from the first date of the reminder until the action is complete or the final deadline date.")
    #fnl_reminder = st.date_input("Final reminder")

    # Dropdown for recurring / one-off
    recurrence = st.selectbox("Recurrence (every X days)", ["0", "10","15","20","25","30","60","90"])
    st.caption("For one-off event, select 0 days for recurrence.")
    st.caption("IMPORTANT: The reminder function for recurrent events still need to be build. For the time being, please notify the Data team when you add a recurrent event.")
    
    # Text input for key contacts
    loc8me_contact = st.text_input("Loc8me contact", placeholder="Please add email address")
    shm_team = st.selectbox("SHM team responsible", ['Data','Finance','Investment','Legal','Ops']) 
    shm_individual = st.text_input("SHM individual responsible", placeholder="Please add email address")
    shm_bu = st.text_input("SHM BU lead", placeholder="Please add email address")
    added_by = st.text_input("Added by", placeholder="Please add your email address")
    entry_date = st.date_input("Requirement added on")

    # Collect data into a DataFrame for preview
    data = {
        "Dwelling ID": dwelling_id,
        "Asset ID": asset_id,
        "Property": selected_asset_address,
        "Detailed Address (if applicable)": selected_address,
        "Lender": lender,
        "Condition Title": condition_title,
        "Reference": reference,
        "Requirements": requirements,
        "Action Required": action_req,
        "Trigger Date": trigger_date,
        "Deadline Period (days)": deadline_period,
        "Deadline": deadline_date,
        "First reminder": fst_reminder,
        #"Final reminder": fnl_reminder,
        "Loc8me Contact": loc8me_contact,
        "SHM team resopnsible": shm_team,
        "SHM invidual responsible": shm_individual,
        "SHM BU lead": shm_bu,
        "Data entered by": added_by,
        "Entry date": entry_date
    }
    preview_df = pd.DataFrame([data])
    preview_df = preview_df.set_index('Dwelling ID')

    # Display the data as a table for preview
    st.write("IMPORTANT!")
    st.write("Please check the following details entered before submission.")

    transposed_preview_df = preview_df.T
    #transposed_preview_df = transposed_preview_df.iloc[1:,:]
    st.table(transposed_preview_df)

    submit_button = st.button("Submit")
  
    if submit_button:
        # Prepare the data tuple for database insertion
        data_tuple = (
            dwelling_id, asset_id, selected_asset_address, selected_address, lender, 
            condition_title, reference, requirements, 
            action_req, trigger_date, deadline_period, deadline_date, fst_reminder,
            #fnl_reminder, 
            recurrence, loc8me_contact, shm_team, shm_individual,
            shm_bu, added_by, entry_date #... other fields as needed
        )

        # Connect to the database
        conn = create_connection()

        # Create the table if it doesn't exist
        create_table(conn)

        # Insert data into the database
        try:
            insert_data(conn, data_tuple)
            st.success("Data submitted successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

        # Close the database connection
        conn.close()