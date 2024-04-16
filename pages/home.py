import streamlit as st

def home_fun():
    st.title("Home")
    st.write("Welcome to the SPMS - please open the navigation bar to select what you want to do.")

    left_column, right_column = st.columns([3, 1])

    with left_column:
        icon_path = "images/yellow_car.png"
        st.image(icon_path, use_column_width=True)

    with right_column:
        pass  