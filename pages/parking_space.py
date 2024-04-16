import streamlit as st
from pages import parking_slots
from pages import space_init
# Function to display live footage


# Main function to run the Streamlit app
def main():
    st.title("Parking Management System")

    # Selection menu for choosing different actions
    selected_menu = st.selectbox(
        "Select Action:",
        ['Display live footage', 'Mark Parking Spaces'],
        format_func=lambda x: "Manual Entry" if x == "Manual Entry" else x,
        index=0,
    )

    if selected_menu == 'Display live footage':
        parking_slots.parking_slot_fun()

    elif selected_menu == 'Mark Parking Spaces':
        space_init.main()
    


if __name__ == "__main__":
    main()
