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
        st.set_page_config(page_title='F1 - Data Viz',
                           layout="wide", page_icon='assets/favicon.png')

        self.navigation = ''
        self.pilot_name = ''
        self.all_drivers = ''
        self.all_circuits = ''
        self.driverid = ''
        self.driver_details = ''
        self.circuit_name = ''
        self.year = ''
        self.round = ''
        self.race_name = ''

        self.main_page()

    def main_page(self):
        self.side_bar()

        st.markdown(
            '''
            <style>
                .appview-container .main .block-container {padding-top: 1rem}
                .row_heading.level0 {display:none}
                .blank {display:none}
                .stDataFrame {border:0px}
                
            </style>
            ''', unsafe_allow_html=True)

        col1, col2 = st.columns([9, 2])

        with col1:
            st.title('F1 Data Visualization')
        with col2:
            st.markdown(' ')
            st.markdown(' ')
            st.image(Image.open('assets/f1-logo.png'))

        if self.navigation == 'Driver':
            self.driver_page()

        if self.navigation == 'Season':
            self.championship_page()

        if self.navigation == 'Circuit':
            self.circuit_page()

        if self.navigation == 'Race':
            self.race_page()

        if self.navigation == 'About':
            self.about_page()

    def side_bar(self):
        with st.sidebar:
            st.header('Navigate')

            self.navigation = st.radio(
                "Go to:",
                ("Circuit", "Season", "Driver", "Race", "About"),
                index=4
            )

            if self.navigation == 'Driver':
                # Cache
                self.all_drivers = query_all_drivers()

                # Search name
                st.subheader('Search driver')

                pilot_name_search = st.text_input('Write a driver name:', 'Lewis')

                response = query_driver(self.all_drivers, pilot_name_search)

                # Select pilot
                self.pilot_name = st.selectbox(
                    f"Drivers with a name similar to '{pilot_name_search}':",
                    tuple(response))

            if self.navigation == 'Circuit':
                # Cache
                self.all_circuits = query_all_circuits()

                # Search name
                st.subheader('Search a circuit')

                countries = list(
                    self.all_circuits['Country'].unique().astype(str))
                countries.sort()

                # Search name
                country = st.selectbox(f'Select a circuit country', countries)

                circuits = list(
                    self.all_circuits[self.all_circuits['Country'] == country]['Name'])

                self.circuit_name = st.selectbox(f'Select a circuit', circuits)

            if self.navigation == 'Race':
                st.subheader('Search a race')

                self.year = st.selectbox(
                    f'Select a season:', range(2022, 1949, -1))

                races = query_all_races(self.year)

                self.race_name = st.selectbox(f'Select a circuit:', races)

                self.round = races.index(self.race_name) + 1

            if self.navigation == 'Season':
                
                st.subheader('Select a Season')

                self.year = st.selectbox(
                    f'By year:', range(2022, 1949, -1))

            if self.navigation == 'About':
                st.header('Developed by:')
                
                col2, col1 = st.columns([5,2])
                with col2:
                    st.image(Image.open('assets/profile.jpeg'))
                    st.subheader('André de Souza Reis')

                    st.markdown('### Reach me on [LinkedIn](https://www.linkedin.com/in/andre-de-souza-reis/).')
                    st.markdown('### Take a look on my [GitHub](https://github.com/andre-souza-reis).')
                    st.markdown('### Check my [Porfolio](https://andre-souza-reis.github.io/).')

    def circuit_page(self):

        circuit_details = query_circuit_details(
            self.circuit_name, self.all_circuits)

        st.header(f'Circuit - {self.circuit_name}')

        st.subheader('Map of region')

        lat = float(self.all_circuits[self.all_circuits['Name']
                    == self.circuit_name]['Geo'].values[0]['lat'])
        long = float(self.all_circuits[self.all_circuits['Name']
                     == self.circuit_name]['Geo'].values[0]['long'])

        df = pd.DataFrame([[lat, long]], columns=['lat', 'lon'])
        st.map(df, zoom=14, use_container_width=True)

        st.subheader(f'Last Race Results ({circuit_details[1]})')

        st.write(circuit_details[2])

        st.subheader('Past Winners')

        st.write(circuit_details[0])

    def race_page(self):
        st.header(f'{self.race_name} - {self.year}')

        race_details = query_race_details(self.year, self.round)

        if race_details[2] == '':
            st.text("This race has not yet been held!")
        else:
            st.subheader('Infos')
            col1, col2, col3 = st.columns(3)
            with col2:
                st.markdown(f'**Country**: {race_details[4]}')

            with col3:
                st.markdown(f'**Location**: {race_details[3]}')

            with col1:
                st.markdown(f'**Circuit Name**: {race_details[1]}')

            st.subheader('Race Results')

            st.write(race_details[0])

            st.subheader('Map of circuit region')

            df = pd.DataFrame([[race_details[2]['lat'], race_details[2]['long']]], columns=[
                              'lat', 'lon']).astype(float)
            st.map(df, zoom=14, use_container_width=True)

    def championship_page(self):
        st.header(f'Season - {self.year}')
        [driver, constructor] = query_season_details(self.year)

        st.subheader('Driver Championship')

        st.write(driver)

        st.subheader('Constructor Championship')

        st.write(constructor)

    def driver_page(self):

        drivers = self.all_drivers[self.all_drivers['Name']
                                  == self.pilot_name]['driverId'].values
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

            status = 'Active' if driver_details[5] == True else 'Retired'

            c3r1.markdown(f'**Races:** {driver_details[3]}')
            c3r1.markdown(f'**Podiums:** {driver_details[7]}')
            c3r1.markdown(f'**Status:** {status}')
            teams = driver_details[2]

            if len(teams) > 1:
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
            #     wiki_url = self.all_drivers[self.all_drivers['Name'] == self.pilot_name]['url'].values[0]
            #     fig = query_driver_photo(wiki_url)
            # except:
            #     c1r1.image(Image.open('assets/profile-placeholder.jpg'))
            # else:
            #     c1r1.image(fig)

            c1r1.image(Image.open('assets/profile-placeholder.jpg'))

    def about_page(self):
        st.header('About')
        st.markdown('This is a portfolio project that aims to bring Formula 1 data in a visual and enjoyable way to F1 fans.')
        st.markdown('The application is divided on 5 pages, which can be reached through the side menu:')
        st.markdown(
            '''
                * **Circuit:** On this page, the user can search a specific circuit, selecting its country and name in the side menu. Then it will be possible to see the map of the region, the last race results, and all the F1 past winners of the selected circuit. 
                * **Season:** On this page, the user can select a year in the side menu and get information about the driver and constructor championship of that year, such as points, wins, positions, etc.
                * **Driver:** On this page, the user can write a driver name in the side menu and select a driver in the drop-down box. Then, it will be possible to get a lot of information about the selected driver, such as nationality, number of races, number of wins, data regarding the actual world championship (if the driver is a current F1 driver), etc.
                * **Race:** On this page, the user can select a year and a circuit to get information about a specific race, such as the final positions, drivers names and drivers teams. 
                * **About:** On this page, which is this one that you are reading, the user can find more information about the project and the application developer.
            '''
        )
        st.subheader('Development')
        st.markdown('This project was all developed in Python, using the [Streamlit](https://streamlit.io/) library to the frontend, the backend was developed mainly using [Pandas](https://pandas.pydata.org/) to treat the data, and last but not least, all the data shown on this project is requested from the [Ergast Developer API](https://ergast.com/mrd/).')

        col1, spc1, col2, spc2, col3 = st.columns([2,1,2,1,2])

        with col1:
            st.image(Image.open('assets/streamlit-logo.png'))

        with col2:
            st.image(Image.open('assets/pandas-logo-300.png'))

        with col3:
            st.image(Image.open('assets/ergast.png'))

