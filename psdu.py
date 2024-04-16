import streamlit as st
import pandas as pd
import numpy as np
from ultralytics import YOLO
import json
import os
import tempfile
import cv2

def load_class_list(file_path):
    with open(file_path, "r") as file:
        return file.read().strip().split("\n")

def parkingspace(video_file_path, class_list):
    model = YOLO('yolov8s.pt')

    st.title("Parking Space Monitoring")

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

    cap = cv2.VideoCapture(video_file_path)

    # Placeholder for the initial image
    placeholder = st.empty()

    stop_button = st.button("Stop")
    while True:
        ret, frame = cap.read()
        if not ret or stop_button:
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

        # Update the placeholder with the current frame
        placeholder.image(frame, channels="BGR", use_column_width=True)

    cap.release()

def main():
    class_list = load_class_list("coco.txt")
    video_file = st.file_uploader("Upload a video file", type=["mp4"])

    if video_file is not None:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(video_file.read())
            temp_file_path = temp_file.name

        parkingspace(temp_file_path, class_list)

if __name__ == "__main__":
    main()
