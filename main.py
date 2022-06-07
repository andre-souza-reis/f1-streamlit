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
        # Setting page title, wide layout and page icon
        st.set_page_config(page_title='F1 - Data Viz',
                           layout="wide", page_icon='assets/favicon.png')

        # Initializing attributes
        self.navigation = ''
        self.driver_name = ''
        self.all_drivers = ''
        self.all_circuits = ''
        self.driverid = ''
        self.driver_details = ''
        self.circuit_name = ''
        self.year = ''
        self.round = ''
        self.race_name = ''

        # Render main page
        self.main_page()

# Pages and side menu

    def main_page(self):
        # Render side menu
        self.side_bar()

        # Getting rid of index collumn in dataframes and empty space on top of main page
        st.markdown(
            '''
            <style>
                .appview-container .main .block-container {padding-top: 1rem}
                .row_heading.level0 {display:none}
                .blank {display:none}
                .stDataFrame {border:0px}
                
            </style>
            ''', unsafe_allow_html=True)

        # Positioning Title and F1 Logo
        col1, col2 = st.columns([9, 2])

        with col1:
            st.title('F1 Data Visualization')
        with col2:
            st.markdown(' ')
            st.markdown(' ')
            st.image(Image.open('assets/f1-logo.png'))

        # Calling the right page, deppending on the side menu selection
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
            # Title of navigation
            st.header('Navigate')

            # Radio buttons to navigate
            self.navigation = st.radio(
                "Go to:",
                ("Circuit", "Season", "Driver", "Race", "About"),
                index=4
            )

            # Defining the side menu deppending on the page selected

            if self.navigation == 'Driver':
                # If not done yet, requesting all drivers names
                if self.all_drivers == '':
                    self.all_drivers = query_all_drivers()

                # Search driver title
                st.subheader('Search driver')

                # Text input to search drivers names
                pilot_name_search = st.text_input(
                    'Write a driver name:', 'Lewis')

                # Looking for drivers names simmilar to the input name
                response = query_driver(self.all_drivers, pilot_name_search)

                # Select driver
                self.driver_name = st.selectbox(
                    f"Drivers with a name similar to '{pilot_name_search}':",
                    tuple(response))

            if self.navigation == 'Circuit':
                # If not done yet, requesting all circuit names
                if self.all_circuits == '':
                    self.all_circuits = query_all_circuits()

                # Search title
                st.subheader('Search a circuit')

                #Querying all the circuit countries
                countries = list(
                    self.all_circuits['Country'].unique().astype(str))
                countries.sort()

                # Selected country
                country = st.selectbox(f'Select a circuit country', countries)

                #Querying all circuits of selected country
                circuits = list(
                    self.all_circuits[self.all_circuits['Country'] == country]['Name'])

                # Selected circuit
                self.circuit_name = st.selectbox(f'Select a circuit', circuits)

            if self.navigation == 'Race':
                # Title
                st.subheader('Search a race')

                # Select box of possible years
                self.year = st.selectbox(
                    f'Select a season:', range(2022, 1949, -1))
                
                # Querying all races of selected year
                races = query_all_races(self.year)

                # Select box with all circuits of selected year
                self.race_name = st.selectbox(f'Select a circuit:', races)

                # Getting round of selected year
                self.round = races.index(self.race_name) + 1

            if self.navigation == 'Season':
                # Title
                st.subheader('Select a Season')

                # Select box of possible years
                self.year = st.selectbox(
                    f'By year:', range(2022, 1949, -1))

            if self.navigation == 'About':
                # Title
                st.header('Developed by:')

                # Positioning elements
                col2, col1 = st.columns([5, 2])
                with col2:
                    # Developer picture
                    st.image(Image.open('assets/profile.jpeg'))

                    # Developer name
                    st.subheader('André de Souza Reis')

                    # Developer infos
                    st.markdown(
                        '### Reach me on [LinkedIn](https://www.linkedin.com/in/andre-de-souza-reis/).')
                    st.markdown(
                        '### Take a look on my [GitHub](https://github.com/andre-souza-reis).')
                    st.markdown(
                        '### Check my [Porfolio](https://andre-souza-reis.github.io/).')

    def circuit_page(self):

        # Querying circuit details
        circuit_details = query_circuit_details(
            self.circuit_name, self.all_circuits)

        # Title with the circuit name
        st.header(f'Circuit - {self.circuit_name}')

        # Title
        st.subheader('Map of the region')

        # Getting latitude and longitude of circuit
        lat = float(self.all_circuits[self.all_circuits['Name']
                    == self.circuit_name]['Geo'].values[0]['lat'])
        long = float(self.all_circuits[self.all_circuits['Name']
                     == self.circuit_name]['Geo'].values[0]['long'])

        # Making a dataframe with latitude and longitude
        df = pd.DataFrame([[lat, long]], columns=['lat', 'lon'])

        #Plotting the region of the circuit map 
        st.map(df, zoom=14, use_container_width=True)

        # Title
        st.subheader(f'Last Race Results ({circuit_details[1]})')

        # Dataframe with last race results
        st.write(circuit_details[2])

        # Title
        st.subheader('Past Winners')

        # Dataframe with past winners
        st.write(circuit_details[0])

    def race_page(self):
        # Title
        st.header(f'{self.race_name} - {self.year}')

        # Querying race details
        race_details = query_race_details(self.year, self.round)

        # Checking if the user selected the current year and a race that not happend yet
        if race_details[2] == '':
            st.text("This race has not yet been held!")
        # If race already happend:
        else:
            # Title
            st.subheader('Infos')

            # Positioning elements
            col1, col2, col3 = st.columns(3)

            # Showing Country, Location and Circuit Name
            with col2:
                st.markdown(f'**Country**: {race_details[4]}')

            with col3:
                st.markdown(f'**Location**: {race_details[3]}')

            with col1:
                st.markdown(f'**Circuit Name**: {race_details[1]}')

            # Title
            st.subheader('Race Results')

            # Dataframe with race results
            st.write(race_details[0])

            # Title
            st.subheader('Map of the circuit region')

            # Building dataframe with circuit latitude and longitude
            df = pd.DataFrame([[race_details[2]['lat'], race_details[2]['long']]], columns=[
                              'lat', 'lon']).astype(float)
            
            # Showing map with the circuit region
            st.map(df, zoom=14, use_container_width=True)

    def championship_page(self):
        # Title with year selected
        st.header(f'Season - {self.year}')

        # Querying driver and constructor championship details 
        [driver, constructor] = query_season_details(self.year)

        # Title
        st.subheader('Driver Championship')

        # Dataframe with driver championship data
        st.write(driver)

        # Title
        st.subheader('Constructor Championship')

        # Dataframe with constructor championship data
        st.write(constructor)

    def driver_page(self):

        # Getting driver ID of driver selected in side menu
        drivers = self.all_drivers[self.all_drivers['Name']
                                   == self.driver_name]['driverId'].values

        # If the driver exists:                                   
        if len(drivers) > 0:
            driverid = drivers[0]

            # Querying driver details throught the driver ID
            driver_details = query_driver_detail(driverid)

            # Title
            st.header(self.driver_name)

            # Positioning elements in three columns
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

            # Processing teams array to string
            if len(teams) > 1:
                teams_f = ''
                for i in teams[:-1]:
                    teams_f += i + ', '
                teams_f += teams[-1]
                c3r1.markdown(f'**Team:** {teams_f}')
            else:
                c3r1.markdown(f'**Team:** {teams[0]}')

            # If driver is not retired of F1
            if(status == 'Active'):

                # Title
                st.subheader('Actual World Championship Results')

                # Querying details of current championship
                data = query_driver_actual_details(driverid)

                # Positioning current championship elements in three columns
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

            # Title
            st.subheader('Past World Championship Results')
            
            # Dataframe with past world championship results
            st.write(driver_details[9])

            # Getting driver picture from wikipedia (future feature)

            # try:
            #     wiki_url = self.all_drivers[self.all_drivers['Name'] == self.driver_name]['url'].values[0]
            #     fig = query_driver_photo(wiki_url)
            # except:
            #     c1r1.image(Image.open('assets/profile-placeholder.jpg'))
            # else:
            #     c1r1.image(fig)

            # Showing generic driver picture
            c1r1.image(Image.open('assets/profile-placeholder.jpg'))

    def about_page(self):
        # Title
        st.header('About')
        
        # About text
        st.markdown(
            'This is a portfolio project that aims to bring Formula 1 data in a visual and enjoyable way to F1 fans.')
        st.markdown(
            'The application is divided on 5 pages, which can be reached through the side menu:')
        st.markdown(
            '''
                * **Circuit:** On this page, the user can search a specific circuit, selecting its country and name in the side menu. Then it will be possible to see the map of the region, the last race results, and all the F1 past winners of the selected circuit. 
                * **Season:** On this page, the user can select a year in the side menu and get information about the driver and constructor championship of that year, such as points, wins, positions, etc.
                * **Driver:** On this page, the user can write a driver name in the side menu and select a driver in the drop-down box. Then, it will be possible to get a lot of information about the selected driver, such as nationality, number of races, number of wins, data regarding the actual world championship (if the driver is a current F1 driver), etc.
                * **Race:** On this page, the user can select a year and a circuit to get information about a specific race, such as the final positions, drivers names and drivers teams. 
                * **About:** On this page, which is this one that you are reading, the user can find more information about the project and the application developer.
            '''
        )

        # Title
        st.subheader('Development')

        # Development text
        st.markdown(
            'This project was all developed in Python, using the [Streamlit](https://streamlit.io/) library to the frontend, the backend was developed mainly using [Pandas](https://pandas.pydata.org/) to treat the data, and last but not least, all the data shown on this project is requested from the [Ergast Developer API](https://ergast.com/mrd/).')

        # Positioning logos in three columns with two spacers columns
        col1, spc1, col2, spc2, col3 = st.columns([2, 1, 2, 1, 2])

        with col1:
            st.image(Image.open('assets/streamlit-logo.png'))

        with col2:
            st.image(Image.open('assets/pandas-logo-300.png'))

        with col3:
            st.image(Image.open('assets/ergast.png'))

