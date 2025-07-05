import streamlit as st
from auth.login_page import show_login_page


# Must be the first Streamlit command
st.set_page_config(
    page_title="HIA - HealthAI Agent",
    page_icon="🩺",
    layout="wide"
)

def main():
    # SessionManager.init_session()

    show_login_page()
    #show_footer()


if __name__ == "__main__":
    main()