def query_all_drivers():
    data = requests.request(
        "GET", 'http://ergast.com/api/f1/drivers?limit=10000').text
    drivers = pd.read_xml(
        data,
        namespaces={'doc': "http://ergast.com/mrd/1.5"},
        xpath='.//doc:Driver'
    )
    drivers = drivers.assign(Name=drivers[['GivenName', 'FamilyName']].apply(
        ' '.join, axis=1)).drop(['GivenName', 'FamilyName'], axis=1)

    return drivers


def query_all_circuits():
    data = requests.request(
        "GET", 'http://ergast.com/api/f1/circuits?limit=10000').text
    tree = ET.fromstring(data)

    circuits = []
    for i in range(len(tree[0])):
        circuitId = tree[0][i].attrib['circuitId']
        circuit = tree[0][i].find(
            '{http://ergast.com/mrd/1.5}CircuitName').text
        geo = tree[0][i].find('{http://ergast.com/mrd/1.5}Location').attrib
        country = tree[0][i].find(
            '{http://ergast.com/mrd/1.5}Location').find('{http://ergast.com/mrd/1.5}Country').text
        circuits.append([circuitId, circuit, geo, country])

    return pd.DataFrame(circuits, columns=['ID', 'Name', 'Geo', 'Country'])


def query_driver(all_drivers, name):

    similar_drivers = process.extractBests(
        name, all_drivers['Name'].to_list(), limit=10, score_cutoff=80)
    similar_drivers_list = []
    for i in similar_drivers:
        similar_drivers_list.append(i[0])

    return similar_drivers_list


