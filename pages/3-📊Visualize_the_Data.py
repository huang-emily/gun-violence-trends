import streamlit as st
import numpy as np
import pandas as pd
from scipy.stats import rankdata
import streamlit as st

# for graphing
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

st.set_page_config(page_title="Visualize the Data")
st.title("Visualize the Data")

st.markdown("""
    These charts were originally created in Power BI which you can find the file for in 
    the [Github repo](https://github.com/huang-emily/gun-violence-trends).
            
    The filters in the sidebar allow you to configure the incident dataset by Year, 
    US Region, and State. Selecting the US Region will reset the selection of the State, 
    so be sure to select which US Regions you'd like to include first before configuring 
    the selected states. 
            
    The data shown in the charts are made of of three datasets (mass shooting 
    incident data from the Gun Violence Archive and the estimated population from 
    2014-2023 for each city and state from the US Census Bureau). 
""")

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

@st.cache_data(show_spinner=False)
def load_data():
    # import the state popoulation and rename the columns
    state_pop = pd.read_csv("data/cleaned_state_est_2014_2023.csv")
    # import the city population and rename the columns
    city_pop = pd.read_csv("data/cleaned_city_est_2014_2023.csv")
    state_party_color = pd.read_csv("data/state_party_color.csv")
    cleaned = pd.read_csv("data/cleaned_mass_shootings_2014-2023.csv")
    cleaned['State_Political_Color'] = cleaned["State_Name"].map(state_party_color.set_index("STATE_NAME")["COLOR"])
    
    def get_year(row, choice):
        if choice == "State_Name":
            state_name = row[choice]
            row_year = row["Year"]
            
            return state_pop[state_pop["NAME"] == state_name]["POPESTIMATE" + str(row_year)].values[0]
       
        elif choice == "City_or_County":
            city_name = row[choice]
            state_name = row["State_Name"]
            row_year = row["Year"]
            
            return city_pop[(city_pop["NAME"] == city_name) & (city_pop["STNAME"] == state_name)]["POPESTIMATE" + str(row_year)].values[0]

    cleaned["State_PopEstimate"] = cleaned.apply(get_year, args=(["State_Name"]), axis=1)
    cleaned["City_PopEstimate"] = cleaned.apply(get_year, args=(["City_or_County"]), axis=1)
    
    return cleaned

with st.spinner("Loading data... Estimated to take around 30 seconds.", show_time=True):
    cleaned = load_data()

