# streamlit run main.py

import streamlit as st
from PIL import Image
import requests
import pandas as pd
from fuzzywuzzy import process
from io import BytesIO

class f1():
    def __init__(self):
        st.set_page_config(layout="wide")

        self.navigation = ''
        self.pilot_name = ''
        self.all_pilots = ''
        self.driverid = ''
        self.driver_details = ''

        self.main_page()

    def main_page(self):
        self.side_bar()

        col1, col2 = st.columns([9,2])

        with col1:
            st.title('F1 Data Visualization')
        with col2:
            st.markdown(' ')
            st.markdown(' ')
            st.image(Image.open('assets/f1-logo.png'))

        if self.navigation == 'Pilot':
            self.pilot_page()

        if self.navigation == 'Championship':
            self.championship_page()

        if self.navigation == 'Circuit':
            self.circuit_page()

        if self.navigation == 'Race':
            self.race_page()

    def side_bar(self):
        with st.sidebar:
            st.header('Navigate')

            self.navigation = st.radio(
                "Go to:",
                ("Circuit", "Championship", "Pilot", "Race")
            )

            if self.navigation == 'Pilot':
                #Cache
                self.all_pilots = query_all_pilots()

                # Search name
                st.subheader('Search pilot')

                pilot_name_search = st.text_input('Pilot name', 'Lewis')

                response = query_driver(self.all_pilots, pilot_name_search)

                # Select pilot
                self.pilot_name = st.selectbox(
                f'Pilots with a name similar to {pilot_name_search}',
                tuple(response))

                # Select period
                st.subheader('Select period')
                self.period = st.slider('Year: ', 1960, 2022, (1996, 2022))

    def circuit_page(self):
        st.header('Circuit')

    def race_page(self):
        st.header('Race')

    def championship_page(self):
        st.header('Championship')

    def pilot_page(self):

        driverid = self.all_pilots[self.all_pilots['Name'] == self.pilot_name]['driverId'].values[0]
        driver_details = query_driver_detail(driverid)
        
        st.header(self.pilot_name)

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

        try:
            wiki_url = self.all_pilots[self.all_pilots['Name'] == self.pilot_name]['url'].values[0]
            fig = query_driver_photo(wiki_url)
        except:
            c1r1.image(Image.open('assets/profile-placeholder.jpg'))
        else:
            c1r1.image(fig)

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

def query_all_pilots():
    data = requests.request("GET", 'http://ergast.com/api/f1/drivers?limit=10000').text
    pilots = pd.read_xml(
        data,
        namespaces = {'doc': "http://ergast.com/mrd/1.5"},
        xpath = './/doc:Driver'
    )
    pilots = pilots.assign(Name = pilots[['GivenName', 'FamilyName']].apply(' '.join, axis = 1)).drop(['GivenName', 'FamilyName'], axis = 1)

    return pilots

def query_driver(all_pilots, name):
    
    similar_pilots = process.extractBests(name, all_pilots['Name'].to_list(), limit = 10, score_cutoff=80)
    similar_pilots_list = []
    for i in similar_pilots:
        similar_pilots_list.append(i[0])

    return similar_pilots_list

def query_driver_photo(url):
    text = requests.request("GET", url).text

    sample = "//upload.wikimedia.org/wikipedia/commons/thumb"

    start = text.find(sample)
    end = text[start:].find('"')

    response = requests.get('https:' + text[start:(start + end)])
    
    return Image.open(BytesIO(response.content))

def query_driver_detail(driver_id):
    driver_details = []

    data = requests.request("GET", 'http://ergast.com/api/f1/drivers/' + driver_id).text
    drivers =  pd.read_xml(
        data,
        namespaces = {'doc': "http://ergast.com/mrd/1.5"},
        xpath = './/doc:Driver'
        )
    
    driver_details.append(drivers['Nationality'][0])

    return driver_details

instance = f1()