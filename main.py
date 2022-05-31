# streamlit run main.py

import streamlit as st
from PIL import Image
import requests
import pandas as pd

st.set_page_config(layout="wide")

def query_driver(name):
    
    return requests.request("GET", 'http://ergast.com/api/f1/drivers?=123')

def circuit_page():
    st.header('Circuit')

def race_page():
    st.header('Race')

def championship_page():
    st.header('Championship')

def pilot_page(data):
    st.header(data[1])

    c1r1, c2r1, c3r1 = st.columns(3)

    c2r1.markdown(f'**Victories:** {10}')
    c2r1.markdown(f'**Poles:** {8}')
    c2r1.markdown(f'**World Championships:** {0}')
    c2r1.markdown(f'**Constructor championship:** {1}')
    c2r1.markdown(f'**Country:** {1}')

    c3r1.markdown(f'**Races:** {10}')
    c3r1.markdown(f'**Podiums:** {10}')
    c3r1.markdown(f'**Status:** {10}')
    c3r1.markdown('**Actual Team:** ' + 'Mercedes')
    teams = ['Mercedes', 'Ferrari']
    if len(teams)>1:
        teams_f = ''
        for i in teams[:-1]:
            teams_f += i + ', '
        teams_f += teams[-1]
        c3r1.markdown(f'**Team:** {teams_f}')
    else:
        c3r1.markdown(f'**Team:** {teams[0]}')

    c1r1.image(Image.open('assets/LH.jpg'))

    st.subheader('Actual World Championship Results')
    # If status is not retired:
        # Actual championship info:
            # Points
            # Victories
            # Podiuns
            # Poles
            # Team

    st.subheader('Past World Championship Results')
    # If exist
        # Past champioship info 


def side_bar():
    with st.sidebar:
        st.header('Navigate')
        navigation = st.radio(
            "Go to:",
            ("Circuit", "Championship", "Pilot", "Race")
        )

        if navigation == 'Pilot':
            # Search name
            st.subheader('Search pilot')

            pilot_name_search = st.text_input('Pilot name', 'Lewis')

            response = query_driver(pilot_name_search)

            # print(dir(response))
            # print(response.text)
            # print(pd.read_html('http://ergast.com/api/f1/drivers?=123'))

            # Select pilot
            pilot_name = st.selectbox(
            f'Pilots with a name similar to {pilot_name_search}',
            ('Lewis Hamilton', 'Lewis Lamilton', 'Lewis Gamilton'))

            # Select period
            st.subheader('Select period')
            period = st.slider('Year: ', 1960, 2022, (1996, 2022))

            data = [navigation, pilot_name, period]

        return data

def main_page():
    data = side_bar()
    nav = data[0]
    col1, col2 = st.columns([9,2])

    with col1:
        st.title('F1 Data Visualization')
    with col2:
        st.markdown(' ')
        st.markdown(' ')
        st.image(Image.open('assets/f1-logo.png'))

    if nav == 'Pilot':
        pilot_page(data)

    if nav == 'Championship':
        championship_page()

    if nav == 'Circuit':
        circuit_page()

    if nav == 'Race':
        race_page()

main_page()