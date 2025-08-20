# Import necessary libraries
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
from numerize.numerize import numerize

# --- Page Configuration ---
st.set_page_config(
    page_title="NYC Citi Bike Strategic Dashboard",
    layout="wide"
)

# --- Data Loading ---
# We use the st.cache_data decorator to load the data only once, making the app faster.
@st.cache_data
def load_data():
    # Load the smaller random sample file we created. This is our primary data source.
    df = pd.read_csv('citi_bike_2022_small_sample.csv')
    df['started_at'] = pd.to_datetime(df['started_at'])
    df['date'] = df['started_at'].dt.date
    df['month'] = df['started_at'].dt.month
    
    # Create the season column based on the month
    seasons = {
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Fall', 10: 'Fall', 11: 'Fall'
    }
    df['season'] = df['month'].map(seasons)
    
    # We also still need our pre-calculated daily summary for the line chart
    df_daily = pd.read_csv('citi_bike_daily_summary_2022.csv')
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    df_daily = df_daily.set_index('date')
    
    # Return both dataframes
    return df, df_daily

df, df_daily = load_data()

# --- Sidebar for Page Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    'Select a page:',
    [
        "1. Introduction", 
        "2. Station Popularity Analysis",
        "3. Seasonal Ridership Trends",
        "4. Geospatial Route Analysis", 
        "5. Recommendations"
    ]
)

# --- Page Content ---
# Based on the user's selection in the sidebar, we display the corresponding content.

if page == "1. Introduction":
    st.title("NYC Citi Bike Strategic Dashboard")
    st.markdown("""
    ### Project Overview
    This dashboard presents a strategic analysis of the NYC Citi Bike service for 2022. The goal is to provide the business strategy department with actionable insights to address key challenges, such as bike shortages at popular stations, and to identify opportunities for service expansion.
    
    ### Dashboard Contents
    Use the navigation sidebar on the left to select a page and explore different aspects of the analysis:
    - **Station Popularity:** Identify the busiest start stations and analyze their seasonal ridership distribution.
    - **Seasonal Trends:** Understand how ridership fluctuates with temperature throughout the year.
    - **Geospatial Analysis:** Visualize the city's most popular "bike highways."
    - **Recommendations:** View the final, data-driven recommendations based on this analysis.
    """)
    
    # We will use a try-except block in case the image is not found.
    try:
        image = Image.open('bike_image.jpg')
        st.image(image, caption='A Citi Bike station in NYC.')
    except FileNotFoundError:
        pass # If the image isn't there, the app will just continue without it.

elif page == "2. Station Popularity Analysis":
    st.header("Analysis of Most Frequented Start Stations by Season")
    st.markdown("""
    This chart breaks down the ridership of the top 20 busiest start stations by season. 
    It clearly shows that while some stations are popular year-round, the vast majority of trips occur during the **Summer** and **Fall**. 
    This insight is crucial for planning seasonal bike fleet adjustments.
    """)

    # --- Sidebar Filter ---
    st.sidebar.markdown("---") 
    season_options = ['Winter', 'Spring', 'Summer', 'Fall'] # We define the list here
    season_filter = st.sidebar.multiselect(
        label='Select seasons to display:',
        options=season_options,
        default=season_options
    )
    
    # Add a check to ensure at least one season is selected
    if not season_filter:
        st.warning("Please select at least one season in the sidebar.")
    else:
        # Filter the dataframe based on the user's selection
        df_filtered = df[df['season'].isin(season_filter)]
        
        # --- KPI Metric ---
        total_rides = len(df_filtered)
        st.metric(label="Total Sampled Rides in Selected Seasons", value=numerize(float(total_rides)))
        
        # --- Dynamic Calculation for Stacked Bar Chart ---
        top_20_station_names = df_filtered['start_station_name'].value_counts().nlargest(20).index
        df_top_20 = df_filtered[df_filtered['start_station_name'].isin(top_20_station_names)]
        df_stacked_data = df_top_20.groupby(['start_station_name', 'season']).size().reset_index(name='trip_count')

        # --- Create the Stacked Bar Chart with Plotly ---
        fig_stacked_bar = go.Figure()

        # THE FIX: Use the correct variable 'season_options' in the loop
        for season in season_options:
            if season in season_filter: 
                df_season = df_stacked_data[df_stacked_data['season'] == season]
                fig_stacked_bar.add_trace(
                    go.Bar(
                        x=df_season['trip_count'],
                        y=df_season['start_station_name'],
                        name=season,
                        orientation='h'
                    )
                )
        
        # Update the layout for a professional look
        fig_stacked_bar.update_layout(
            title=dict(text='Seasonal Trip Distribution for Top 20 Stations', x=0.5, xanchor='center'),
            xaxis_title='Number of Trips (from sample)',
            yaxis_title='Start Station Name',
            yaxis=dict(categoryorder='total ascending'),
            barmode='stack',
            height=800,
            legend_title_text='Season'
        )
        
        st.plotly_chart(fig_stacked_bar, use_container_width=True, theme="streamlit")
        
