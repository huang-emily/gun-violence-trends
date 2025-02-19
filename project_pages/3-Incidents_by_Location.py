import streamlit as st
import numpy as np
import pandas as pd
from scipy.stats import rankdata
import streamlit as st

# for graphing
import plotly.express as px

st.set_page_config(page_title="Visualizing Incidents by Location")
st.title("Visualizing Incidents by Location")

# Removing the outliers, trim 10%
def remove_outliers(data, col):
    Q3 = np.quantile(data[col], 0.95)
    Q1 = np.quantile(data[col], 0.05)
    IQR = Q3 - Q1

    lower_range = Q1 - 1.1 * IQR
    upper_range = Q3 + 1.1 * IQR
    outlier_free_list = [x for x in data[col] if (
        (x > lower_range) & (x < upper_range))]
    filtered_data = data.loc[data[col].isin(outlier_free_list)]
    return filtered_data

@st.cache_data
def load_cleaned():
    return pd.read_csv("data/cleaned_mass_shootings_2014-2023.csv")
cleaned = load_cleaned()

@st.cache_data
def load_party_color():
    return pd.read_csv("data/state_party_color.csv")
state_color = load_party_color()

with st.sidebar:
    color = st.selectbox(
        "Pick a feature to base the color sequence",
        (
            "Total_Victims",
            "Victims_Injured",
            "Victims_Killed",
            "State_Political_Color",
            "US_Region"
        )
    )

    year = st.slider(
        "Select year(s)",
        2014,
        2023,
        (2014,2023)
    )

    us_region = st.multiselect(
        "Select US Region(s)",
        cleaned["US_Region"].unique().tolist(),
        cleaned["US_Region"].unique().tolist()
    )

    state = st.multiselect(
        "Select state(s)",
        cleaned["State_Name"].unique().tolist(),
        cleaned.loc[cleaned["US_Region"].isin(us_region), 'State_Name'].unique().tolist()
    )

filtered_us_region = cleaned[cleaned["US_Region"].isin(us_region)]
filtered_state = cleaned[cleaned["State_Name"].isin(state)]
filtered_year = cleaned[(cleaned["Year"] >= year[0]) & (cleaned["Year"] <= year[1])]

filtered = filtered_us_region.merge(filtered_state, on='Incident_ID', how='inner').merge(filtered_year, on='Incident_ID', how='inner')

# statistics on shown incidents
if filtered.empty:
    st.write("No data available for the selected filters.")
else: 
    # statistics on shown incidents
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Number of Incidents", filtered["Incident_ID"].count())
    col2.metric("Highest # of Injured", filtered["Victims_Injured"].max())
    col3.metric("Highest # of Killed", filtered["Victims_Killed"].max())
    col4.metric("Highest # of Total", filtered["Total_Victims"].max())

    def create_chart(filtered, color):
        if color in ("Total_Victims", "Victims_Injured", "Victims_Killed"):
            filtered['quantile_rank'] = rankdata(filtered[color], method='average') / len(filtered[color])
            color_scale = [
                '#FFC0CB',  # Pink
                '#FFB6C1',  # Light Pink
                '#FFA07A',  # Light Salmon
                '#FF7F7F',  # Medium Light Red
                '#FF6347',  # Tomato
                '#FF4500',  # Orange Red
                '#FF0000',  # Red
                '#DC143C',  # Crimson
                '#B22222',  # Fire Brick
                '#8B0000'   # Dark Red
            ]
            picked_variable = 'quantile_rank'
            legend_title = 'Normalized ' + color

            fig = px.scatter_mapbox(filtered, 
                                    lat="Latitude", lon="Longitude", 
                                    hover_name="City_or_County", 
                                    hover_data={
                                        "Latitude": False,
                                        "Longitude": False,
                                        "Incident_Date": True, 
                                        "Total_Victims": True, 
                                        "Victims_Injured": True, 
                                        "Victims_Killed": True
                                    },
                                    color="quantile_rank",
                                    color_continuous_scale=color_scale, 
                                    zoom=3, 
                                    height=600)
            fig.update_layout(
                mapbox=dict(
                    style="carto-positron",
                    center=dict(lat=37.0902, lon=-95.7129),
                    zoom=3
                ),
                coloraxis_colorbar=dict(
                    title=legend_title,
                    orientation='h',  # Set the orientation to horizontal
                    x=0.5,  # Horizontal position of the color bar
                    y=0.95,  # Vertical position of the color bar
                    xanchor='center',
                    yanchor='top',
                    thickness=10,  # Set the thickness of the color bar
                    len=0.5,  # Set the length of the color bar
                    bgcolor='rgba(255, 255, 255, 0.75)'
                )
            )

        elif color in ("State_Political_Color", "US_Region"):
            if color == "US_Region":
                color_map = {
                    'Northeast': '#1f77b4',  # Blue
                    'Midwest': '#ff7f0e',    # Orange
                    'South': '#2ca02c',      # Green
                    'West': '#d62728'       # Red
                }
            else:
                filtered['State_Political_Color'] = filtered["State_Name"].map(state_color.set_index("STATE_NAME")["COLOR"])
                color_map  = {
                    'RED': '#FF0000', 
                    'BLUE': '#0000FF', 
                    'PURPLE':'#800080'
                }

            picked_variable = color

            fig = px.scatter_mapbox(filtered, 
                                    lat="Latitude", lon="Longitude", 
                                    hover_name="City_or_County", 
                                    hover_data={
                                        "Latitude": False,
                                        "Longitude": False,
                                        "Incident_Date": True, 
                                        "Total_Victims": True, 
                                        "Victims_Injured": True, 
                                        "Victims_Killed": True
                                    },
                                    color=picked_variable,  # Use the 'Region' column for coloring
                                    color_discrete_map=color_map,  # Apply the color map
                                    zoom=3, 
                                    height=600)

            fig.update_layout(
                mapbox=dict(
                    style="carto-positron",
                    center=dict(lat=37.0902, lon=-95.7129),
                    zoom=3
                ),
                legend=dict(
                    x=0.5,  # Position the legend outside the plot
                    y=0.95,  # Vertical position of the legend
                    bgcolor='rgba(255, 255, 255, 0.75)', 
                    orientation="h", 
                    xanchor='center',
                    yanchor='top',
                )
            )

        return fig

    fig = create_chart(filtered, color)

    # Plot!
    st.plotly_chart(fig)
