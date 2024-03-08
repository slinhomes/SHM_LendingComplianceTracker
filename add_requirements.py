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
        sql = '''CREATE TABLE [dbo].[SHMLendingCompliance] (
                [UID] UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY,
                [Dwelling_ID] NVARCHAR(MAX) NULL,
                [Asset_ID] NVARCHAR(MAX) NULL,
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
                [recurrence] INT NULL,
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
                   deadline_period, deadline_date, fst_reminder, recurrence, num_of_recurrence, loc8me_contact, 
                   shm_team, shm_individual, shm_bu, added_by, entry_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''

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
    selected_asset_addresses = st.multiselect("Asset Address", list(asset_address.keys()), help="You can select multiple addresses.")

    # Initialize variables to store concatenated strings
    concatenated_dwelling_ids = ""
    concatenated_asset_ids = ""
    concatenated_asset_addresses = ""
    concatenated_detailed_addresses = ""

    # Initialize sets to hold unique IDs and addresses
    selected_dwelling_ids = set()
    selected_asset_ids = set()

    # Process selected asset addresses
    if selected_asset_addresses:
        for selected_asset_address in selected_asset_addresses:
            asset_id = asset_address[selected_asset_address]
            selected_asset_ids.add(asset_id)
            # Find detailed addresses related to the selected asset address
            for addr, details in all_addresses.items():
                if details[1] == asset_id:
                    selected_dwelling_ids.add(details[0])
                    concatenated_detailed_addresses += addr + ", "

        concatenated_asset_addresses = ", ".join(selected_asset_addresses)
        concatenated_asset_ids = ", ".join(selected_asset_ids)
        concatenated_dwelling_ids = ", ".join(selected_dwelling_ids)

    # Allow users to select multiple detailed addresses
    filtered_detailed_addresses = {addr: details for addr, details in all_addresses.items() if details[1] in selected_asset_ids}
    selected_detailed_addresses = st.multiselect("Detailed Address", list(filtered_detailed_addresses.keys()), help="You can select multiple addresses if they are related to the selected asset address(es).")

    # If specific detailed addresses are selected, override the concatenated strings for dwelling IDs and detailed addresses
    if selected_detailed_addresses:
        selected_dwelling_ids.clear()  # Clear previous selections
        concatenated_detailed_addresses = ""  # Reset the string
        for selected_address in selected_detailed_addresses:
            dwelling_id, asset_id, propco = all_addresses[selected_address]
            selected_dwelling_ids.add(dwelling_id)
            concatenated_detailed_addresses += selected_address + ", "

        concatenated_dwelling_ids = ", ".join(selected_dwelling_ids)
    
    # Trim trailing commas
    concatenated_detailed_addresses = concatenated_detailed_addresses.rstrip(", ")
    concatenated_asset_addresses = concatenated_asset_addresses.rstrip(", ")

    # Dropdown for selecting a requirements or condition
    condition_title = st.selectbox("Condition title",
                                   ['HMO Licence','Asbestos Survey','Refurb Compliance',
                                    'Refurb Inspectors (incl. Building Certificates and HMO variations)',
                                    'Arrange valuer / lender inspection and building surveys', 'FRA',
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
    # Date input for Deadline
    deadline_date = st.date_input("Deadline", value=default_deadline_date)
    # Calculate the default reminder date
    default_fst_reminder_date = deadline_date - timedelta(days=14)
    # Date input for Reminders
    fst_reminder = st.date_input("Reminder starts on", value=default_fst_reminder_date)
    st.caption("Note: Reminders will be sent to individual responsible via email every Monday at 7:00am, from the first date of the reminder until the action is complete or the final deadline date.")

    # Dropdown for recurring / one-off
    recurrence = st.selectbox("Recurrence (every X days from the first deadline date)", ["0","30","60","90","180","365"])
    st.caption("Example 1: For one-off event, select 0 days for recurrence.")
    st.caption("Example 2: For a quarterly event, select 90 days for recurrence.")
    st.caption("IMPORTANT: The reminder function for recurrent events still need to be build. For the time being, please notify the Data team when you add a recurrent event.")
    # End date of recurring events
    num_of_recurrence = st.selectbox("Number of recurrence", ["0","1","2","3","4","5"])
    
    # Text input for key contacts
    loc8me_contact = st.text_input("Loc8me contact", placeholder="Please add email address")
    shm_team = st.selectbox("SHM team responsible", ['Ops','Legal','Finance','Investment','Data']) 
    shm_individual = st.text_input("SHM individual responsible", placeholder="Please add email address")
    shm_bu = st.text_input("SHM BU lead", placeholder="Please add email address")
    st.caption("Note: SHM individual responsible and SHM BU lead has to be different.")
    added_by = st.text_input("Added by", placeholder="Please add your email address")
    entry_date = st.date_input("Requirement added on")


    # Collect data into a DataFrame for preview
    data = {
        "Dwelling ID": concatenated_dwelling_ids,
        "Asset ID": concatenated_asset_ids,
        "Asset Address": concatenated_asset_addresses,
        "Detailed Address": concatenated_detailed_addresses,
        "Lender": selected_lender,
        "Condition Title": condition_title,
        "Reference": reference,
        "Requirements": requirements,
        "Action Required": action_req,
        "Trigger Date": trigger_date.strftime('%Y-%m-%d') if trigger_date else None,
        "Deadline Period (days)": deadline_period,
        "Deadline Date": deadline_date.strftime('%Y-%m-%d') if deadline_date else None,
        "First Reminder": fst_reminder.strftime('%Y-%m-%d') if fst_reminder else None,
        "Recurrence": recurrence,
        "Number of recurrence": num_of_recurrence,
        "Loc8me Contact": loc8me_contact,
        "SHM Team Responsible": shm_team,
        "SHM Individual Responsible": shm_individual,
        "SHM BU Lead": shm_bu,
        "Added By": added_by,
        "Entry Date": entry_date.strftime('%Y-%m-%d') if entry_date else None
    }

    preview_df = pd.DataFrame([data])

    # Display the data as a table for preview with an important message
    st.markdown("<span style='color: red; font-weight: bold;'>IMPORTANT! Please check all your data inputs before submission.</span>", unsafe_allow_html=True)
    st.table(preview_df.T)

    # Build a submit button
    submit_button = st.button("Submit")

    if submit_button:
        # Prepare the data tuple for database insertion
        data_tuple = (
            concatenated_dwelling_ids, concatenated_asset_ids, concatenated_asset_addresses, concatenated_detailed_addresses, selected_lender, 
            condition_title, reference, requirements, action_req, trigger_date, 
            deadline_period, deadline_date, fst_reminder, recurrence, num_of_recurrence, loc8me_contact, 
            shm_team, shm_individual, shm_bu, added_by, entry_date
        )

        # Connect to the database
        conn = create_connection()

        # Create the table if it does not exist
        create_table(conn)

        # Insert data into the database
        try:
            insert_data(conn, data_tuple)
            st.success("Data submitted successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

        # Close the database connection
        conn.close()
