# streamlit run main.py

import streamlit as st
from PIL import Image
import requests
import pandas as pd
from fuzzywuzzy import process
from io import BytesIO
import xml.etree.ElementTree as ET
from datetime import date

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

        if self.navigation == 'Driver':
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
                ("Circuit", "Championship", "Driver", "Race")
            )

            if self.navigation == 'Driver':
                #Cache
                self.all_pilots = query_all_pilots()

                # Search name
                st.subheader('Search driver')

                pilot_name_search = st.text_input('Driver name', 'Lewis')

                response = query_driver(self.all_pilots, pilot_name_search)

                # Select pilot
                self.pilot_name = st.selectbox(
                f'Drivers with a name similar to {pilot_name_search}',
                tuple(response))

    def circuit_page(self):
        st.header('Circuit')

    def race_page(self):
        st.header('Race')

    def championship_page(self):
        st.header('Championship')

    def pilot_page(self):

        drivers = self.all_pilots[self.all_pilots['Name'] == self.pilot_name]['driverId'].values
        if len(drivers) > 0:
            driverid = drivers[0]
            driver_details = query_driver_detail(driverid)
            
            st.header(self.pilot_name)

            c1r1, c2r1, c3r1 = st.columns(3)

            c2r1.markdown(f'**World Championships:** {driver_details[8]}')
            c2r1.markdown(f'**Victories:** {driver_details[6]}')
            c2r1.markdown(f'**Poles:** {driver_details[1]}')
            c2r1.markdown(f'**Nationaliy:** {driver_details[0]}')
            c2r1.markdown('**Last Team:** ' + driver_details[4])

            status = 'Active' if driver_details[5]==True else 'Retired'

            c3r1.markdown(f'**Races:** {driver_details[3]}')
            c3r1.markdown(f'**Podiums:** {driver_details[7]}')
            c3r1.markdown(f'**Status:** {status}')
            teams = driver_details[2]

            if len(teams)>1:
                teams_f = ''
                for i in teams[:-1]:
                    teams_f += i + ', '
                teams_f += teams[-1]
                c3r1.markdown(f'**Team:** {teams_f}')
            else:
                c3r1.markdown(f'**Team:** {teams[0]}')


            if(status == 'Active'):
                st.subheader('Actual World Championship Results')
                
                data = query_driver_actual_details(driverid)
                
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown('**Position**')
                    st.markdown(data[0])

                with col2:
                    st.markdown('**Points**')
                    st.markdown(data[1])

                with col3:
                    st.markdown('**Wins**')
                    st.markdown(data[2])
                    

            st.subheader('Past World Championship Results')
            st.write(driver_details[9])

            # try:
            #     wiki_url = self.all_pilots[self.all_pilots['Name'] == self.pilot_name]['url'].values[0]
            #     fig = query_driver_photo(wiki_url)
            # except:
            #     c1r1.image(Image.open('assets/profile-placeholder.jpg'))
            # else:
            #     c1r1.image(fig)

            c1r1.image(Image.open('assets/profile-placeholder.jpg'))

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

    # Query qualifying data and parsing
    quali = requests.request("GET", f'http://ergast.com/api/f1/drivers/{driver_id}/qualifying?limit=1000').text
    tree = ET.fromstring(quali)

    #Getting nationality
    nationality = tree[0][0].find('{http://ergast.com/mrd/1.5}QualifyingList').find('{http://ergast.com/mrd/1.5}QualifyingResult').find('{http://ergast.com/mrd/1.5}Driver').find('{http://ergast.com/mrd/1.5}Nationality').text

    #Initializing counter and dictionary
    poles = 0
    constructors = {}

    # Loop trought all the qualifying data
    for i in range(len(tree[0])):
        # Getting pole
        if (
            tree[0][i]
                .find('{http://ergast.com/mrd/1.5}QualifyingList')
                .find('{http://ergast.com/mrd/1.5}QualifyingResult')
                .attrib['position'] == '1'):
            poles+=1

        # Getting contructors
        constructor = tree[0][i].find('{http://ergast.com/mrd/1.5}QualifyingList').find('{http://ergast.com/mrd/1.5}QualifyingResult').find('{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Name').text
        constructors[constructor] = None

    # Getting the team of last qualifying
    last_team = tree[0][len(tree[0])-1].find('{http://ergast.com/mrd/1.5}QualifyingList').find('{http://ergast.com/mrd/1.5}QualifyingResult').find('{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Name').text

    #Getting status (checking the last qualifying year)
    status = tree[0][len(tree[0])-1].attrib['season'] == str(date.today().year)

    # Requesting data and parsing
    races_data = requests.request("GET", f'http://ergast.com/api/f1/drivers/{driver_id}/results?limit=1000').text
    tree = ET.fromstring(races_data)

    constructors = {}
    # Loop trought all the qualifying data
    for i in range(len(tree[0])):
        # Getting contructors
        constructor = tree[0][i].find('{http://ergast.com/mrd/1.5}ResultsList').find('{http://ergast.com/mrd/1.5}Result').find('{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Name').text
        constructors[constructor] = None

    races = len(tree[0])
    wins = 0
    podium = 0

    for i in range(races):
        position = int(tree[0][i].find('{http://ergast.com/mrd/1.5}ResultsList').find('{http://ergast.com/mrd/1.5}Result').attrib['position'])
        wins = (wins + 1) if position == 1 else wins
        podium = (podium + 1) if position <= 3 else podium

    # Requesting data and parsing
    champioship_data = requests.request("GET", f'https://ergast.com/api/f1/drivers/{driver_id}/driverStandings').text
    tree = ET.fromstring(champioship_data)

    results = []
    championships = 0
    for i in range(len(tree[0])):
        season = tree[0][i].attrib['season']
        position = tree[0][i].find('{http://ergast.com/mrd/1.5}DriverStanding').attrib['position'] 
        points = tree[0][i].find('{http://ergast.com/mrd/1.5}DriverStanding').attrib['points']
        vic = tree[0][i].find('{http://ergast.com/mrd/1.5}DriverStanding').attrib['wins']
        team = tree[0][i].find('{http://ergast.com/mrd/1.5}DriverStanding').find('{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Name').text
        emoji = '🥇' if position == '1' else '🥈' if position == '2' else '🥉' if position == '3' else ' '
        championships = championships+1 if position == '1' else championships
        results.append([season, position, vic, points, team, emoji])

    past_championships = pd.DataFrame(results, columns=['Season', 'Position', 'Wins', 'Points', 'Team', 'Medal'])

    # Appending results to the detail list
    driver_details = [
        nationality,
        poles,
        list(constructors.keys()),
        races,
        last_team,
        status,
        wins,
        podium,
        championships,
        past_championships
    ]

    return driver_details

def query_driver_actual_details(driver_id):
    # Query qualifying data and parsing
    actual = requests.request("GET", f'https://ergast.com/api/f1/current/drivers/{driver_id}/driverStandings').text
    tree = ET.fromstring(actual)

    position = tree[0][0][0].attrib['position']
    points = tree[0][0][0].attrib['points']
    wins = tree[0][0][0].attrib['wins']

    return [position, points, wins]

instance = f1()