def query_driver_photo(url):
    text = requests.request("GET", url).text

    sample = "//upload.wikimedia.org/wikipedia/commons/thumb"

    start = text.find(sample)
    end = text[start:].find('"')

    response = requests.get('https:' + text[start:(start + end)])

    return Image.open(BytesIO(response.content))


def query_driver_detail(driver_id):

    # Query qualifying data and parsing
    quali = requests.request(
        "GET", f'http://ergast.com/api/f1/drivers/{driver_id}/qualifying?limit=1000').text
    tree = ET.fromstring(quali)

    # Getting nationality
    nationality = tree[0][0].find('{http://ergast.com/mrd/1.5}QualifyingList').find('{http://ergast.com/mrd/1.5}QualifyingResult').find(
        '{http://ergast.com/mrd/1.5}Driver').find('{http://ergast.com/mrd/1.5}Nationality').text

    # Initializing counter and dictionary
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
            poles += 1

        # Getting contructors
        constructor = tree[0][i].find('{http://ergast.com/mrd/1.5}QualifyingList').find('{http://ergast.com/mrd/1.5}QualifyingResult').find(
            '{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Name').text
        constructors[constructor] = None

    # Getting the team of last qualifying
    last_team = tree[0][len(tree[0])-1].find('{http://ergast.com/mrd/1.5}QualifyingList').find(
        '{http://ergast.com/mrd/1.5}QualifyingResult').find('{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Name').text

    # Getting status (checking the last qualifying year)
    status = tree[0][len(tree[0])-1].attrib['season'] == str(date.today().year)

    # Requesting data and parsing
    races_data = requests.request(
        "GET", f'http://ergast.com/api/f1/drivers/{driver_id}/results?limit=1000').text
    tree = ET.fromstring(races_data)

    constructors = {}
    # Loop trought all the qualifying data
    for i in range(len(tree[0])):
        # Getting contructors
        constructor = tree[0][i].find('{http://ergast.com/mrd/1.5}ResultsList').find('{http://ergast.com/mrd/1.5}Result').find(
            '{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Name').text
        constructors[constructor] = None

    races = len(tree[0])
    wins = 0
    podium = 0

    for i in range(races):
        position = int(tree[0][i].find('{http://ergast.com/mrd/1.5}ResultsList').find(
            '{http://ergast.com/mrd/1.5}Result').attrib['position'])
        wins = (wins + 1) if position == 1 else wins
        podium = (podium + 1) if position <= 3 else podium

    # Requesting data and parsing
    champioship_data = requests.request(
        "GET", f'https://ergast.com/api/f1/drivers/{driver_id}/driverStandings').text
    tree = ET.fromstring(champioship_data)

    results = []
    championships = 0
    for i in range(len(tree[0])):
        season = tree[0][i].attrib['season']
        position = tree[0][i].find(
            '{http://ergast.com/mrd/1.5}DriverStanding').attrib['position']
        points = tree[0][i].find(
            '{http://ergast.com/mrd/1.5}DriverStanding').attrib['points']
        vic = tree[0][i].find(
            '{http://ergast.com/mrd/1.5}DriverStanding').attrib['wins']
        team = tree[0][i].find('{http://ergast.com/mrd/1.5}DriverStanding').find(
            '{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Name').text
        emoji = '🥇' if position == '1' else '🥈' if position == '2' else '🥉' if position == '3' else ' '
        championships = championships+1 if position == '1' else championships
        results.append([season, position, vic, points, team, emoji])

    past_championships = pd.DataFrame(
        results, columns=['Season', 'Position', 'Wins', 'Points', 'Team', 'Medal'])

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
    actual = requests.request(
        "GET", f'https://ergast.com/api/f1/current/drivers/{driver_id}/driverStandings').text
    tree = ET.fromstring(actual)

    position = tree[0][0][0].attrib['position']
    points = tree[0][0][0].attrib['points']
    wins = tree[0][0][0].attrib['wins']

    return [position, points, wins]


