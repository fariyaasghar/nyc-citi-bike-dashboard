# Import necessary libraries
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Page Configuration ---

st.set_page_config(
    page_title="NYC Citi Bike Strategic Dashboard",
    layout="wide"
)

# --- Data Loading (from pre-aggregated files for speed) ---
@st.cache_data
def load_data():
    df_top_1000 = pd.read_csv('citi_bike_top_1000_routes.csv')
    df_top_20_stations = df_top_1000.groupby('start_station_name')['trip_count'].sum().nlargest(20).reset_index()
    df_daily = pd.read_csv('citi_bike_daily_summary_2022.csv')
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    df_daily = df_daily.set_index('date') # Set date as index
    return df_top_20_stations, df_daily

df_top_20_stations, df_daily = load_data()


# --- Dashboard Title and Introduction ---
st.title("NYC Citi Bike Strategic Dashboard")
st.markdown("""
This dashboard provides insights into the NYC Citi Bike service to support the business strategy department in identifying expansion opportunities and managing bike distribution.
The analysis focuses on station popularity and seasonal demand trends throughout 2022.
""")

# --- Visualization 1: Top 20 Popular Stations ---
st.header("1. What are the most popular starting stations?")

fig_bar = go.Figure(
    go.Bar(
        x=df_top_20_stations['trip_count'],
        y=df_top_20_stations['start_station_name'],
        orientation='h',
        marker=dict(color=df_top_20_stations['trip_count'], colorscale='Viridis')
    )
)
# THEME FIX: Explicitly set the template to 'plotly_dark' for consistency.
fig_bar.update_layout(
    title=dict(
        text='Top 20 Most Popular Citi Bike Start Stations (2022)',
        x=0.5,
        xanchor='center'
    ),
    xaxis_title='Total Number of Trips', yaxis_title='Start Station Name',
    yaxis=dict(autorange="reversed"),
    height=700, template='plotly_dark'
)
st.plotly_chart(fig_bar, use_container_width=True)


# --- Visualization 2: Seasonal Trends ---
st.header("2. How does ridership change with temperature?")
st.markdown("A strong positive correlation is visible between the average temperature and the number of daily bike trips. Ridership peaks during the warmest summer months and drops significantly in winter.")

# Use the fully corrected code for the line chart
fig_line = make_subplots(specs=[[{"secondary_y": True}]])
fig_line.add_trace(
    go.Scatter(x=df_daily.index, y=df_daily['trip_count'], name='Daily Bike Trips', mode='lines', line=dict(color='deepskyblue')),
    secondary_y=False,
)
fig_line.add_trace(
    go.Scatter(x=df_daily.index, y=df_daily['avgTemp'], name='Avg. Temp (°C)', mode='lines', line=dict(color='tomato')),
    secondary_y=True,
)
# THEME FIX & AXIS FIX
fig_line.update_layout(
    title=dict(
        text='Daily Bike Trips vs. Average Temperature in NYC (2022)',
        x=0.5,
        xanchor='center'
    ),
    template='plotly_dark', height=600,
    legend=dict(x=0.02, y=0.98),
    xaxis=dict(type='date', title='Date')
)
fig_line.update_yaxes(title_text='Daily Bike Trips', secondary_y=False)
fig_line.update_yaxes(title_text='Average Temperature (°C)', secondary_y=True)
fig_line.update_xaxes(range=['2022-01-01', '2022-12-31'])
st.plotly_chart(fig_line, use_container_width=True)


# --- Visualization 3: Geospatial Map of Popular Routes ---
st.header("3. What are the most popular trip routes?")
st.markdown("The map below visualizes the top 1,000 most popular bike routes in 2022. Use the filter to narrow down the view to see the absolute busiest 'bike highways' of New York City.")

try:
    with open('nyc_top_1000_bike_routes.html', 'r') as f:
        html_data = f.read()

    # THE FIX: Create three columns. The middle one will be very wide.
    # We are giving a little more space on the left to see if it helps centering.
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1]) # 10% left, 80% middle, 10% right

    with col2: # Place the map in the wide, central column (col2)
        st.components.v1.html(html_data, height=1000)

except FileNotFoundError:
    st.error("Map file ('nyc_top_1000_bike_routes.html') not found. Please ensure it is in the same directory as the script.")