import streamlit as st
import hmac
import add_requirements
import search_requirements

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("Password incorrect, please try again.")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Main Streamlit app starts here
st.button("Click me")


# Initialize multi-page app setup
def main():
    st.set_page_config(page_title="SHM Lending Compliance Report", layout="wide")
    st.sidebar.title("Main Menu")

    # Custom labels with HTML for spacing
    page_labels = ["Add Requirements", "Search for Existing Requirements"]

    # Sidebar for page navigation
    selected_label = st.sidebar.radio("Select a page:", page_labels)

    # Map the labels to functions
    app_pages = {
        "Add Requirements": add_requirements.show,
        "Search for Existing Requirements": search_requirements.show,
    }

    # Display selected page
    st.title("SHM Lending Compliance Report")
    app_pages[selected_label]()

if __name__ == "__main__":
    main()