def query_circuit_details(circuit_name, all_circuits):
    circuit_id = all_circuits[all_circuits['Name']
                              == circuit_name]['ID'].values[0]

    data = requests.request(
        "GET", f'http://ergast.com/api/f1/circuits/{circuit_id}/results/1?limit=1000').text
    tree = ET.fromstring(data)

    details = []
    for i in range(len(tree[0])):
        season = int(tree[0][i].attrib['season'])
        race = tree[0][i].find('{http://ergast.com/mrd/1.5}RaceName').text
        name = tree[0][i].find('{http://ergast.com/mrd/1.5}ResultsList').find('{http://ergast.com/mrd/1.5}Result').find(
            '{http://ergast.com/mrd/1.5}Driver').find('{http://ergast.com/mrd/1.5}GivenName').text
        last_name = tree[0][i].find('{http://ergast.com/mrd/1.5}ResultsList').find('{http://ergast.com/mrd/1.5}Result').find(
            '{http://ergast.com/mrd/1.5}Driver').find('{http://ergast.com/mrd/1.5}FamilyName').text
        constructor = tree[0][i].find('{http://ergast.com/mrd/1.5}ResultsList').find('{http://ergast.com/mrd/1.5}Result').find(
            '{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Name').text
        details.append([season, race, (name + ' ' + last_name), constructor])

    hist = pd.DataFrame(
        details, columns=['Season', 'Race Name', 'Driver', 'Constructor'])

    last_year = hist.iloc[[-1]]['Season'].values[0]

    data = requests.request("GET", f'http://ergast.com/api/f1/{last_year}/circuits/{circuit_id}/results?limit=1000').text
    tree = ET.fromstring(data)

    details = []
    for i in tree[0][0].find('{http://ergast.com/mrd/1.5}ResultsList').findall('{http://ergast.com/mrd/1.5}Result'):
        position = int(i.attrib['position'])
        number = int(i.attrib['number'])
        name = i.find(
            '{http://ergast.com/mrd/1.5}Driver').find('{http://ergast.com/mrd/1.5}GivenName').text
        last_name = i.find(
            '{http://ergast.com/mrd/1.5}Driver').find('{http://ergast.com/mrd/1.5}FamilyName').text
        constructor = i.find(
            '{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Name').text
        emoji = '🥇' if position == 1 else '🥈' if position == 2 else '🥉' if position == 3 else ' '
        details.append(
            [position, number, (name + ' ' + last_name), constructor, emoji])

    last_year_details = pd.DataFrame(
        details, columns=['Position', 'Number', 'Driver', 'Constructor', 'Medal'])

    return [hist, last_year, last_year_details]


def query_all_races(year):
    data = requests.request("GET", f'http://ergast.com/api/f1/{year}').text
    tree = ET.fromstring(data)

    races = []
    for i in tree[0].findall('{http://ergast.com/mrd/1.5}Race'):
        races.append(i.find('{http://ergast.com/mrd/1.5}RaceName').text)

    return races