# Query functions

def query_all_drivers():
    '''    
    Process:
    * Getting a Dataframe with details of all drivers in the database

    Return:
    drivers:pd.Dataframe
    '''

    # Requesting all drivers details
    data = requests.request(
        "GET", 'http://ergast.com/api/f1/drivers?limit=10000').text

    # Building a pd.Dataframe from the xml
    drivers = pd.read_xml(
        data,
        namespaces={'doc': "http://ergast.com/mrd/1.5"},
        xpath='.//doc:Driver'
    )

    # Merging GivenName and FamilyName Columns
    drivers = drivers.assign(Name=drivers[['GivenName', 'FamilyName']].apply(
        ' '.join, axis=1)).drop(['GivenName', 'FamilyName'], axis=1)

    return drivers


def query_all_circuits():
    '''    
    Process:
    * Getting a Dataframe with details of all circuits in the database

    Return:
    pd.Dataframe
    '''

    # Requesting all circuit names
    data = requests.request(
        "GET", 'http://ergast.com/api/f1/circuits?limit=10000').text
    
    # Building tree
    tree = ET.fromstring(data)

    # Building array with circuit ID, Circuit name, dictionary with circuit latitude and longitude, 
    # circuit country (columns) for each cirucuit in the database (rows)
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
    '''
    Input:
    all_drivers:pd.dataframe - All the drivers in the database
    name:string
    
    Process:
    * Getting an array with similar driver names in the dataframe to the specified name

    Return:
    similar_drivers_list:Array
    '''
    # Getting a list of similar driver names in the dataframe to the specified name
    similar_drivers = process.extractBests(
        name, all_drivers['Name'].to_list(), limit=10, score_cutoff=80)
    
    # Building an array with the simmilar names
    similar_drivers_list = []
    for i in similar_drivers:
        similar_drivers_list.append(i[0])

    return similar_drivers_list


