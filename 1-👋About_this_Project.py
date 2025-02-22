import streamlit as st

st.set_page_config(page_title="About this Project")

st.title("About this Project")
st.markdown(
    """
    This project was created by Emily Huang. To view the project files, visit the [Github repo](https://github.com/huang-emily/gun-violence-trends/tree/main). 

    ## Motivation
    Mass shootings are known to be a phenomenon that occurs mainly in the United States. In recent years, it seems mass shootings are even more common than before. Alarmed by this observation, I wanted to test if this observation really were true.

    ## Tools used
    - **Data Analysis**: Python (Numpy, Pandas), SQL
    - **Visualizations**: Power BI, Python (Matplotlib, Plotly, Seaborn, Streamlit)
    - **Code Management**: SQL Server Management Studio, Jupyter Notebook

    ## Proposed Questions
    1. Are mass shootings really more common in recent years?
    2. If so, are there any patterns in the data in regard to the date and/or location of the incident?
    3. What underlying factors may have caused these incidents?

    ## About the Dataset

    The original data on mass shootings is from the [Gun Violence Archive](https://www.gunviolencearchive.org/), and the compiled dataset is from [figshare](https://figshare.com/articles/dataset/Gun_Violence/14552136).

    This analysis will be using the compiled dataset which contains additional columns of the separated year, month, and date of the incident.

    The Gun Violence Archive defines mass shootings as a minimum of four victims shot, either injured or killed, not including any shooter who may also have been killed or injured in the incident.

    Two other datasets were used to assist in this study:
    - [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/42MVDX) - obtaining state-level presidential results
    - [US Census Bureau](https://www.census.gov/data/datasets.html) - obtaining population estimates for all states

    ## Findings

    From this study, we were able to observe that mass shootings were in fact more frequent as of recent years. Incidents were likely to occur during the summer months when more traveling was done, but incidents were notably more frequent in Red states where gun laws are more lenient compared to Purple and Blue states. 

    However, as a whole, the United States is acquiring more guns, and more access to guns means more opportunities for mass shootings to occur regardless of location. 
    """)