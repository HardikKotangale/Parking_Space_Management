import streamlit as st
from pages import  entry, exit, dashboard, home, parking_space, register, wstp_msg

import importlib.util

def import_page(module_name):
    spec = importlib.util.spec_from_file_location(module_name, f"pages/{module_name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
def main():
    st.title("Smart Parking System Management")

    st.sidebar.title("Navigation")
    page_options = ["Home", "Car Entry","Car Exit" ,"Dashboard","Parking Space","Register User","Whatsapp Message"]
    selected_page = st.sidebar.radio("Go to",  page_options, index=0)

    if selected_page == "Home":
        home_page = import_page("home")
        home_page.home_fun()
    elif selected_page == "Car Entry":
        car_entry_page = import_page("entry")
        car_entry_page.main()
    elif selected_page == "Car Exit":
        car_exit_page = import_page("exit")
        car_exit_page.main()
    elif selected_page == "Dashboard":
        dashboard_page = import_page("dashboard")
        dashboard_page.main()
    elif selected_page== "Parking Space":
        parking_space_page = import_page("parking_space")
        parking_space_page.main()   
    elif selected_page== "Register User":
        register_page = import_page("register")
        register_page.user()
    elif selected_page== "Whatsapp Message":
        whatsapp_msg_page = import_page("wstp_msg")
        whatsapp_msg_page.main()


if __name__ == "__main__":
    main()