elif page == "3. Seasonal Ridership Trends":
    st.header("Analysis of Seasonal Ridership and Weather Impact")
    st.markdown("""
    This chart illustrates the strong positive correlation between average daily temperature and the number of bike trips. 
    Ridership clearly peaks during the warmest summer months (June-September) and drops significantly in the cold winter months. 
    This seasonal pattern is a critical factor for managing fleet size and anticipating demand throughout the year.
    """)

    # Create the Plotly dual-axis figure (this is the same code from your prototyping notebook)
    fig_line = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add Bike Trips Trace
    fig_line.add_trace(
        go.Scatter(x=df_daily.index, y=df_daily['trip_count'], name='Daily Bike Trips', mode='lines', line=dict(color='deepskyblue')),
        secondary_y=False,
    )
    
    # Add Temperature Trace
    fig_line.add_trace(
        go.Scatter(x=df_daily.index, y=df_daily['avgTemp'], name='Avg. Temp (°C)', mode='lines', line=dict(color='tomato')),
        secondary_y=True,
    )
    
    # Update Layout
    fig_line.update_layout(
        title=dict(
            text='Daily Bike Trips vs. Average Temperature in NYC (2022)',
            x=0.5,
            xanchor='center'
        ),
        template='plotly_dark', 
        height=600,
        legend=dict(x=0.02, y=0.98),
        xaxis=dict(type='date', title='Date')
    )
    
    # Update Y-Axes Titles
    fig_line.update_yaxes(title_text='Daily Bike Trips', secondary_y=False)
    fig_line.update_yaxes(title_text='Average Temperature (°C)', secondary_y=True)
    
    # Set the X-Axis Range
    fig_line.update_xaxes(range=['2022-01-01', '2022-12-31'])
    
    # Display the chart in the Streamlit app
    st.plotly_chart(fig_line, use_container_width=True)
    
elif page == "4. Geospatial Route Analysis":
    st.header("Geospatial Analysis of Popular Trip Routes")
    st.markdown("""
    This map visualizes the top 1,000 most popular bike routes in 2022. The color and thickness of the arcs 
    represent the number of trips, with bright red, thick lines indicating the busiest corridors. 
    Use the filter on the map to narrow the view and discover the absolute busiest 'bike highways' of New York City.
    """)

    # Read the HTML map file that you created in Task 2.5
    try:
        with open('nyc_top_1000_bike_routes.html', 'r') as f:
            html_data = f.read()

        # Use st.components.v1.html to display the Kepler.gl map
        st.components.v1.html(html_data, height=600)

    except FileNotFoundError:
        st.error("Map file ('nyc_top_1000_bike_routes.html') not found. Please ensure it is in the same directory as the script.")
        
elif page == "5. Recommendations":
    st.title("Strategic Recommendations")
    st.markdown("""
    Based on the analysis of the 2022 Citi Bike data, here are three key recommendations to address distribution challenges and guide future expansion:
    """)
     # --- ADD IMAGE HERE ---
    # We place the image right after the introduction and before the main points.
    try:
        # Make sure the image file 'recommendation_image.jpg' is in your project folder
        image = Image.open('bike_image_2.webp')
        
        # THE FIX: Create three columns. The middle one will be twice as wide
        # as the outer ones, effectively making it 50% of the page width.
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2: # This line is indented
            st.image(image, caption='Data-driven strategies for urban mobility.')
        
    except FileNotFoundError:
        # If the image isn't found, the app will just show a note instead of crashing.
        st.info("Note: A recommendation image can be added here.")
    st.markdown("#### 1. **Implement Dynamic, Season-Aware Rebalancing**")
    st.markdown("""
    **Observation:** The analysis of top stations reveals that while some hubs (like those near transit centers) are busy year-round, many others see a dramatic drop in usage during Winter and Spring. The seasonal trend chart confirms that overall ridership is significantly lower in colder months.
    
    **Recommendation:** Shift from a static to a **dynamic, season-aware rebalancing strategy**. Focus logistical efforts on keeping the top 5-10 "all-weather" commuter stations fully stocked in winter, while reducing service to more recreational or fair-weather stations. In Summer and Fall, expand rebalancing efforts to the full top 20 stations to meet peak demand.
    """)

    st.markdown("#### 2. **Optimize Fleet Size Based on Seasonal Demand**")
    st.markdown("""
    **Observation:** The seasonal trend analysis reveals a dramatic drop in overall ridership between November and March, directly correlating with lower temperatures.
    
    **Recommendation:** Scale back the active fleet during the winter months. This will significantly reduce operational costs related to maintenance, charging (for e-bikes), and logistics. A data-driven threshold, for example, reducing the active fleet by 40-50% when the average weekly temperature drops below 5°C, could be implemented to optimize resources.
    """)
    
    st.markdown("#### 3. **Develop a Dual Strategy for Commuter vs. Leisure Hotspots**")
    st.markdown("""
    **Observation:** The geospatial map highlights A-to-B commuter "highways," while the raw data's top routes are often single-station round trips in recreational areas like Central Park.
    
    **Recommendation:** Treat these two types of hotspots differently. For **commuter corridors**, the focus should be on ensuring bike *availability* during rush hour. For **leisure hotspots**, the focus should be on ensuring a high *volume* of bikes, especially on weekends, and potentially offering different pricing models for hourly rentals to maximize revenue.
    """)