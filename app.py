import streamlit as st
import add_requirements
import search_requirements

# Initialize multi-page app setup
def main():
    st.set_page_config(page_title="SHM Lending Compliance Report", layout="wide")
    st.sidebar.title("Main Menu")

    # Custom labels with HTML for spacing
    page_labels = ["Add Requirements", "&nbsp;", "Search for Existing Requirements"]

    # Sidebar for page navigation
    selected_label = st.sidebar.radio("Select a page:", page_labels, format_func=lambda x: x.replace("&nbsp;", ""))

    # Map the labels to functions
    app_pages = {
        "Add Requirements": add_requirements.show,
        "Search for Existing Requirements": search_requirements.show,
    }

    # Display selected page
    st.title("SHM Lending Compliance Report")
    app_pages[selected_page]()

if __name__ == "__main__":
    main()