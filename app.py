import streamlit as st
import pandas as pd
import numpy as np
import time

pages = {
    "At a Glance": [
        st.Page("project_pages/motivation.py", title="Motivation for Project"),
        st.Page("project_pages/eda.py", title="Exploratory Data Analysis"),
        st.Page("project_pages/about.py", title="About this Project")
    ],
    "Visualize":[
        st.Page("project_pages/visualize_location.py", title="Incidents by Location"),
        st.Page("project_pages/visualize_time.py", title="Incidents by Time")
    ]
}

pg = st.navigation(pages)
pg.run()