import streamlit as st
import pywhatkit
import sqlite3

with sqlite3.connect("car_data.db",check_same_thread=False) as conn:
    c2 = conn.cursor()

    c2.execute('''CREATE TABLE IF NOT EXISTS user_details
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             license_plate TEXT, 
             user_name TEXT,
             mobile_number TEXT,
             car_model TEXT,
             registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
             parking_status TEXT DEFAULT 'IN')''')
    conn.commit()

def main():
    st.title("WhatsApp Message Sender")
    
    # Retrieve the mobile number associated with the license plate
    license_plate = "GJ03ER0563"  # Example license plate number
    c2.execute("SELECT mobile_number FROM user_details WHERE license_plate=?", (license_plate,))
    result = c2.fetchone()
    if result:
        to_phone = result[0]
    else:
        to_phone = None

    # Get user input: message
    message = st.text_area("Enter Message to Send!", value="Hey there! What's up?", placeholder="Enter Message to send")

    if to_phone and message:
            try:
                pywhatkit.sendwhatmsg_instantly(phone_no=to_phone, message=message, wait_time=10)
                st.success("Message sent successfully!")
            except Exception as e:
                st.error(f"Error sending message: {e}")
    else:
        st.warning("Please provide both recipient number and message.")
conn.commit()
if __name__ == "__main__":
    main()