with st.sidebar:
    st.subheader("Filter the Data")
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
    def create_scattermap(filtered, color):
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

    def create_bar(filtered, choice):
        bar_filtered = filtered[[choice, "Total_Victims", "Victims_Injured", "Victims_Killed"]]

        # organize the city data
        total_filtered = pd.DataFrame(bar_filtered.groupby(choice)[["Total_Victims", "Victims_Injured", "Victims_Killed"]].sum().sort_index())
        total_filtered.reset_index(inplace=True)
        total_filtered = total_filtered.sort_values(by="Total_Victims", ascending=False).head(10)
        total_title = "Top 10 " + choice + " by Total Victims"
        total_fig = px.bar(total_filtered, 
                                x=choice, 
                                y=["Victims_Injured", "Victims_Killed"],
                                title=total_title)
        total_fig.add_trace(go.Scatter(
            x=total_filtered[choice],
            y=total_filtered['Total_Victims'],
            text=total_filtered['Total_Victims'],
            mode='text',
            textposition='top center',
            showlegend=False
        ))
        total_fig.update_layout(
            legend=dict(
                x=0.5, 
                y=0.95,
                bgcolor='rgba(255, 255, 255, 0.75)',
                xanchor='left',
                yanchor='top',
            )
        )

        num_filtered = pd.DataFrame(bar_filtered[choice].value_counts())
        num_filtered.reset_index(inplace=True)
        num_filtered = num_filtered.sort_values(by="count", ascending=False).head(10)
        num_title = "Top 10 " + choice + " by Number of Incidents"
        num_fig = px.bar(num_filtered, 
                                x=choice, 
                                y="count",
                                title=num_title)
        num_fig.add_trace(go.Scatter(
            x=num_filtered[choice],
            y=num_filtered['count'],
            text=num_filtered['count'],
            mode='text',
            textposition='top center',
            showlegend=False
        ))
        num_fig.update_layout(
            legend=dict(
                x=0.5, 
                y=0.95,
                bgcolor='rgba(255, 255, 255, 0.75)',
                xanchor='left',
                yanchor='top',
            )
        )

        return total_fig, num_fig

    def create_dist(filtered, choice):
        dist_filtered = filtered[[choice, "Total_Victims", "Victims_Injured", "Victims_Killed"]]

        # organize the city data
        total_filtered = pd.DataFrame(dist_filtered.groupby(choice)["Total_Victims"].sum().sort_index())
        total_filtered.reset_index(inplace=True)
        total_filtered = total_filtered.sort_values(by="Total_Victims", ascending=False)
        # total_title = "Distribution of all " + choice + " by Total Victims"
        total_fig = ff.create_distplot([total_filtered['Total_Victims']], group_labels=['Total_Victims'], bin_size=50)
        total_fig.update_layout(
            legend=dict(
                x=0.5, 
                y=0.95,
                bgcolor='rgba(255, 255, 255, 0.75)',
                xanchor='left',
                yanchor='top',
            )
        )

        num_filtered = pd.DataFrame(dist_filtered[choice].value_counts())
        num_filtered.reset_index(inplace=True)
        num_filtered = num_filtered.sort_values(by="count", ascending=False)
        # num_title = "Distribution of all " + choice + " by Number of Incidents"
        num_fig = ff.create_distplot([num_filtered['count']], group_labels=['count'], bin_size=10)
        num_fig.update_layout(
            legend=dict(
                x=0.5, 
                y=0.95,
                bgcolor='rgba(255, 255, 255, 0.75)',
                xanchor='left',
                yanchor='top',
            )
        )

        return total_fig, num_fig

    def create_incidentchart(filtered, choice):
        incident_filtered = filtered[["State_Name", "City_or_County", "Incident_ID", "State_Political_Color", "Year", "State_PopEstimate", "City_PopEstimate"]]

        color_map  = {
            'RED': '#FF0000', 
            'BLUE': '#0000FF', 
            'PURPLE':'#800080'
        }

        if choice == "State_Name":
            bar_incident = pd.DataFrame(incident_filtered.groupby(["State_Name", "State_Political_Color", "Year", "State_PopEstimate"]).value_counts())
            bar_incident.reset_index(inplace=True)
            bar_incident["State_IncidentRate"] = (bar_incident["count"]/bar_incident["State_PopEstimate"])*100000
            incident_rate = pd.DataFrame(bar_incident.groupby(["State_Name", "State_Political_Color"])["State_IncidentRate"].mean())
            incident_rate.reset_index(inplace=True)
            incident_rate = incident_rate.sort_values(by="State_IncidentRate", ascending=False).head(20)

            incident_fig = px.bar(incident_rate, 
                                x=choice, 
                                y="State_IncidentRate",
                                color="State_Political_Color",
                                color_discrete_map=color_map,  # Apply the color map
                                title="Top 20 Incident Rates per 100K Residents by State")
            incident_fig.update_layout(
                legend=dict(
                    x=0.5, 
                    y=0.95,
                    bgcolor='rgba(255, 255, 255, 0.75)',
                    xanchor='left',
                    yanchor='top',
                )
            )
            incident_fig.update_xaxes(categoryorder="total descending")

        elif choice == "City_or_County":
            bar_incident = pd.DataFrame(incident_filtered.groupby(["State_Name", "City_or_County", "State_Political_Color", "Year", "City_PopEstimate"]).value_counts())
            bar_incident.reset_index(inplace=True)
            bar_incident["City_IncidentRate"] = (bar_incident["count"]/bar_incident["City_PopEstimate"])*1000
            incident_rate = pd.DataFrame(bar_incident.groupby(["State_Name", "City_or_County", "State_Political_Color"])["City_IncidentRate"].mean())
            incident_rate.reset_index(inplace=True)
            incident_rate = incident_rate.sort_values(by="City_IncidentRate", ascending=False).head(20)

            incident_fig = px.bar(incident_rate, 
                                x=choice, 
                                y="City_IncidentRate",
                                color="State_Political_Color",
                                color_discrete_map=color_map,  # Apply the color map
                                title="Top 20 Incident Rates per 1K Residents by City")
            incident_fig.update_layout(
                legend=dict(
                    x=0.5, 
                    y=0.95,
                    bgcolor='rgba(255, 255, 255, 0.75)',
                    xanchor='left',
                    yanchor='top',
                )
            )
            incident_fig.update_xaxes(categoryorder="total descending")

        return incident_fig

    # statistics on shown incidents
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Number of Incidents", filtered["Incident_ID"].count())
    col2.metric("Highest # of Injured", filtered["Victims_Injured"].max())
    col3.metric("Highest # of Killed", filtered["Victims_Killed"].max())
    col4.metric("Highest # of Total", filtered["Total_Victims"].max())  
    # give option for color plotting
    # then plot the map chart
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
    map_fig = create_scattermap(filtered, color)
    st.plotly_chart(map_fig)

    # give option for location type
    # then plot the bar charts
    tab1, tab2 = st.tabs(["By City/County", "By State"])

    with tab1:
        if pd.unique(filtered["City_or_County"]).size < 2:
            st.write("No city data to compare.")
        else:
            total_bar_fig, num_bar_fig = create_bar(filtered=filtered, choice="City_or_County")
            total_dist_fig, num_dist_fig = create_dist(filtered=filtered, choice="City_or_County")
            incident_fig = create_incidentchart(filtered=filtered, choice="City_or_County")

            city_col1, city_col2 = st.columns(2)
            with city_col1:
                st.plotly_chart(total_bar_fig)
                st.plotly_chart(num_bar_fig)
            
            with city_col2:
                st.plotly_chart(total_dist_fig)
                st.plotly_chart(num_dist_fig)
            
            st.plotly_chart(incident_fig)


    with tab2:
        if pd.unique(filtered["State_Name"]).size < 2:
            st.write("No state data to compare.")
        else:
            total_bar_fig, num_bar_fig = create_bar(filtered=filtered, choice="State_Name")
            total_dist_fig, num_dist_fig = create_dist(filtered=filtered, choice="State_Name")
            incident_fig = create_incidentchart(filtered=filtered, choice="State_Name")
            
            state_col1, state_col2 = st.columns(2)
            with state_col1:
                st.plotly_chart(total_bar_fig)
                st.plotly_chart(num_bar_fig)
            
            with state_col2:
                st.plotly_chart(total_dist_fig)
                st.plotly_chart(num_dist_fig)
            
            st.plotly_chart(incident_fig)


