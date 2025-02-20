import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import io

# helper functions for displaying things
def get_df_info(df):
    buffer = io.StringIO ()
    df.info (buf=buffer)
    lines = buffer.getvalue ().split ('\n')

    # lines to print directly
    # lines_to_print = [0, 1, 2, -2, -3]
    #for i in lines_to_print:
    st.write (lines [2])

    # lines to arrange in a df
    list_of_list = []
    for x in lines [5:-3]:
        list = x.split ()
        list_of_list.append (list)
    info_df = pd.DataFrame (list_of_list, columns=['index', 'Column', 'Non-null-Count', 'null', 'Dtype'])
    info_df.drop (columns=['index', 'null'], axis=1, inplace=True)
    st.table(info_df)

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

# session state
@st.cache_data
def load_data():
    return pd.read_csv("data/mass-shootings-2014-2023.csv")
data = load_data()

@st.cache_data
def load_cleaned():
    return pd.read_csv("data/cleaned_mass_shootings_2014-2023.csv")
cleaned = load_cleaned()

@st.cache_data
def load_trimmed_cleaned():
    victim_cols = ['Victims_Injured', 'Victims_Killed', 'Total_Victims']
    filtered = cleaned
    for i in victim_cols:
        filtered = remove_outliers(filtered, i)
    return filtered
no_outliers_cleaned = load_trimmed_cleaned()

# sidebar navigation
st.sidebar.markdown('''
    # Sections
    - [Overview of Dataset](#overview-of-dataset)
    - [Data Cleaning](#data-cleaning)
    - [Feature Engineering](#feature-engineering)
    - [Summary Statistics](#summary-statistics)
    - [Exploring Trends with Time](#exploring-trends-with-time)
    - [Exploring Trends with Location](#exploring-trends-with-location)
    ''', unsafe_allow_html=True)

# page content 
st.title("Are mass shooting incidents increasing in recent years?")
st.markdown(
    """
    This page will go through step by step the process I took to get 
    to my conclusion which you can find in the "About this Project" page.

    To set context, Mass shootings are known to be a phenomenon 
    that occurs mainly in the United States. In recent years, 
    it seems mass shootings are even more common than before. 
    Alarmed by this observation, I wanted to test if this 
    observation really were true.

    From this motivation, I want to answer the following 
    questions:
    1. Are mass shootings really more common in recent years?
    2. If so, are there any patterns in the data in regard to the date and/or location of the incident?
    3. What underlying factors may have caused these incidents?
    """
)

# data cleaning and feature engineering section
st.header("Overview of Dataset")
st.markdown(
    """
    Before doing any analysis, the first step is figuring out what kind 
    of features the dataset offers.
    
    """)
st.dataframe(data.head())
get_df_info(data)

st.markdown(
    """
    From these columns, we have 4683 observations and 18 columns. Out of the 18 columns,
    I'm particularly interested in analyzing **location** and **time**
    in regards to **victim** data:
    - **Time**: Incident_Date, Incident_Time, Year, Month, Day
    - **Location**: State_Name, State_Name, Business_or_Location_Name, Address, Latitude, Longitude
    - **Victims**: Victims_Injured, Victims_Killed
    
    Before going straight into analyzing the data from these features, it's important to 
    see if there's any NA's in any of the columns but most specifically the 
    columns of interest. 
    """
)

# data cleaning section
st.header("Data Cleaning")
st.markdown(
    """
    We have seen what the dataset has to offer and have an idea of the features of interest. 
    I now want to know the total number of NA's in each column. This will determine 
    whether we can actually use those columns.
    
    """)
st.table(pd.DataFrame(data.isna().sum(), columns=['Num of NAs']))

