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
def update_database(conn, uid, fst_reminder, deadline_date):
    sql = """UPDATE SHMLendingCompliance 
             SET fst_reminder = ?, deadline_date = ?
             WHERE UID = ?;"""
    cursor = conn.cursor()
    cursor.execute(sql, (fst_reminder, deadline_date, uid))
    conn.commit()

# Function to update completion
def update_completion(conn, uid, completed_by, complete_on):
    sql = """UPDATE SHMLendingCompliance 
             SET complete_by = ?, complete_on = ?
             WHERE UID = ?;"""
    cursor = conn.cursor()
    cursor.execute(sql, (completed_by, complete_on, uid))
    conn.commit()

def show():
    # st.write("Please note that this site is currently under development.")
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

    # Process asset and dwelling addresses to handle multiple addresses
    asset_addresses_raw = [row[0] for row in rows]
    dwelling_addresses_raw = [row[1] for row in rows]

    # Split addresses by comma and get unique values
    def get_unique_addresses(address_list):
        split_addresses = [address.strip() for addr in address_list for address in addr.split(',')]
        return list(set(split_addresses))
    
    asset_addresses = get_unique_addresses(asset_addresses_raw)
    dwelling_addresses = get_unique_addresses(dwelling_addresses_raw)

    lenders = [row[2] for row in rows]
    condition_title = [row[3] for row in rows]

    # Search bars
    selected_asset_address = st.selectbox("Search by Property Keywords", [""] + asset_addresses)
    selected_dwelling_address = st.selectbox("Search by Detailed Address Keywords", [""] + dwelling_addresses, 
                                             placeholder="Only select this if you are looking for requirements at dwelling level")
    selected_lender = st.selectbox("Lender", [""] + lenders)
    selected_condition_title = st.selectbox("Condition title", [""] + condition_title)

    # Search button
    if st.button('Search'):
        # Construct the SQL query based on selected criteria
        query = """
        SELECT SHMLendingCompliance.uid, SHMLendingCompliance.condition_title, SHMLendingCompliance.reference, 
               SHMLendingCompliance.requirements, SHMLendingCompliance.action_req, SHMLendingCompliance.fst_reminder, 
               SHMLendingCompliance.deadline_date, SHMLendingCompliance.shm_team, 
               SHMLendingCompliance.added_by, SHMLendingCompliance.entry_date, SHMLendingCompliance.complete_by, SHMLendingCompliance.complete_on
        FROM SHMLendingCompliance
        WHERE 1=1
        """
        params = []
        
        if selected_asset_address:
            query += " AND SHMLendingCompliance.Asset_address LIKE ?"
            params.append(f"%{selected_asset_address}%")

        if selected_dwelling_address:
            query += " AND SHMLendingCompliance.Dwelling_address LIKE ?"
            params.append(f"%{selected_dwelling_address}%")

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
                              "SHM team responsible", "Condition added by", "Condition added on", "Completed by", "Completed on"]
            
            st.session_state['search_results'] = pd.DataFrame.from_records(result_rows, columns=result_columns).set_index('UID')

    # Display search results and editor
    if st.session_state['search_results'] is not None:
        st.markdown("---")
        st.write("Search Results: (please make sure you have pressed the Search button)")
        st.dataframe(st.session_state['search_results'])

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Update Requirements")

            uid_to_update = st.selectbox("Select UID to Update", st.session_state['search_results'].index)
            new_first_reminder = st.date_input("New First Reminder", value=st.session_state['search_results'].loc[uid_to_update,'First reminder'], key="new_first_reminder")
            new_deadline = st.date_input("New Deadline", value=st.session_state['search_results'].loc[uid_to_update,'Deadline'], key="new_deadline")
        
            # Update button
            if st.button('Update Database'):
                update_database(conn, uid_to_update, new_first_reminder, new_deadline)
                st.success(f'Thanks! Record for UID: {uid_to_update} is successfully updated!')
            else:
                st.caption("To update the record, please make sure you click 'Update Database'.")
        
        with col2:
            st.subheader("Mark Completion")

            select_uid_for_completion = st.selectbox("Select UID to Mark Completion", st.session_state['search_results'].index)
            completed_by = st.text_input("Completed By (add your initials)", key="new_completed_by")
            completed_on = st.date_input("Completed On", key ="new_completed_on")
            submit_completion = st.button("Submit Completion", key="submit_completion")

            if submit_completion:
                update_completion(conn, select_uid_for_completion, completed_by, completed_on)
                st.success("Completion submitted successfully!")
            else:
                st.caption("To submit completion, please make sure you click 'Mark Completion'.")

                    
    

    


