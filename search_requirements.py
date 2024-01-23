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

def update_completion_status(conn, uid, completed_by):
    try:
        sql = '''UPDATE SHMLendingCompliance SET Completed_by = ? WHERE UID = ?;'''
        cur = conn.cursor()
        cur.execute(sql, (completed_by, uid))
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")

def update_database(conn, uid, first_reminder, deadline, completed_by):
    sql = """UPDATE SHMLendingCompliance 
             SET First_reminder = ?, Deadline = ?, Completed_by = ?
             WHERE UID = ?;"""
    cursor = conn.cursor()
    cursor.execute(sql, (first_reminder, deadline, completed_by, uid))
    conn.commit()

def show():
    st.write("Please note that this site is currently under development.")
    # st.caption("Please note that this site is currently under development.")
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
            # Define the columns to display
            result_columns = ["UID", "Condition title", "Reference", "Requirements", 
                              "Action needed", "First reminder", "Deadline", 
                              "SHM team responsible", "Condition added by", "Condition added on"]
            
            # Convert the result to a pandas DataFrame
            result_df = pd.DataFrame.from_records(result_rows, columns=result_columns)
            result_df = result_df.set_index('UID')

            # Add a column for 'Completed_by' initials
            result_df['Completed_by'] = ''

            # Display the result
            st.write("Search Results:")
            # st.dataframe(result_df)
            # for uid, row in result_df.iterrows():
            #     st.write(row)
            #     initials = st.text_input(f"Enter initials to mark as complete for '{uid}'", key=f"initials_{uid}")
            #     if initials:
            #         # Assuming UID is included in the result_rows
            #         update_completion_status(conn, uid, initials)
            #         st.success(f"Marked as completed by {initials} for '{uid}'")
            #         break  # Break to update one record at a time

            edited_df = st.data_editor(result_df, hide_index=True, width=1000, 
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
                try:
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
                except Exception as e:
                    st.error(f"An error occurred while updating the database: {e}")


        else:
            st.write("No results found matching the criteria.")
    


