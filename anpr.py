import cv2
import requests
import datetime
from ultralytics import YOLO
import json
import streamlit as st
import sqlite3
import pandas as pd
from utils import key, url
import win32com.client as wincl

# Initialize YOLO model
vehical_model = YOLO("yolov8n.pt")

# Connect to SQLite database
conn = sqlite3.connect('car_data.db',check_same_thread=False)
c = conn.cursor()

# Create car_data table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS car_data (plate TEXT, in_time TEXT)''')
conn.commit()

# Function to insert car data into database
def insert_car_data(plate, in_time):
    c.execute("INSERT INTO car_data (plate, in_time) VALUES (?, ?)", (plate, in_time))
    conn.commit()

# Function to fetch car data from database
def fetch_car_data():
    c.execute("SELECT * FROM car_data")
    return c.fetchall()

# Function to speak text using Windows SAPI
def speak(text):
    speaker = wincl.Dispatch("SAPI.SpVoice")
    speaker.Speak(text)

def fetch_parking_status(license_plate):
    c.execute("SELECT parking_status FROM user_details WHERE license_plate = ?", (license_plate,))
    return c.fetchone()

def update_parking_status(license_plate, new_status):
    c.execute("UPDATE user_details SET parking_status = ? WHERE license_plate = ?", (new_status, license_plate))
    conn.commit()

def main():
    # Initialize the webcam (change the index if you have multiple cameras)
    cap = cv2.VideoCapture(0)

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
                    speak("Welcome, We are making the entry of your car")
                    
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
                        parking_status_tuple = fetch_parking_status(car_number)
                        parking_status = parking_status_tuple[0]
                        if parking_status == 'IN':
                            update_parking_status(car_number, 'OUT')
                            timestamp = response_data['timestamp']
                            insert_car_data(car_number, timestamp)
                        st.write(f"Detected License Plate: {car_number}")
                        #st.write(f"Timestamp: {timestamp}")
                    
                    speak("Data saved. Please park your car.")

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
