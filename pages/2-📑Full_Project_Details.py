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
    - [Understanding the Underlying Reason](#understanding-the-underlying-reason)
    - [Takeaways](#takeaways)
    - [Sources Used](#sources-used)
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

    Using the Data Visualization page as reference, we can take a look at the data 
    with "time" in mind. 

    As a refresher, the features I'll be taking a look at for time are **Year** and 
    **Month**. Though we have Day, the level of granularity that it provides is too 
    precise for what we want tofigure out. **Month** and **Year** provide the level of 
    granularity that we want to analyze since it aligns well with seasons and holidays.

    When looking at **Year** with the total number of victims, number of victims killed, 
    and number of victims injured, we see a noticeable spike in these numbers after 2019. 
    In order to make sure that this spike is statistically significant, we also plot the 
    distribution plots or histograms which again are located in the Data Visualization page.

    When we compare the histograms with the line charts, we can see that the spike is 
    statistically significant as the histograms show a bimodal distribution which means 
    the spike was enough to create two hills rather the one which is the norm. To be 
    clear, the bimodal distribution is present in all statistics, meaning there is a 
    meaningful spike in incidents. 

    Factors like the political climate, unemployment, and racial inequality may have 
    played a part in this rise of incidents.

    When looking at the **Month** with the total number of victims, number of victims 
    killed, and number of victims injured, we see that our initial findings from the summary 
    statistics ring true, **Summer months do indeed have more incidents (and therefore more 
    victims) compared to others month in the a given year.**

    There are a number of reasons why this could be the case:
    - The summer months tend to be when families are on vacation, meaning there are more people 
    outside exposed to other people.
    - Because of the hot weather during these months in the US, people are also incentivized to 
    go outside and expose themselves to other people.
    - Both previous statements may be especially true after a long period of social isolation 
    caused by COVID.

    Now that we've taken a look at the data with respect to time, we'll now take a look at 
    the data with respect to location.

    """
)

# exploring incident trends in relation to time
st.header("Exploring Trends with Location")
st.markdown(
    """
    
    Again, using the Data Visualization page as reference, we can take a look at the data 
    with "location" in mind. 

    Starting with US Region, we see some interesting statistics:
    
    For the Norteast,
    - 13.21% of all unique reported incidents
    - 12.38% of all victims involved in any incident
    - 13.21% of all injured victims involved in any reported incident
    - 9.02% of all killed victims involved in any reported incident
    
    For the Midwest, 
    - 26.18% of all unique reported incidents
    - 25.28% of all victims involved in any incident
    - 25.84% of all injured victims involved in any reported incident
    - 23.00% of all killed victims involved in any reported incident

    For the South,
    - 45.24% of all unique reported incidents
    - 45.24% of all victims involved in any incident
    - 44.54% of all injured victims involved in any reported incident
    - 48.09% of all killed victims involved in any reported incident

    For the West, 
    - 15.37% of all unique reported incidents
    - 17.09% of all victims involved in any incident
    - 16.41% of all injured victims involved in any reported incident
    - 19.88% of all killed victims involved in any reported incident

    Looking over these numbers, we see that South makes up nearly half of all recorded incidents 
    in the data. This is true across all the victim statistics too. If we include both Midwest 
    and the South, these two regions make up nearly majority of the incidents in the data base. 
    This raises an interesting question of whether or not political leanings have an effect on 
    whether an incident occurs in a location or not since an overwhelming amount of the red states 
    are in the South and Midwest regions of the USA. 
    
    When we look at the states and cities with the most incidents, unsurprisingly the states and 
    cities with a higher population are more likely to have a higher number of incidents. This is 
    intuitive since higher density regions tend to have a higher crime rate, meaning residents have 
    a higher likelihood of being victims of a shooting.
    
    In order to compare each state and city at a more similar level, we calculate the incident rate 
    for each state. This is calculated by: 
    1. Get the number of incidents that occur in a specific year
    2. Divide the incident number for that year by the population recorded by the Census Bureau that year
    3. Repeat steps 1 and 2 until you get the incident rate for each year from 2014 - 2023
    4. Get the average incident rate for all calculated years. 

    With the incident rate calculated on both the state and city level, we can now compare all states 
    and cities to similar grounds. From here, we can see that our observation from the US Region 
    level of granularity that the cities and states from red states make up a good portion of locations 
    with the highest incident rates.
    
    From these observations in the data, there may be some pattern occurring where locations in the South 
    have a higher rate of mass shootings compared to other locations.
    
    """
)

# exploring incident trends in relation to time
st.header("Understanding the Underlying Reason")
st.markdown(
    """
    From our observations of the data in the lens of "time" and "location", we see that there is a more 
    obvious pattern with the "location", namely locations that lean more towards conservative or Republican 
    see a higher rate of mass shooting incidents compared to locations that lean more towards liberal or 
    Democratic. 
    
    This observation may cause a question to pop up: "Why do locations that lean more Red have higher incident 
    rates?" From this article, Red states have historically been pro-Second amendment, making their lawmakers 
    more likely to make guns more accessible. However, we can see from the chart in the article that looser guns 
    laws are associated with higher gun deaths. 

    """
)

st.image("images/In Red States, ‘Gun Reform’ Means Making It Easier To Buy And Carry Guns.png")
st.image("images/potts_guns-red-states_0513-standard-2.png")

st.markdown(
    """
    On top of that, Americans as a whole are acquiring more guns. Charts from the Bureau of Alcohol, 
    Tobacco, Firearms and Explosives show a similar pattern to the “Number of Incidents each Year” 
    chart where there is a sudden spike after 2019. 

    """
)

st.image("images/increase-in-ghost-guns-recover.png")
st.image("images/nfa_firearms_processed_fy23.png")
st.image("images/nfa_forms_processed_fy23_v2.png")

# exploring incident trends in relation to time
st.header("Takeaways")
st.markdown(
    """
    From this study, we were able to observe that mass shootings were in fact more frequent as 
    of recent years. Incidents were likely to occur during the summer months when more traveling 
    was done, but incidents were notably more frequent in Red states where gun laws are more 
    lenient compared to Purple and Blue states. 

    However, as a whole, the United States is acquiring more guns, and more access to guns means 
    more opportunities for mass shootings to occur regardless of location. It seems if we as a country 
    are looking to lower the rate of mass shootings occuring nationwide, the solution may to restrict 
    or ban gun ownership rather than allow more people to gain access to them. 

    """
)


st.header("Sources Used")
st.markdown(
    """
    The following resources were used to support the study conducted.
    
    Articles:
    - [Ammo Article on How Many Guns in the US](https://ammo.com/articles/how-many-guns-in-the-us)
    - [ATF Data Statistics](https://www.atf.gov/resource-center/data-statistics)
    - [FiveThirtyEight Article on Republican Expanding Gun Rights](https://fivethirtyeight.com/features/republican-states-expanding-gun-rights-mass-shootings/)

    Assisting Data Sources:
    - [Harvard Dataverse Dataset for Political Leaning by State](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/42MVDX)
    - [US Census Bureau Dataset for State and City Population](https://www.census.gov/data/datasets.html)
    
    """
, unsafe_allow_html=True)