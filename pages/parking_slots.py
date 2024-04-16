import streamlit as st
import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
import json
import pytz
from datetime import datetime
import os

def get_current_ist_time():
        ist_timezone = pytz.timezone('Asia/Kolkata')
        current_ist_time = datetime.now(ist_timezone)
        formatted_time = current_ist_time.strftime("%H%M%S")
        return formatted_time
        
def parking_slot_fun():
    model = YOLO('yolov8s.pt')

    def RGB(event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            colorsBGR = [x, y]
            #print(colorsBGR)

    cv2.namedWindow('RGB', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('RGB', RGB)
    cv2.moveWindow('RGB', 100, 100) 

    # Use webcam feed instead of a video file
    cap = cv2.VideoCapture(4)  # 0 represents the default webcam, change it if needed

    my_file = open("coco.txt", "r")
    data = my_file.read()
    class_list = data.split("\n")

    # Read vacant spaces from JSON file
    with open("sample.json", "r") as json_file:
        vacant_spaces_data = json.load(json_file)

    # Convert the vacant_spaces_data dictionary into a list of areas
    areas = []
    for area_index, vacant_space_coordinates in vacant_spaces_data.items():
        areas.append({
            "id": area_index,
            "coordinates": np.array(vacant_space_coordinates, np.int32),
            "occupied": False  # Initially all areas are considered vacant
        })

    # Create output directory if it doesn't exist
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    frame_count = 0
    video_placeholder = st.empty()
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (1020, 500))
        results = model.predict(frame)

        for area in areas:
            area["occupied"] = False  # Reset occupancy status for each frame

        for area_index, area in enumerate(areas):
            area_list = []
            a = results[0].boxes.data.numpy()  # Extract NumPy array from Boxes object
            px = pd.DataFrame(a, columns=['x1', 'y1', 'x2', 'y2', 'confidence', 'class_id']).astype("float")

            for index, row in px.iterrows():
                x1 = int(row.iloc[0])
                y1 = int(row.iloc[1])
                x2 = int(row.iloc[2])
                y2 = int(row.iloc[3])
                d = int(row.iloc[5])

                c = class_list[d]
                if 'car' in c:
                    cx = int(x1 + x2) // 2
                    cy = int(y1 + y2) // 2

                    results_area = cv2.pointPolygonTest(area["coordinates"], ((cx, cy)), False)
                    if results_area >= 0:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)
                        area_list.append(c)
                        area["occupied"] = True

            area_count = len(area_list)

            if area_count == 1:
                cv2.polylines(frame, [area["coordinates"]], True, (0, 0, 255), 2)
                cv2.putText(frame, str(area["id"]), (area["coordinates"][0][0], area["coordinates"][0][1] - 5),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
            else:
                cv2.polylines(frame, [area["coordinates"]], True, (0, 255, 0), 2)
                cv2.putText(frame, str(area["id"]), (area["coordinates"][0][0], area["coordinates"][0][1] - 5),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

        # Count vacant spaces and display
        vacant_count = sum(not area["occupied"] for area in areas)
        cv2.putText(frame, f"Vacant Spaces: {vacant_count}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Print vacant spaces information on console
       # print("Vacant Parking Spaces:")
        # for area in areas:
        #     if not area["occupied"]:
        #         print(f"Area ID: {area['id']}")
        # print(f"Total Vacant Spaces: {vacant_count}")

        # Save processed frame to output directory
        timestamp=get_current_ist_time()
        #print(timestamp)
        #timestamp = int(time.time())
        output_path = os.path.join(output_dir, f"frame_{timestamp}.jpg")
        cv2.imwrite(output_path, frame)
        frame_count += 1

        # Convert the frame to RGB format
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Display the frame in the video placeholder
        video_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
