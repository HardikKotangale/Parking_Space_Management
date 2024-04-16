import streamlit as st
import plotly.graph_objects as go
import sqlite3
import pandas as pd

# Function to fetch car data from the database
def fetch_car_data():
    with sqlite3.connect("car_data.db",check_same_thread=False) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM car_data")
        return c.fetchall()

# Function to plot metric with icon
def plot_metric_with_icon(icon_path, label, value):
    st.image(icon_path, use_column_width=True)
    st.markdown(f"<p style='font-size:{40}px; text-align: center; font-family: Poppins;'>{value}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:{20}px; text-align: center; font-family: Roboto Mono;'>{label}</p>", unsafe_allow_html=True)

# Function to create and display pie chart
def plot_pie_chart(labels, values):
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    st.plotly_chart(fig, use_container_width=True)

# Visitor history function
def view_visitor_history():
    # Create a new container for the view_visitor_history chart
    view_visitor_history_container = st.container()
    with view_visitor_history_container:
        st.markdown("<h2 style='text-align: center; font-size: 40px;'>Car Entry</h2>", unsafe_allow_html=True)
        car_data = fetch_car_data()
        df = pd.DataFrame(car_data, columns=['plate', 'in_time'])
        st.write(df.style.set_properties(**{'text-align': 'center', 'margin': 'auto'}).set_table_styles([{'selector':'th', 'props':[('text-align', 'center')]}]))

# Streamlit app entry point
def main():

    st.title("Parking Management System")
    st.markdown("<h1 style='text-align: center;'>Dashboard</h1>", unsafe_allow_html=True)

    # Display visitor history section
    view_visitor_history()
    # Define the columns within the container

    Parking_statistics_overview=st.container()
    with Parking_statistics_overview:
        st.markdown("<h2 style='text-align: center; font-size: 40px;'>Parking Statistics Overview</h2>", unsafe_allow_html=True)
        column_1, column_2, column_3, column_4 = st.columns(4)

        # with column_1:
        #     icon_path = "images/car.png"
        #     plot_metric_with_icon(icon_path, "Total Vehicle Parked", 20)

        with column_2:
            with sqlite3.connect("car_data.db",check_same_thread=False) as conn:
                c = conn.cursor()

                c.execute("SELECT COUNT(*) AS total_rows FROM car_data")
                vehicle_in_count = c.fetchone()[0]

            icon_path = "images/carIn.png"
            plot_metric_with_icon(icon_path, "Vehicles In", vehicle_in_count)

        with column_3:
            icon_path = "images/carOut.png"
            c = conn.cursor()
            c.execute("SELECT COUNT(*) AS total_rows FROM car_data")
            vehicle_out_count = c.fetchone()[0]
            plot_metric_with_icon(icon_path, "Vehicles Out", vehicle_out_count)

        with column_4:
            icon_path = "images/parkingDone.png"
            c.execute("""SELECT COUNT(*) AS total_rows 
                            FROM car_data 
                            WHERE in_time >= strftime('%Y-%m-%d %H:%M:%S', 'now', '-1 day');

                            """)
            Parking_done_24hrs = c.fetchone()[0]
            plot_metric_with_icon(icon_path, "Parking Done Within 24 Hrs", Parking_done_24hrs)

    # Create a new container for the pie chart
    pie_chart_container = st.container()

    # Define the content within the pie chart container
    with pie_chart_container:
        st.markdown("<h2 style='text-align: center; font-size: 40px;'>Vehicles In/Out Breakdown</h2>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)  # Add a horizontal line for separation
        # Create the pie chart showing the breakdown of vehicles in and out
        vehicles_labels = ['In', 'Out']
        vehicles_values = [15, 10]  # Sample data for demonstration
        plot_pie_chart(vehicles_labels, vehicles_values)

if __name__ == "__main__":
    main()
