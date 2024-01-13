import streamlit as st
import pyodbc
import re

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

# Function to validate email
def is_valid_email(email):
    # Regular expression for validating an email
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, email):
        return True
    else:
        return False

def show():
    #st.write("Welcome to the Add Requirements Page")
    st.markdown("---")  # Page breaker

    # Connect to the database and fetch property addresses and IDs
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Dwelling_ID, flat_number, property_address, city, propco FROM SHMDwellingInfo")
    rows = cursor.fetchall()
    addresses = {f'{row[1]} {row[2]}, {row[3]}': (row[0], row[4]) for row in rows}  # Mapping address to DwellingID and propco

    # Dropdown for selecting property address
    selected_address = st.selectbox("Property Address", list(addresses.keys()))

    # Display Dwelling ID and full address
    dwelling_id, propco = addresses[selected_address]
    st.write(f"Dwelling ID: {dwelling_id}")
    st.write(f"Propco: {propco}")

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

    # Date input for Deadline and Reminders
    deadline_date = st.date_input("Deadline")
    fst_reminder = st.date_input("First reminder")
    fnl_reminder = st.date_input("Final reminder")

    # Dropdown for recurring / one-off
    recurrence = st.selectbox("Recurrence (every X days)", ["0", "10","15","20","25","30","60","90"])
    st.caption("For one-off event, select 0 days for recurrence.")
    
    # Text input for key contacts
    loc8me_contact = st.text_input("Loc8me contact", placeholder="Please add email address")
    shm_team = st.text_input("SHM team responsible", placeholder="Please add team initial") 
    shm_individual = st.text_input("SHM individual responsible", placeholder="Please add email address")
    shm_bu = st.text_input("SHM BU lead", placeholder="Please add email address")
    added_by = st.text_input("Added by", placeholder="Please add your initials")

    # Example of using the validation function (adjust according to your app's flow)
    if st.button('Submit'):
        if is_valid_email(loc8me_contact) and is_valid_email(shm_bu):
            st.success("")
        else:
            st.error("Please enter valid email addresses.")
    
    # Additional code for the page goes here