st.markdown(
    """
    From the 18 columns, 3 columns have a non-zero total of NA's. 
    
    Looking at these three columns, they don't have too much of an impact on the 
    questions we're trying to answer. 
    - For location, we have all rows with at least city and state name, meaning we 
    don't need the additional level of granularity that address or busines/location 
    name would provide. 
    - For time, we have all rows with the year, month, and day information. Just like with 
    the 'Address' and 'Business_or_Location_Name', the level of granularity from 'Incident_Time' 
    is not needed.
    
    Because of this, we can safely disregard these columns and keep all
    incident rows.

    We have a good pulse on what all the columns are besides 'Incident_Characteristics'. 
    I want to look more deeply into what kind of values are in the column.
    """)

st.table(data['Incident_Characteristics'].head())

st.markdown(
    """
    Looking through the 'Incident_Characteristics' column, the values seem to be 
    sentences that vary greatly between each observation. Because we're particularly 
    interested in the time and location of the incidents, we don't need to worry about 
    this variation and safely **leave out this column** in our final dataset.

    Now that we understand the features we're sure we want to work with, it's now a good 
    time to look into the observations and see if we need to drop any rows.
    """
)

st.markdown(
    """
    First, we want to make sure all observations are indeed mass shootings which
    is defined by the Gun Violence Archive as:
    - **mass shooting**: a shooting with a minimum four victims shot, either injured 
    or killed, not including any shooter who may also have been killed or injured 
    in the incident. 

    Out of the all the obervations, these rows don't fulfill that requirement:    
    """
)

st.dataframe(data[(data['Victims_Injured'] + data['Victims_Killed']) < 4])

st.markdown(
    """
    Because we have 4683 observations in the dataset, we can safely **remove these 
    4 incidents** from the dataset and carry on with feature engineering.

    Next, let's look at the victim data and see if there are any outliers we need to 
    get rid as it may sway statistics like mean, standard deviation, variance, etc.
    """
)

# set up plotly object
option = st.selectbox(
    "Choose a feature to view from the original dataset",
    ("Victims_Injured", "Victims_Killed")
)
df_box = data[option]
fig = px.box(df_box, y=option)

# display plotly object on website
st.plotly_chart(fig, on_select="rerun")

st.markdown(
    """
    We see a huge outlier in the 'Victims_Injured' column and several outliers in the 
    'Victims_Killed' column. 

    Though we have several outliers, it may be important to keep them for visualizing 
    purposes and see where they trend in location. Because of this, we will keep all of 
    the rows but keep in mind when plotting statistics that can be affecte by these 
    outliers.

    We're done with cleaning! It's now time for feature engineering.
    """
)


# feature engineering section
st.header("Feature Engineering")
st.markdown(
    """
    From our data cleaning exercise, we have the following columns of interest:
    - **Time**: Incident_Date, Year, Month, Day
    - **Location**: State_Name, State_Name, Latitude, Longitude

    Because mass shootings are defined by the victims, **any columns related 
    to the suspects will not be used from the dataset**. This leaves us with 
    the following columns: 
    - **Victim**: Victims_Injured, Victims_Killed

    Now that we have our columns of interest, a couple of new columns I want to create is: 
    - **US_Region**: The level of granularity from the national to state is too narrow. It 
    would be interesting to have a level in-between to observe how a state plays in a portion 
    of the nation
    - **Total_Victims**: since injured and killed victims have no correlation to each other 
    (suspects ususally set out to kill, not just injure), it would be interesting to have this 
    as a feature to analyze
    """
)

# some summary statistics
st.header("Summary Statistics")
st.markdown(
    """
    Now that we have our data, I want to perform some basic data analysis and gather 
    basic summary statistics to see how the data looks.
    """
)

st.table(cleaned[['Victims_Injured', 'Victims_Killed', 'Total_Victims']].describe())

col1,col2,col3,col4 = st.columns(4)

with col1:
    # chart for year
    st.table(cleaned["Year"].value_counts())

with col2:
    # chart for month
    st.table(cleaned["Month"].value_counts())

with col3:
    # chart for month
    st.table(cleaned["State_Name"].value_counts().head(10))

