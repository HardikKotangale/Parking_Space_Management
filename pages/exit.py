import pytz
import cv2
import requests
import datetime
from ultralytics import YOLO
import json
import streamlit as st
import streamlit.components.v1 as components
from streamlit.components.v1 import html
import sqlite3
import razorpay
client = razorpay.Client(auth=("rzp_live_ccdgxUrjuwvI5O", "lHxlvFXCwt8qz6StKedTMab2"))
import pandas as pd
from utils import key, url
import pywhatkit

# Initialize YOLO model
vehical_model = YOLO("yolov8n.pt")

# Connect to SQLite database
conn = sqlite3.connect('car_data.db',check_same_thread=False)
c = conn.cursor()
def get_current_ist_time():
        ist_timezone = pytz.timezone('Asia/Kolkata')
        current_ist_time = datetime.now(ist_timezone)
        return current_ist_time
# Create car_data table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS car_data (plate TEXT, in_time TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS user_details
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
             license_plate TEXT, 
             user_name TEXT,
             mobile_number TEXT,
             car_model TEXT,
             registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
             parking_status TEXT DEFAULT 'IN')''')
conn.commit()

# Function to insert car data into database
def insert_car_data(plate, in_time):
    c.execute("INSERT INTO car_data (plate, in_time) VALUES (?, ?)", (plate, in_time))
    conn.commit()

# Function to fetch car data from database
def fetch_car_data():
    c.execute("SELECT * FROM car_data")
    return c.fetchall()

def fetch_parking_status(license_plate):
    c.execute("SELECT parking_status FROM user_details WHERE license_plate = ?", (license_plate,))
    return c.fetchone()

def update_parking_status(license_plate, new_status):
    c.execute("UPDATE user_details SET parking_status = ? WHERE license_plate = ?", (new_status, license_plate))
    conn.commit()

def fetch_in_time_status(plate):
    c.execute("SELECT in_time FROM car_data WHERE plate = ?", (plate,))
    return c.fetchone()

from datetime import datetime

def calculate_parking_duration(in_time):
    in_time_data = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S.%f%z')
    current_time = get_current_ist_time()
    time_difference = current_time - in_time_data
    duration_seconds = time_difference.total_seconds()  
    duration_minutes = duration_seconds / 60
    return duration_minutes


def main():
    # Initialize the webcam (change the index if you have multiple cameras)
    cap = cv2.VideoCapture(3)

    # Display the live webcam feed using Streamlit
    st.title("Vehicle Detection and Recognition")
    st.markdown("**Live Webcam Feed**")
    placeholder = st.empty()

    # Start processing frames from the webcam
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Perform vehicle detection every 10 frames
        if ret and cap.get(cv2.CAP_PROP_POS_FRAMES) % 10 == 0:
            detections_generator = vehical_model(frame, verbose=False)[0]

            for detection in detections_generator.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = detection
                if int(class_id) in [2, 3, 5, 7]:
                    
                    # Encode frame to JPEG format for sending to API
                    _, img_encoded = cv2.imencode('.jpg', frame)
                    files = {"upload": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")}
                    headers = {"Authorization": f"Token {key}"}
                    
                    # Send frame to API for license plate recognition
                    response = requests.post(url, files=files, headers=headers)
                    response_data = json.loads(response.text)
                    
                    # If license plate is detected, save data to database
                    if response_data['results']:
                        car_number = response_data['results'][0]['plate']
                        car_number = car_number.upper()
                        c.execute("SELECT mobile_number FROM user_details WHERE license_plate=?", (car_number,))
                        result = c.fetchone()
                        parking_status_tuple = fetch_parking_status(car_number)
                        parking_status = parking_status_tuple[0]
                        if parking_status == 'IN':
                            if result:
                                to_phone = result[0]
                                in_time = fetch_in_time_status(car_number.lower())
                                print(in_time[0])
                                duration = calculate_parking_duration(in_time[0])
                                bill_amount = round((duration) * 1000)
                                order = client.order.create({
                                    "amount": int(bill_amount),
                                    "currency": "INR",
                                    
                                })
                                paymentId = order['id']
                                st.experimental_set_query_params(
                                order_id=paymentId
                                )
                                with open("./pages/payment.html", "r") as file:
                                    html_content = file.read()
                                html_content = html_content.replace('amount": "5000"', f'amount": "{int(bill_amount)}"')
                                components.html(html_content,height=800,width=500)
                                id = st.text_input('Enter Payment Id Generated After Making Payment')  
                                message = f"Thank you! Your parking bill is {int(bill_amount)}. We have sent a link for payment. Please pay the bill. Have a safe drive. \n http://localhost:8501/exit?{paymentId} "
                                pywhatkit.sendwhatmsg_instantly(phone_no=to_phone, message=message, wait_time=10)
                                update_parking_status(car_number, 'OUT')
                            else:
                                to_phone = None
                        
        # Display the frame in Streamlit
        placeholder.image(frame, channels="BGR", use_column_width=True)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the VideoCapture object and close OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
