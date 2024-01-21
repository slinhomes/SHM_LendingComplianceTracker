import streamlit as st
import add_requirements
import search_requirements

# Initialize multi-page app setup
def main():
    st.set_page_config(page_title="SHM Lending Compliance Report", layout="wide")
    st.sidebar.title("Main Menu")

    # Adding space between links in the sidebar
    st.sidebar.radio("Select a page:", ["Add Requirements"])
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)  # Adding space
    st.sidebar.radio("Select a page:", ["Search for Existing Requirements"], index=1)

    # Display selected page
    st.title("SHM Lending Compliance Report")
    app_pages[selected_page]()

if __name__ == "__main__":
    main()