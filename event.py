import generate_events
import metapy
import datetime
import re

def deformat_string(s):
    s = s.replace(generate_events.N_ESCAPE_DELIMINATOR, '\n')
    s = s.replace(generate_events.R_ESCAPE_DELIMINATOR, '\r')
    return s

class Event:
    """
    Simple object representation of an event
    """
    def __init__(self, idx, d_id):
        """
        Create event from its data in a MeTA index
        """
        data = idx.metadata(d_id)
        self.d_id = d_id
        self.title = data.get('title')
        self.overview = deformat_string(data.get('overview'))
        self.keywords = data.get('keywords')
        self.link = data.get('link')

        date_str = data.get('date')
        date_str = (date_str[:19]) if len(date_str) > 19 else date_str
        if len(date_str) == 10 or len(date_str) == 12:
            date_str = (date_str[:10])
            self.date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        else:
            try:
                self.date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                self.date = datetime.datetime(2999, 1, 1, 0, 0, 0)

        if self.date < datetime.datetime.now():
            self.date = datetime.datetime.now()

        self.start = self.date - datetime.timedelta(days=self.date.weekday())
        self.end = self.start + datetime.timedelta(days=6)

    def __lt__(self, other):
        """
        Define events to be sorted by their dates
        """
        return self.date < other.date

    def __eq__(self, other):
        """
        Define events to be equal to each other if they have the same name
        and are from the same host
        """
        this_title = ''.join(re.split('[^a-zA-Z]*', self.title))
        other_title = ''.join(re.split('[^a-zA-Z]*', other.title))
        return this_title == other_title and self.link[:20] == other.link[:20]

    def __ne__(self, other):
        """
        Define events to be not equal to each other when they have different
        names or are from different hosts
        """
        return not self.__eq__(other)