def query_driver_photo(url):
    '''
    Input:
    url:string
    
    Process:
    * Getting main picture url of the specified wikipedia page
    * Requesting picture

    Return:
    pil.Image
    '''
    # Requesting wikipedia page
    text = requests.request("GET", url).text

    # Lookign for this string on the page
    sample = "//upload.wikimedia.org/wikipedia/commons/thumb"

    start = text.find(sample)
    end = text[start:].find('"')

    # Requesting main picture of the wikipedia page
    response = requests.get('https:' + text[start:(start + end)])

    return Image.open(BytesIO(response.content))


def query_driver_detail(driver_id):

    # Query qualifying data
    quali = requests.request(
        "GET", f'http://ergast.com/api/f1/drivers/{driver_id}/qualifying?limit=1000').text
    
    # Building tree
    tree = ET.fromstring(quali)

    # Getting nationality
    nationality = tree[0][0].find('{http://ergast.com/mrd/1.5}QualifyingList').find('{http://ergast.com/mrd/1.5}QualifyingResult').find(
        '{http://ergast.com/mrd/1.5}Driver').find('{http://ergast.com/mrd/1.5}Nationality').text

    # Initializing counter and dictionary
    poles = 0
    constructors = {}

    # Loop throught all the qualifying data
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
    '''
    Input:
    driver_id:string
    
    Process:
    * Getting driver position, points and wins on the current championship

    Return:
    [position:string, points:string, wins:string]:Array
    '''
    # Query driver standing on current championship
    actual = requests.request(
        "GET", f'https://ergast.com/api/f1/current/drivers/{driver_id}/driverStandings').text
    
    # Building tree
    tree = ET.fromstring(actual)

    # Getting data from the tree
    position = tree[0][0][0].attrib['position']
    points = tree[0][0][0].attrib['points']
    wins = tree[0][0][0].attrib['wins']

    return [position, points, wins]


