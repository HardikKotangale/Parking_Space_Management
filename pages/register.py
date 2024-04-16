import streamlit as st
import numpy as np
import sqlite3
import pandas as pd
from utils import key, url
from datetime import datetime
import pytz

user_color = '#000000'
#title_webapp = "Register User Form"
html_temp = f"""
            <div style="background-color:{user_color};padding:12px">
            
            </div>
            """

st.markdown(html_temp, unsafe_allow_html=True)
with sqlite3.connect("car_data.db",check_same_thread=False) as conn:
    def get_current_ist_time():
        ist_timezone = pytz.timezone('Asia/Kolkata')
        current_ist_time = datetime.now(ist_timezone)
        return current_ist_time
    c2 = conn.cursor()
    c2.execute('''CREATE TABLE IF NOT EXISTS user_details
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             license_plate TEXT, 
             user_name TEXT,
             mobile_number TEXT,
             car_model TEXT,
             registration_time TIMESTAMP DEFAULT NULL,
             parking_status TEXT DEFAULT 'OUT')''')
    conn.commit()

def user():

    license_plate = st.text_input('Enter License Plate Number')
    user_name = st.text_input('Enter User Name')
    mobile_number = st.text_input('Enter Mobile Number')
    car_model = st.text_input('Enter Car Model')
    # Save button
    if st.button('Save'):
        # Check if the car is already registered
        c2.execute("SELECT * FROM user_details WHERE license_plate=?", (license_plate.upper(),))
        existing_entry = c2.fetchone()
        if existing_entry:
            st.warning('Car is already registered')
        else:
            current_ist_time=get_current_ist_time()
            # If the car is being registered for the first time, mark parking status as "OUT"
            c2.execute('''INSERT INTO user_details (license_plate, user_name, mobile_number, car_model, registration_time, parking_status) VALUES (?, ?, ?, ?, ?, ?)''', (license_plate.upper(), user_name, mobile_number, car_model, current_ist_time, 'OUT'))
            conn.commit()
            st.success('Car details saved successfully with OUT status.')

    # # View Data option
    # if st.button('View Data'):
    #     # Fetch data from the database
    #     c2.execute("SELECT * FROM user_details")
    #     data = c2.fetchall()
    #     if data:
    #         # Display data in a table format
    #         df = pd.DataFrame(data, columns=['ID', 'License Plate', 'User Name', 'Mobile Number', 'Car Model', 'Registration Time', 'Parking Status'])
    #         st.write(df)
    #     else:
    #         st.warning('No data found in the database.')
                
if __name__ == "__main__":
    user()