"""
Class: CS230--Section 3
Name: Erica Estrella
Description: Final Project
I pledge that I have completed the programming assignment independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
"""
import pydeck as pdk
import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import calendar


@st.cache_data
def convertDF(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def graph(data):
    fig, ax = plt.subplots(figsize=(10, 6))
    counts = data['OFFENSE_DESCRIPTION'].value_counts() # counts the occurrences of each unique value in description column
    return fig, ax, counts

def lineChart(df):
    st.subheader("Total Incidents by Month For 2023")

    fig, ax = plt.subplots(figsize=(10, 6))
    incidents = df.groupby('MONTH')['INCIDENT_NUMBER'].count() # df that counts total incidents grouped by month
    incidents = incidents.rename('Total Incidents')

    months = [calendar.month_name[i] for i in incidents.index] # list of month names

    ax.plot(months, incidents.values, marker='o', linestyle='-') # designates x and y axis values and other specifics for plot
    ax.set_xlabel('Month')
    ax.set_ylabel('Total Incidents')
    ax.set_title('Total Incidents Across All Months')
    st.pyplot(fig)
    st.write(incidents)

def selections(df):
    monthDict = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August',
                 9: 'September', 10: 'October', 11: 'November'}
    selectedMonth = st.selectbox("Select a month", list(monthDict.values()))
    dow = st.selectbox("Select a day of the week", df['DAY_OF_WEEK'].unique())
    monthNum = [key for key, value in monthDict.items() if value == selectedMonth][0]  # finds the correspondng value for the month selected in dictionary
    return selectedMonth, dow, monthNum

def pieChart(df, top = 10):
    st.subheader("Crime Distribution by Month and Day of the Week")
    selectedMonth, dow, monthNum = selections(df)
    data = df[(df['DAY_OF_WEEK'] == dow) & (df['MONTH'] == monthNum)]  # filters the data based on user selection

    fig, ax, counts = graph(data)  # calls for the graph function
    topCodes = counts.head(top)  # filters data by the top 10 offense codes for less clutter, learned by watching https://youtu.be/rxWkIn1EZnM?si=l7WngNzp3pyva-zK
    ax.pie(topCodes, labels=topCodes.index, autopct='%1.1f%%')  # sets the labels and percent format for visual purposes

    ax.set_title(f'Top {top} Crime Distribution on {dow} for the month of {selectedMonth}')
    st.pyplot(fig)

def map(df):
    st.subheader("Crime Location Map")
    selectedMonth, dow, monthNum = selections(df)

    offenseDescription = ['All'] + list(df['OFFENSE_DESCRIPTION'].unique()) # options for select box
    selection = st.selectbox('Select Offense Code', offenseDescription)

    if selection == 'All':
        data = df[(df['DAY_OF_WEEK'] == dow) & (df['MONTH'] == monthNum)] # displays all coffense codes, default
    else:
        data = df[(df['DAY_OF_WEEK'] == dow) & (df['MONTH'] == monthNum) & (df['OFFENSE_DESCRIPTION'] == selection)] # else displays selected coffense codes

    mapDF = data[['OFFENSE_DESCRIPTION', 'OCCURRED_ON_DATE', 'Lat', 'Long']] # creates a data frame with data for map

    view = pdk.ViewState(latitude=42.3601, longitude=-71.0589, zoom=12)  # inital map view long and lat

    offense = mapDF['OFFENSE_DESCRIPTION'].unique() # array with all unique values of offense description
    color = {code: [random.randint(0, 200) for i in range(3)] for code in offense}
    mapDF['color'] = mapDF['OFFENSE_DESCRIPTION'].map(color)
    mapDF['radius'] = 65

    layer = pdk.Layer(
        'ScatterplotLayer',
        data=mapDF,
        get_position='[Long, Lat]',
        get_radius='radius',
        get_color='color',
        pickable=True
    )

    tooltip = {'html': 'Occurrence Date: <b>{OCCURRED_ON_DATE}</b>', 'style': {'backgroundColor': 'steelblue', 'color': 'white'}}

    deck = pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v10',
        layers=[layer],
        initial_view_state=view,
        tooltip=tooltip
    )

    st.pydeck_chart(deck)

def barChart(df):
    st.subheader("Crime Distribution by Street")
    selectedMonth, dow, monthNum = selections(df)
    street = st.text_input("Enter the street name:").upper()  # user input

    data = df[(df['STREET'] == street) & (df['DAY_OF_WEEK'] == dow) & (df['MONTH'] == monthNum)]  #  filters data based on user input for street and dow

    st.subheader("Bar Chart - Crime Codes for Selected Street and Day")

    fig, ax, counts = graph(data)  #  calls for graph function

    counts = counts.sort_values(ascending=False)  # sorts data from largest to smallest
    ax.bar(counts.index, counts.values)  #  creates bar graph for count index as x-axis and values for y-axis
    ax.set_xlabel('Crime Code')
    ax.set_ylabel('Number of Crimes')
    ax.set_title(f'Crime Distribution on {dow} for {selectedMonth}')
    ax.tick_params(axis='x', rotation=90) #  rotates x-axis labels 90 degrees
    st.pyplot(fig)

def main():
    df = pd.read_csv('bostoncrime2023.csv', header=0)

    st.title("Boston Crimes Analysis")

    st.subheader(f"The purpose of this website is to help law enforcement keep track of crimes in the greater Boston area."
                 f"\nUse the buttons to the right to choose the information you wish to view"
                 f"\n\nTo download the csv used, press the button below!")


    csv = convertDF(df)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='bostoncrime2023.csv',
        mime='text/csv',
    )

    image = Image.open('image2.jpg')
    st.image(image)

    tabs = ["Total Incidents by Month For 2023", "Crime Distribution by Month and Day of Week", "Crime Location Map",
            "Crime Distribution by Street"]  # tab names
    selectedTab = st.sidebar.radio("Select a tab", tabs)

    if selectedTab == "Total Incidents by Month For 2023":
        lineChart(df)

    elif selectedTab == "Crime Distribution by Month and Day of Week":
        pieChart(df)

    elif selectedTab == "Crime Location Map":
        map(df)

    elif selectedTab == "Crime Distribution by Street":
        barChart(df)

if __name__ == "__main__":
    main()
