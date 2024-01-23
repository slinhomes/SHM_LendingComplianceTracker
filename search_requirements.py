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

# Function to update db
def update_database(conn, uid, fst_reminder, deadline_date, completed_by):
    sql = """UPDATE SHMLendingCompliance 
             SET fst_reminder = ?, deadline_date = ?, completed_by = ?
             WHERE UID = ?;"""
    cursor = conn.cursor()
    cursor.execute(sql, (fst_reminder, deadline_date, completed_by, uid))
    conn.commit()

def show():
    st.write("Please note that this site is currently under development.")
    # st.caption("Please note that this site is currently under development.")
    st.markdown("---")  # Page breaker

    # Initialize session state variables
    if 'search_results' not in st.session_state:
        st.session_state['search_results'] = None

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
        query = """
        SELECT SHMLendingCompliance.uid, SHMLendingCompliance.condition_title, SHMLendingCompliance.reference, 
               SHMLendingCompliance.requirements, SHMLendingCompliance.action_req, SHMLendingCompliance.fst_reminder, 
               SHMLendingCompliance.deadline_date, TeamDirectory.team, 
               SHMLendingCompliance.added_by, SHMLendingCompliance.entry_date
        FROM SHMLendingCompliance 
        LEFT JOIN TeamDirectory ON SHMLendingCompliance.shm_team = TeamDirectory.team_member_emails
        WHERE 1=1
        """
        params = []
        
        if selected_asset_address:
            query += " AND SHMLendingCompliance.Asset_address = ?"
            params.append(selected_asset_address)

        if selected_dwelling_address:
            query += " AND SHMLendingCompliance.Dwelling_address = ?"
            params.append(selected_dwelling_address)

        if selected_lender:
            query += " AND SHMLendingCompliance.lender = ?"
            params.append(selected_lender)

        if selected_condition_title:
            query += " AND SHMLendingCompliance.condition_title = ?"
            params.append(selected_condition_title)

        # Execute the query
        cursor = conn.cursor()
        cursor.execute(query, params)

        # Fetch all rows and column names
        result_rows = cursor.fetchall()

        if result_rows:
            result_columns = ["UID", "Condition title", "Reference", "Requirements", 
                              "Action needed", "First reminder", "Deadline", 
                              "SHM team responsible", "Condition added by", "Condition added on"]
            
            result_df = pd.DataFrame.from_records(result_rows, columns=result_columns).set_index('UID')
            result_df['complete_by'] = ""

            st.markdown("---")
            st.write("Search Results:")

            edited_df = st.data_editor(result_df, hide_index=True, 
                           column_config = {
                               "UID": st.column_config.TextColumn(),
                               "Condition title": st.column_config.TextColumn(),
                               "Reference": st.column_config.TextColumn(),
                               "Requirements": st.column_config.TextColumn(),
                               "Action needed": st.column_config.TextColumn(),
                               "First reminder": st.column_config.DateColumn(),
                               "Deadline": st.column_config.DateColumn(),
                               "SHM team responsible": st.column_config.TextColumn(),
                               "Condition added by": st.column_config.TextColumn(),
                               "Condition added on": st.column_config.DateColumn(),
                               "Completed by": st.column_config.TextColumn()
                           },
                           disabled=["UID", "Condition title", "Reference", "Requirements", 
                              "Action needed", "SHM team responsible","Condition added by","Condition added on"])
            
            # Update button
            if st.button('Update Database'):
                for uid in edited_df.index:
                    if not edited_df.loc[uid, :].equals(result_df.loc[uid, :]):
                        # Fetch the edited data
                        edited_data = edited_df.loc[uid]
                        first_reminder = edited_data['First reminder']
                        deadline = edited_data['Deadline']
                        completed_by = edited_data['Completed by']

                        # Update database for this UID
                        update_database(conn, uid, first_reminder, deadline, completed_by)
                        st.success(f'Updated UID: {uid}')
        
    else:
        # st.write("No results found matching the criteria.")

    