def query_circuit_details(circuit_name, all_circuits):
    '''
    Input:
    circuit_name:string
    all_circuits:pd.Dataframe - Dataframe with all circuits in the database
    
    Process:
    * Getting the circuit ID throught the name input and the all_circuits dataframe
    * Requsting all season winners of the specified circuit
    * Requesting last year race results of the specified circuit 
    * hist - Dataframe with all season winners
    * last_year - Year of the circuit last year
    * last_year_details - Dataframe with last year race results

    Return:
    [hist:pd.Dataframe, last_year:string, last_year_details:pd.Dataframe]:Array
    '''
    # Getting circuit ID from all_circuits dataframe
    circuit_id = all_circuits[all_circuits['Name']
                              == circuit_name]['ID'].values[0]

    # Requestind circuit data
    data = requests.request(
        "GET", f'http://ergast.com/api/f1/circuits/{circuit_id}/results/1?limit=1000').text

    # Building tree
    tree = ET.fromstring(data)

    # Building array with season, race name, winner name, winner constructor (columns) of each year (rows)
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

    # Building Dataframe from array
    hist = pd.DataFrame(
        details, columns=['Season', 'Race Name', 'Driver', 'Constructor'])

    # Getting last race year of the specified circuit
    last_year = hist.iloc[[-1]]['Season'].values[0]

    # Requesting the last year race results of the specified circuit 
    data = requests.request(
        "GET", f'http://ergast.com/api/f1/{last_year}/circuits/{circuit_id}/results?limit=1000').text

    # Building tree
    tree = ET.fromstring(data)

    # Building array with position, number, name and last name, constructor and emoji medal (columns)
    # of each driver (rowns)
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

    # Building dataframe from array
    last_year_details = pd.DataFrame(
        details, columns=['Position', 'Number', 'Driver', 'Constructor', 'Medal'])

    return [hist, last_year, last_year_details]


def query_all_races(year):
    '''
    Input:
    year:int - Season year
    
    Process:
    * Request all races of the specified year
    * Returning an array with all races names of the specified year

    Return:
    races:Array
    '''

    # Requesting races names
    data = requests.request("GET", f'http://ergast.com/api/f1/{year}').text
    
    # Building tree
    tree = ET.fromstring(data)

    # Building array with all races names
    races = []
    for i in tree[0].findall('{http://ergast.com/mrd/1.5}Race'):
        races.append(i.find('{http://ergast.com/mrd/1.5}RaceName').text)

    return races


