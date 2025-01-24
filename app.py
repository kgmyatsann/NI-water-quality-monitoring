import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import folium_static

# Load dataset
datafile = "River_Water_Quality_Monitoring_1990_to_2018_-_pH.csv"
df = pd.read_csv(datafile, dtype={'Column8': 'str', 'Column11': 'str'}, low_memory=False)

# Convert Date column to datetime format
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Ensure Date column is timezone naive
df['Date'] = df['Date'].dt.tz_localize(None)

# Swap longitude and latitude columns if necessary
df['latitude'] = df['Y']
df['longitude'] = df['X']

# Drop rows with missing pH values
df.dropna(subset=['PH'], inplace=True)

# Streamlit UI
st.set_page_config(page_title="River Water Quality Dashboard", layout="wide")
st.title("River Water Quality Monitoring Dashboard")

# Sidebar filters
station_options = df['Station_Name'].unique()
selected_station = st.sidebar.selectbox("Select Station", station_options)

date_range = st.sidebar.date_input(
    "Select Date Range", [df['Date'].min().date(), df['Date'].max().date()],
    min_value=df['Date'].min().date(), max_value=df['Date'].max().date()
)

# Filter data based on selection
filtered_df = df[(df['Station_Name'] == selected_station) &
                 (df['Date'] >= pd.Timestamp(date_range[0])) &
                 (df['Date'] <= pd.Timestamp(date_range[1]))]

# Load custom HTML map
st.subheader("Station Location")
with open("ni_water_quality_map_2018_clustered.html", "r") as f:
    html_map = f.read()

st.components.v1.html(html_map, height=600)

# Time series visualization
st.subheader(f"pH Levels Over Time at {selected_station}")
fig = filtered_df.plot(x='Date', y='PH', kind='line', title='pH Trend', ylabel='pH Level')
st.pyplot(fig.figure)

# Data Table
st.subheader("Filtered Data Table")
st.dataframe(filtered_df[['Date', 'PH', 'Station_Name']])

# Summary Statistics
st.subheader("Statistical Summary")
st.write(filtered_df['PH'].describe())


# Report Button
if st.button("Report"):
    with open("index.html", "r") as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=600)