def query_race_details(year, round):
    data = requests.request(
        "GET", f'http://ergast.com/api/f1/{year}/{round}/results?limit=1000').text
    tree = ET.fromstring(data)

    details = []
    try:
        for i in tree[0][0].find('{http://ergast.com/mrd/1.5}ResultsList').findall('{http://ergast.com/mrd/1.5}Result'):
            position = i.attrib['position']
            number = i.attrib['number']
            name = i.find(
                '{http://ergast.com/mrd/1.5}Driver').find('{http://ergast.com/mrd/1.5}GivenName').text
            last_name = i.find(
                '{http://ergast.com/mrd/1.5}Driver').find('{http://ergast.com/mrd/1.5}FamilyName').text
            constructor = i.find(
                '{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Name').text
            emoji = '🥇' if position == '1' else '🥈' if position == '2' else '🥉' if position == '3' else ' '

            details.append(
                [position, number, (name + ' ' + last_name), constructor, emoji])
        circuit_name = tree[0].find('{http://ergast.com/mrd/1.5}Race').find(
            '{http://ergast.com/mrd/1.5}Circuit').find('{http://ergast.com/mrd/1.5}CircuitName').text
        geo = tree[0].find('{http://ergast.com/mrd/1.5}Race').find(
            '{http://ergast.com/mrd/1.5}Circuit').find('{http://ergast.com/mrd/1.5}Location').attrib
        loc = tree[0].find('{http://ergast.com/mrd/1.5}Race').find('{http://ergast.com/mrd/1.5}Circuit').find(
            '{http://ergast.com/mrd/1.5}Location').find('{http://ergast.com/mrd/1.5}Locality').text
        country = tree[0].find('{http://ergast.com/mrd/1.5}Race').find('{http://ergast.com/mrd/1.5}Circuit').find(
            '{http://ergast.com/mrd/1.5}Location').find('{http://ergast.com/mrd/1.5}Country').text

    except:
        circuit_name = ''
        geo = ''
        loc = ''
        country = ''

    race_details = pd.DataFrame(
        details, columns=['Position', 'Number', 'Driver', 'Constructor', 'Medal'])

    return [race_details, circuit_name, geo, loc, country]


def query_season_details(year):
    driver = requests.request("GET",f'http://ergast.com/api/f1/{year}/driverStandings').text
    driver_data = ET.fromstring(driver)

    constructor = requests.request("GET",f'http://ergast.com/api/f1/{year}/constructorStandings').text
    constructor_data = ET.fromstring(constructor)

    driver_season = []
    for i in driver_data[0].find('{http://ergast.com/mrd/1.5}StandingsList').findall('{http://ergast.com/mrd/1.5}DriverStanding'):
        position = int(i.attrib['position'])
        wins = int(i.attrib['wins'])
        points = i.attrib['points']
        name = i.find('{http://ergast.com/mrd/1.5}Driver').find('{http://ergast.com/mrd/1.5}GivenName').text
        last_name = i.find('{http://ergast.com/mrd/1.5}Driver').find('{http://ergast.com/mrd/1.5}FamilyName').text
        nationality = i.find('{http://ergast.com/mrd/1.5}Driver').find('{http://ergast.com/mrd/1.5}Nationality').text
        constructor = i.find('{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Name').text
        medal = '🥇' if position == 1 else '🥈' if position == 2 else '🥉' if position == 3 else ' '
        driver_season.append([position, wins, points, f'{name} {last_name}', nationality, constructor, medal])

    driver_dataframe = pd.DataFrame(driver_season, columns=['Position', 'Wins', 'Points', 'Driver', 'Driver Nationality', 'Constructor', 'Medal'])

    constructor_season = []
    for i in constructor_data[0].find('{http://ergast.com/mrd/1.5}StandingsList').findall('{http://ergast.com/mrd/1.5}ConstructorStanding'):
        position = int(i.attrib['position'])
        wins = int(i.attrib['wins'])
        points = i.attrib['points']
        name = i.find('{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Name').text
        nationality = i.find('{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Nationality').text
        medal = '🥇' if position == 1 else '🥈' if position == 2 else '🥉' if position == 3 else ' '
        constructor_season.append([position, wins, points, name, nationality, medal])

    constructor_dataframe = pd.DataFrame(constructor_season, columns=['Position', 'Wins', 'Points', 'Constructor', 'Nationality', 'Medal'])


    return [driver_dataframe, constructor_dataframe]

instance = f1()
