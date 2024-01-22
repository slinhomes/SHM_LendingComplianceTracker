import streamlit as st
import pyodbc
import pandas as pd

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
    st.write("Welcome to the Search for Existing Compliance Requirements Page")
    st.caption("Please note that this site is currently under development.")
    st.markdown("---")  # Page breaker

    # Connect to the database and fetch property addresses and IDs
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT Asset_Address, Dwelling_Address, Lender, condition_title FROM SHMLendingCompliance")
    rows = cursor.fetchall()

    # Separate the fetched data into individual lists
    asset_addresses = [row[0] for row in rows]
    dwelling_addresses = [row[1] for row in rows]
    lenders = [row[2] for row in rows]
    condition_title = [row[3] for row in rows]

    # Search bars
    selected_asset_address = st.selectbox("Property", [""] + asset_addresses)
    selected_dwelling_address = st.selectbox("Detailed Address", [""] + dwelling_addresses, 
                                             placeholder="Only select this if you are looking for requirements at dwelling level")
    selected_lender = st.selectbox("Lender", [""] + lenders)
    selected_condition_title = st.selectbox("Condition title", [""] + condition_title)

    # Search button
    if st.button('Search'):
        # Construct the SQL query based on selected criteria
        query = "SELECT * FROM SHMLendingCompliance WHERE 1=1"  # Base query
        params = []
        
        if selected_asset_address:
            query += " AND Asset_address = ?"
            params.append(selected_asset_address)

        if selected_dwelling_address:
            query += " AND Dwelling_address = ?"
            params.append(selected_dwelling_address)

        if selected_lender:
            query += " AND lender = ?"
            params.append(selected_lender)

        if selected_condition_title:
            query += " AND condition_title = ?"
            params.append(selected_condition_title)

        # Execute the query
        cursor = conn.cursor()
        cursor.execute(query, params)

        # Fetch all rows and column names
        result_rows = cursor.fetchall()
        if result_rows:
            result_columns = [column[0] for column in cursor.description]

            # Convert the result to a pandas DataFrame
            result_df = pd.DataFrame.from_records(result_rows, columns=result_columns)

            result_df = result_df[['condition_title','reference','requirements','action_req','deadline','shm_team','shm_bu','added_by','entry_date']]

            # Display the result
            st.write("Search Results:")
            st.dataframe(result_df)
        else:
            st.write("No results found matching the criteria.")
    