with col4:
    # chart for month
    st.table(cleaned["City_or_County"].value_counts().head(10))

st.markdown(
    """
    A few things of note here:
    1. The years during and after the pandemic saw a growth in incidents.
    2. The warmer months have more incidents. 
    3. The top states and cities are those with a higher populations.
    4. The statistics for the victims are skewed because of the inclusion of all outliers.
    """
)

st.table(no_outliers_cleaned[['Victims_Injured', 'Victims_Killed', 'Total_Victims']].describe())

# set up plotly object
option = st.selectbox(
    "Choose a feature to view from the trimmed dataset",
    ("Victims_Injured", "Victims_Killed")
)
df_box = no_outliers_cleaned[option]
fig = px.box(df_box, y=option)

# display plotly object on website
st.plotly_chart(fig, on_select="rerun")

st.markdown(
    """
    These summary statistics of the victim data look more true to the average. 

    It is important to keep in mind that a minimum of 0 in both the "Victims_Injured" and 
    "Victims_Killed" is normal since a mass shooting can be 4 injured victims or 4 
    killed victims, and the total would still be 4 total victims for either 
    scenario.
    """
)

# exploring incident trends in relation to time
st.header("Exploring Trends with Time")
st.markdown(
    """
    We've taken a look at the data as a whole. It's time to look at the data in one 
    of the two aspects I mentioned before: Time.

    As a refresher, the features I'll be using for the exploration are: **Year** and 
    **Month**. Though we have Day, the Month and Year of the incident will suffice 
    in showing the trends of these incidents.

    I'll first be exploring the number of incidents per year before diving into how 
    the incidents break down by month. 
    """
)

num_incidents_line = pd.DataFrame(cleaned.groupby(['Year'])['Incident_ID'].count())
num_incidents_line.reset_index(inplace=True)
fig_num_incidents_line = px.line(num_incidents_line, x='Year', y='Incident_ID', title='Number of Incidents per Year')
fig_num_incidents_hist = ff.create_distplot([num_incidents_line['Incident_ID']], group_labels=['Incident_ID'], bin_size=100)

# display plotly object on website
num_incidents_col_chart1, num_incidents_col_chart2 = st.columns(2)

with num_incidents_col_chart1:
    st.plotly_chart(fig_num_incidents_line, on_select="rerun")

with num_incidents_col_chart2:
    st.plotly_chart(fig_num_incidents_hist, on_select="rerun")

# set up line chart for year plotting
# set up plotly object
victim_option = st.selectbox(
    "Choose which victim variable to view in 'Year'",
    ("Victims_Injured", "Victims_Killed", "Total_Victims")
)

df_line = pd.DataFrame(cleaned.groupby(['Year'])[victim_option].sum().sort_index())
df_line.reset_index(inplace=True)
if victim_option in ["Victims_Injured", "Victims_Killed"]:
    victim_text = victim_option.split("_")[1]
    title_string = "Number of Victims " + victim_text + " per Year"
else:
    title_string = "Total Number of Victims per Year"
fig_line = px.line(df_line, x='Year', y=victim_option, title=title_string)
fig_hist = ff.create_distplot([df_line[victim_option]], group_labels=[victim_option], bin_size=100)

# display plotly object on website
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.plotly_chart(fig_line, on_select="rerun")

with col_chart2:
    st.plotly_chart(fig_hist, on_select="rerun")

st.markdown(
    """
    We plot the total number of victims, number of victims killed, and number of victims injured
    and see a noticeable spike in the number after 2019. In order to make sure that this 
    spike is statistically significant, we plot the numbers on a distribution plot or 
    histogram and see a bimodal distribution.

    Both of these charts match the charts shown by the number of incidents per year. This makes 
    sense as the number of victims are caused by an incident.

    This bimodal distribution tells us there is a two high points in the data, meaning the 
    spike is considerable enough to cause the distribtution to have two high points. This trend 
    is seen for all three victim statistics and again matches the statistics for number of 
    incidents.

    Let's look at the trends by 'Month' now.
    """
)