def query_race_details(year, round):
    '''
    Input:
    year:int - Season year
    round:int - Race round
    
    Process:
    * Request the race results of the specified year and round
    * If the race not happend yet, returning empty dataframe and empty strings 
    * geo is a dictionary with circuit latitute and longitude 
    * loc is a string with the circuit region name

    Return:
    [race_details:pd.Dataframe, circuit_name:String, geo:String, loc:String, country:String]:Array
    '''
    # Requesting race results
    data = requests.request(
        "GET", f'http://ergast.com/api/f1/{year}/{round}/results?limit=1000').text

    # Building a tree
    tree = ET.fromstring(data)

    # Building an array with position, number, driver name and last name, constructor and medal emoji
    # (columns) for each driver (rows)
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
        
        # Getting circuit name
        circuit_name = tree[0].find('{http://ergast.com/mrd/1.5}Race').find(
            '{http://ergast.com/mrd/1.5}Circuit').find('{http://ergast.com/mrd/1.5}CircuitName').text
        
        # Getting circuit latitude and longitude
        geo = tree[0].find('{http://ergast.com/mrd/1.5}Race').find(
            '{http://ergast.com/mrd/1.5}Circuit').find('{http://ergast.com/mrd/1.5}Location').attrib
        
        # Getting circuit region name
        loc = tree[0].find('{http://ergast.com/mrd/1.5}Race').find('{http://ergast.com/mrd/1.5}Circuit').find(
            '{http://ergast.com/mrd/1.5}Location').find('{http://ergast.com/mrd/1.5}Locality').text
        
        # Getting circuit country
        country = tree[0].find('{http://ergast.com/mrd/1.5}Race').find('{http://ergast.com/mrd/1.5}Circuit').find(
            '{http://ergast.com/mrd/1.5}Location').find('{http://ergast.com/mrd/1.5}Country').text

    # If the race hasn't happend yet
    except:
        circuit_name = ''
        geo = ''
        loc = ''
        country = ''

    # Building a Dataframe from the array
    race_details = pd.DataFrame(
        details, columns=['Position', 'Number', 'Driver', 'Constructor', 'Medal'])

    return [race_details, circuit_name, geo, loc, country]


def query_season_details(year):
    '''
    Input:
    year:int - Season year
    
    Process:
    * Request final driver and constructor standing for the specified year's season 

    Return:
    [driver_dataframe:pd.Dataframe, constructor_dataframe:pd.Dataframe]:Array
    '''

    # Requesting driver standings
    driver = requests.request(
        "GET", f'http://ergast.com/api/f1/{year}/driverStandings').text

    # Getting driver standing tree
    driver_data = ET.fromstring(driver)

    # Requestig constructor standings
    constructor = requests.request(
        "GET", f'http://ergast.com/api/f1/{year}/constructorStandings').text

    # Getting constructor tree
    constructor_data = ET.fromstring(constructor)

    # Constructing an array with position, wins, points, driver name and last name,
    # constructor and emoji medal (columns), of each driver (rows).
    driver_season = []
    for i in driver_data[0].find('{http://ergast.com/mrd/1.5}StandingsList').findall('{http://ergast.com/mrd/1.5}DriverStanding'):
        position = int(i.attrib['position'])
        wins = int(i.attrib['wins'])
        points = i.attrib['points']
        name = i.find(
            '{http://ergast.com/mrd/1.5}Driver').find('{http://ergast.com/mrd/1.5}GivenName').text
        last_name = i.find(
            '{http://ergast.com/mrd/1.5}Driver').find('{http://ergast.com/mrd/1.5}FamilyName').text
        nationality = i.find(
            '{http://ergast.com/mrd/1.5}Driver').find('{http://ergast.com/mrd/1.5}Nationality').text
        constructor = i.find(
            '{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Name').text
        medal = '🥇' if position == 1 else '🥈' if position == 2 else '🥉' if position == 3 else ' '
        driver_season.append(
            [position, wins, points, f'{name} {last_name}', nationality, constructor, medal])

    # Constructing a pd.Dataframe from the previous array
    driver_dataframe = pd.DataFrame(driver_season, columns=[
                                    'Position', 'Wins', 'Points', 'Driver', 'Driver Nationality', 'Constructor', 'Medal'])

    # Constructing an array with position, wins, points, constructor name and nationality,
    # and emoji medal (columns), of each constructor (rows).
    constructor_season = []
    for i in constructor_data[0].find('{http://ergast.com/mrd/1.5}StandingsList').findall('{http://ergast.com/mrd/1.5}ConstructorStanding'):
        position = int(i.attrib['position'])
        wins = int(i.attrib['wins'])
        points = i.attrib['points']
        name = i.find(
            '{http://ergast.com/mrd/1.5}Constructor').find('{http://ergast.com/mrd/1.5}Name').text
        nationality = i.find('{http://ergast.com/mrd/1.5}Constructor').find(
            '{http://ergast.com/mrd/1.5}Nationality').text
        medal = '🥇' if position == 1 else '🥈' if position == 2 else '🥉' if position == 3 else ' '
        constructor_season.append(
            [position, wins, points, name, nationality, medal])

    # Constructing a pd.Dataframe from the previous array
    constructor_dataframe = pd.DataFrame(constructor_season, columns=[
                                         'Position', 'Wins', 'Points', 'Constructor', 'Nationality', 'Medal'])

    return [driver_dataframe, constructor_dataframe]


instance = f1()
