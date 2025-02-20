import streamlit as st
import numpy as np
import pandas as pd
from scipy.stats import rankdata
import streamlit as st

# for graphing
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Visualizing the Data")
st.title("Visualizing the Data")

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
    state_party_color = pd.read_csv("data/state_party_color.csv")
    cleaned = pd.read_csv("data/cleaned_mass_shootings_2014-2023.csv")
    cleaned['State_Political_Color'] = cleaned["State_Name"].map(state_party_color.set_index("STATE_NAME")["COLOR"])
    return cleaned
cleaned = load_cleaned()

with st.sidebar:
    color = st.selectbox(
        "Pick a feature for the map's color sequence",
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

            fig = px.scatter_map(filtered, 
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
                color_map  = {
                    'RED': '#FF0000', 
                    'BLUE': '#0000FF', 
                    'PURPLE':'#800080'
                }

            picked_variable = color

            fig = px.scatter_map(filtered, 
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


    def create_bar(filtered):
        bar_filtered = filtered[["City_or_County", "State_Name", "Total_Victims", "Victims_Injured", "Victims_Killed", "Year", "Month"]]

        # organize the city data
        bar_city_filtered = pd.DataFrame(bar_filtered.groupby("City_or_County")[["Total_Victims", "Victims_Injured", "Victims_Killed"]].sum().sort_index())
        bar_city_filtered.reset_index(inplace=True)
        bar_city_filtered = bar_city_filtered.sort_values(by="Total_Victims", ascending=False).head(10)
        city_fig = px.bar(bar_city_filtered, 
                                x="City_or_County", 
                                y=["Victims_Injured", "Victims_Killed"],
                                title="Top 10 Cities by Total Victims")
        city_fig.add_trace(go.Scatter(
            x=bar_city_filtered['City_or_County'],
            y=bar_city_filtered['Total_Victims'],
            text=bar_city_filtered['Total_Victims'],
            mode='text',
            textposition='top center',
            showlegend=False
        ))
        city_fig.update_layout(
            legend=dict(
                x=0.5, 
                y=0.95,
                bgcolor='rgba(255, 255, 255, 0.75)',
                xanchor='left',
                yanchor='top',
            )
        )

        # organize the state data
        bar_state_filtered = pd.DataFrame(bar_filtered.groupby("State_Name")[["Total_Victims", "Victims_Injured", "Victims_Killed"]].sum().sort_index())
        bar_state_filtered.reset_index(inplace=True)
        bar_state_filtered = bar_state_filtered.sort_values(by="Total_Victims", ascending=False).head(10)
        state_fig = px.bar(bar_state_filtered, 
                                x="State_Name", 
                                y=["Victims_Injured", "Victims_Killed"],
                                title="Top 10 States by Total Victims")
        state_fig.add_trace(go.Scatter(
            x=bar_state_filtered['State_Name'],
            y=bar_state_filtered['Total_Victims'],
            text=bar_state_filtered['Total_Victims'],
            mode='text',
            textposition='top center',
            showlegend=False
        ))
        state_fig.update_layout(
            legend=dict(
                x=0.5,  # Position the legend outside the plot
                y=0.95,  # Vertical position of the legend
                bgcolor='rgba(255, 255, 255, 0.75)',
                xanchor='left',
                yanchor='top',
            )
        )

        return city_fig, state_fig


    map_fig = create_chart(filtered, color)
    bar_city, bar_state = create_bar(filtered=filtered)
    # Plot!
    st.plotly_chart(map_fig)

    bar_col1, bar_col2 = st.columns(2)
    with bar_col1:
        st.plotly_chart(bar_city)
    
    with bar_col2:
        st.plotly_chart(bar_state)

