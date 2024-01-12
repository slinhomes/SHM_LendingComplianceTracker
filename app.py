import streamlit as st
import add_requirements
import search_requirements

# Initialize multi-page app setup
def main():
    st.set_page_config(page_title="SHM Lending Compliance Report", layout="wide")
    st.sidebar.title("Navigation")
    app_pages = {
        "Add Requirements": add_requirements.show,
        "Search for Existing Requirements": search_requirements.show,
    }

    # Sidebar for page navigation
    selected_page = st.sidebar.radio("Select a page:", list(app_pages.keys()))

    # Display selected page
    st.title("SHM Lending Compliance Report")
    app_pages[selected_page]()

if __name__ == "__main__":
    main()