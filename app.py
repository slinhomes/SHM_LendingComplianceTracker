import hmac
import streamlit as st

# Ask for password before user opens the page
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("""Password incorrect! 
                 Please try again.""")
        st.caption("Email slin@studenthomesmgmt.com to report any system error.")
    return False

if not check_password():
    st.stop()  # Do not continue if check_password is not True.


import streamlit as st
import add_requirements
import search_requirements
import add_requirements2

# Initialize multi-page app setup
def main():
    st.set_page_config(page_title="SHM Refi Bank Requirements Portal", layout="wide")
    st.sidebar.title("Main Menu")

    # Custom labels with HTML for spacing
    page_labels = ["Add requirements", "Add requirements v2","Search for existing requirements"]

    # Sidebar for page navigation
    selected_label = st.sidebar.radio("Select a page:", page_labels)

    # Map the labels to functions
    app_pages = {
        "Add requirements": add_requirements.show,
        "Add requirements 2":add_requirements2.show,
        "Search for existing requirements": search_requirements.show,
    }

    # Display selected page
    st.title("SHM Refi Bank Requirements Portal")
    app_pages[selected_label]()

if __name__ == "__main__":
    main()