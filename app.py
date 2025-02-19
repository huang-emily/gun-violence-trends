import streamlit as st
import pandas as pd
import numpy as np
import time

pages = {
    "Project Details": [
        st.Page("project_pages/1-High_Level_Overview.py", title="High Level Overview"),
        st.Page("project_pages/2-Full_Project_Details.py", title="Full Project Details")
    ],
    "Visualize":[
        st.Page("project_pages/3-Incidents_by_Location.py", title="Incidents by Location"),
        st.Page("project_pages/4-Incidents_by_Time.py", title="Incidents by Time")
    ]
}

pg = st.navigation(pages)
pg.run()