df_num_incidents = pd.DataFrame(cleaned[cleaned['Year'] == 2014]['Month'].value_counts().sort_index())
df_num_incidents.reset_index(inplace=True)
temp_name = 'Num_Incidents' + str(2014)
df_num_incidents = df_num_incidents.rename(columns={'count': temp_name})

for i in range(2015, 2024):
    temp_year = pd.DataFrame(cleaned[cleaned['Year'] == i]['Month'].value_counts().sort_index())
    temp_year.reset_index(inplace=True)
    column_name = 'Num_Incidents' + str(i)
    temp_year = temp_year.rename(columns={'count': column_name})

    df_num_incidents = pd.concat([df_num_incidents, temp_year[column_name]], axis=1)
df_num_incidents = df_num_incidents.set_index('Month')

num_incidents_month = px.line(df_num_incidents, title='Number of Incidents per Month')
st.plotly_chart(num_incidents_month, on_select="rerun")

# set up line chart for month plotting
victim_month_option = st.selectbox(
    "Choose which victim variable to view in 'Month'",
    ("Victims_Injured", "Victims_Killed", "Total_Victims")
)

if victim_month_option in ["Victims_Injured", "Victims_Killed"]:
    victim_text = victim_month_option.split("_")[1]
    month_title_string = "Number of Victims " + victim_text + " per Month"
else:
    month_title_string = "Total Number of Victims per Month"

df_month = pd.DataFrame(cleaned[cleaned['Year'] == 2014].groupby(['Month'])[victim_month_option].sum().sort_index())
df_month.reset_index(inplace=True)
temp_name = victim_month_option + str(2014)
df_month = df_month.rename(columns={victim_month_option: temp_name})

for i in range(2015, 2024):
    temp_year = pd.DataFrame(cleaned[cleaned['Year'] == i].groupby(['Month'])[victim_month_option].sum().sort_index())
    temp_year.reset_index(inplace=True)
    column_name = victim_month_option + str(i)
    temp_year = temp_year.rename(columns={victim_month_option: column_name})

    df_month = pd.concat([df_month, temp_year[column_name]], axis=1)
df_month = df_month.set_index('Month')

# outliers removed
df_month_no_outliers = pd.DataFrame(no_outliers_cleaned[no_outliers_cleaned['Year'] == 2014].groupby(['Month'])[victim_month_option].sum().sort_index())
df_month_no_outliers.reset_index(inplace=True)
temp_name = victim_month_option + str(2014)
df_month_no_outliers = df_month_no_outliers.rename(columns={victim_month_option: temp_name})

for i in range(2015, 2024):
    temp_year = pd.DataFrame(no_outliers_cleaned[no_outliers_cleaned['Year'] == i].groupby(['Month'])[victim_month_option].sum().sort_index())
    temp_year.reset_index(inplace=True)
    column_name = victim_month_option + str(i)
    temp_year = temp_year.rename(columns={victim_month_option: column_name})

    df_month_no_outliers = pd.concat([df_month_no_outliers, temp_year[column_name]], axis=1)

df_month_no_outliers = df_month_no_outliers.set_index('Month')

no_outliers_title = month_title_string + " - No Outliers"
fig_month_no_outliers = px.line(df_month_no_outliers, title=no_outliers_title)
fig_month = px.line(df_month, title=month_title_string)

st.plotly_chart(fig_month, on_select="rerun")
st.plotly_chart(fig_month_no_outliers, on_select="rerun")

st.markdown(
    """
    We can see a confirmation of what we saw in the summary statistics: **Summer 
    months have more incidents (and therefore victims) compared to other months**.
    """
)

# exploring incident trends in relation to time
st.header("Exploring Trends with Location")
st.markdown(
    """
    After taking a look at the incidents by time, it would be interesting if 
    there is a factor location plays in mass shootings.
    """
)