from bs4 import BeautifulSoup
from icalendar import Calendar
from multiprocessing.dummy import Pool as ThreadPool
from dateutil import parser
from tqdm import tqdm

import metapy
import requests
import datetime
import time
import xml.etree.ElementTree as ElementTree

tqdm.monitor_interval = 0
TODAY = datetime.datetime.today()
HEADERS = {'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
CHAMPAIGN_URL = 'https://www.visitchampaigncounty.org/events/rss'
UIUC_URL = 'http://calendars.illinois.edu/ical/7.ics'
CANOPY_URL = 'http://canopyclub.com/calendar/?ical=1&tribe_display=list'
KRANNERT_URL = 'https://krannertcenter.com/calendar/print?date=%s' % str(TODAY.year)
PARKS_URL = 'https://champaignparks.com/events/?ical=1&tribe_display=list'
CAMPUSTOWN_URL = 'https://campustowns.com/events/?ical=1&tribe_display=list'
N_ESCAPE_DELIMINATOR = ' !@#$ '
R_ESCAPE_DELIMINATOR = ' $#@! '

def hour_to_num(hour):
    hour_list = hour.split(':')
    hour_period = filter(lambda x: x.isalpha(), hour_list[1])
    if hour_period == 'am':
        if hour_list[0] == '12':
            return 0
        return int(hour_list[0])
    else:
        if hour_list[0] == '12':
            return 12
        return int(hour_list[0]) + 12

def minute_to_num(minute):
    min_list = minute.split(':')
    return int(filter(lambda x: x.isdigit(), min_list[1]))

def get_uiuc_datetime(date_str):
    date_list = date_str.split()
    date_str = '%s %s %s %s %s' % (date_list[3], date_list[1], date_list[2], hour_to_num(date_list[6]), minute_to_num(date_list[6]))
    return datetime.datetime.strptime(date_str, '%Y %B %d %H %M')

def remove_nonascii(s):
    return "".join(i for i in s if ord(i)<128)

def format_string(s):
    s = remove_nonascii(s)
    s = s.replace('\n', N_ESCAPE_DELIMINATOR)
    s = s.replace('\r', R_ESCAPE_DELIMINATOR)
    s = s.replace('</br><span class="sty3">', '   ')
    s = s.replace('</span><br /></br>', '   ')
    return s

def get_uiuc_event(item):
    link = item.find('link').text
    title = format_string(item.find('title').text)
    response = requests.get(link, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    temp_over = soup.find('meta', property='og:description')
    temp_keys = soup.find('meta', property='og:keywords')
    overview = format_string(temp_over['content']) if temp_over else 'None'
    keywords = format_string(temp_keys['content']) if temp_keys else 'None'
    date = get_uiuc_datetime(format_string(item.find('description').text))

    event = [title, date, overview, keywords, link]
    return event

def write_ical_data(calendar, data, labels, metadata):
    gcal = Calendar.from_ical(calendar.read())
    for x, component in tqdm(enumerate(gcal.walk())):
        if component.name == "VEVENT":
            link = component.get('url')
            title = format_string(component.get('summary'))
            overview = format_string(component.get('description'))
            if overview == '' or overview == ' ':
                overview = 'None'
            date = component.get('dtstart').dt
            data.write('%s %s\n' % (title, overview))
            labels.write('%s\n' % title)
            metadata.write('%s	%s	%s	None	%s\n' % (title, str(date), overview, link))
    calendar.close()

def generate_events():
    """
    Generates event data from a variety of sources. Writes the data into
    MeTA compatible data files.
    """

    # Open MeTA files for data
    data = open('events/events.dat', 'w')
    labels = open('events/events.dat.labels', 'w')
    metadata = open('events/metadata.dat', 'w')

    # Get events from ics files
    response = requests.get(UIUC_URL, headers=HEADERS, allow_redirects=False)
    open('events/general_events.ics', 'wb').write(response.content)
    response = requests.get(CANOPY_URL, headers=HEADERS, allow_redirects=False)
    open('events/canopy_club.ics', 'wb').write(response.content)
    response = requests.get(PARKS_URL, headers=HEADERS, allow_redirects=False)
    open('events/champaign_parks.ics', 'wb').write(response.content)
    response = requests.get(CAMPUSTOWN_URL, headers=HEADERS, allow_redirects=False)
    open('events/campus_town.ics', 'wb').write(response.content)
    print('UIUC General Events:')
    write_ical_data(open('events/general_events.ics', 'rb'), data, labels, metadata)
    print('Canopy Club:')
    write_ical_data(open('events/canopy_club.ics', 'rb'), data, labels, metadata)
    print('Champaign Parks:')
    write_ical_data(open('events/champaign_parks.ics', 'rb'), data, labels, metadata)
    print('CampusTowns:')
    write_ical_data(open('events/campus_town.ics', 'rb'), data, labels, metadata)

    # Get Krannert events
    page = requests.get(KRANNERT_URL, headers=HEADERS)
    soup = BeautifulSoup(page.content, 'html.parser')
    titles = soup.findAll('td', {'class' : 'views-field views-field-title views-align-left'})
    urls = ['https://krannertcenter.com%s' % title.find('a')['href'] for title in titles]
    print("Kranner Center:")
    pool = ThreadPool(16)
    pages = []
    for page in tqdm(pool.imap_unordered(requests.get, urls), total=len(urls)):
        pages.append(page)
    pool.close()
    pool.join()

    for x in range(0, len(titles)):
        link = urls[x]
        page = pages[x]
        soup = BeautifulSoup(page.content, 'html.parser')
        temp_over = soup.find('meta', property='og:description')
        overview = temp_over['content'] if temp_over else 'None'
        overview = format_string(overview)
        words = soup.findAll('span', {'class' : 'types '})
        keywords = ''
        for word in words:
            keywords += '%s, ' % format_string(word.find('a').contents[0])
        if keywords == '':
            keywords = 'None'
        keywords = format_string(keywords)
        title = format_string(titles[x].find('a').contents[0])
        date_str = soup.find('div', {'class' : 'event-date'})
        if date_str:
            date = datetime.datetime.strptime(date_str.contents[0][3:], '%b %d, %Y - %I:%M%p')
        else:
            date = datetime.datetime(2999, 1, 1)

        if date >= TODAY:
            data.write('%s	%s	%s\n' % (title, overview, keywords))
            labels.write('%s' % title)
            metadata.write('%s	%s	%s	%s	%s\n' % (title, str(date), overview, keywords, link))

    # Get Champaign County events
    response = requests.get(CHAMPAIGN_URL, headers=HEADERS)
    tree = ElementTree.fromstring(response.content)
    channel = tree.find('channel')
    items = []
    for item in channel:
        if item.tag == 'item':
            items.append(item)
    pool = ThreadPool(8)
    print('Champaign County:')
    uiuc_events = []
    for event in tqdm(pool.imap(get_uiuc_event, items), total=len(items)):
        uiuc_events.append(event)
    pool.close()
    pool.join()
    for event in uiuc_events:
        data.write('%s %s %s\n' % (event[0], event[2], event[3]))
        labels.write('%s\n' % event[0])
        metadata.write('%s	%s	%s	%s	%s\n' % (event[0], event[1], event[2], event[3], event[4]))
