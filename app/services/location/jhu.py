from . import LocationService
from ...location import TimelinedLocation
from ...coordinates import Coordinates
from ...timeline import Timeline
import app
from flask_pymongo import PyMongo

from collections import OrderedDict
from flask import current_app as appp

mongo = PyMongo(appp, connect=True)

class TimeL:
    """
    Timeline clone.
    """

    def __init__(self, timelines, latestt):
        self.__timeline = timelines
        self.__latest = latestt

    @property
    def timeline(self):
        """
        Gets the history sorted by date (key).
        """
        return OrderedDict(sorted(self.__timeline.items()))

    @property
    def latest(self):
        """
        Gets the latest available history value.
        """
        return self.__latest or 0

    def serialize(self):
        """
        Serializes the timeline into a dict.

        :returns: The serialized timeline.
        :rtype: dict
        """
        return {
            'latest'  : self.latest,
            'timeline': self.timeline
        }


class JhuLocationService(LocationService):
    """
    Service for retrieving locations from Johns Hopkins CSSE (https://github.com/CSSEGISandData/COVID-19).
    """

    def get_all(self):
        # Get the locations.
        return get_locations()
    
    def get(self, id):
        # Get location at the index equal to provided id.
        return self.get_all()[id]

# ---------------------------------------------------------------

import requests
import csv
from datetime import datetime
from cachetools import cached, TTLCache
from ...utils import countrycodes, date as date_util

"""
Base URL for fetching category.
"""
base_url = 'https://raw.githubusercontent.com/CSSEGISandData/2019-nCoV/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-%s.csv';

@cached(cache=TTLCache(maxsize=1024, ttl=3600))
def get_category(category):
    """
    Retrieves the data for the provided category. The data is cached for 1 hour.

    :returns: The data for category.
    :rtype: dict
    """

    # Adhere to category naming standard.
    category = category.lower().capitalize();

    # Request the data
    request = requests.get(base_url % category)
    text    = request.text

    # Parse the CSV.
    data = list(csv.DictReader(text.splitlines()))

    # The normalized locations.
    locations = []

    for item in data:
        # Filter out all the dates.
        dates = dict(filter(lambda element: date_util.is_date(element[0]), item.items()))

        # Make location history from dates.
        history = { date: int(amount or 0) for date, amount in dates.items() };

        # Country for this location.
        country = item['Country/Region']

        # Latest data insert value.
        latest = list(history.values())[-1];

        # Normalize the item and append to locations.
        locations.append({
            # General info.
            'country':  country,
            'country_code': countrycodes.country_code(country),
            'province': item['Province/State'],

            # Coordinates.
            'coordinates': {
                'lat':  item['Lat'],
                'long': item['Long'],
            },

            # History.
            'history': history,

            # Latest statistic.
            'latest': int(latest or 0),
        })

    # Latest total.
    latest = sum(map(lambda location: location['latest'], locations))

    # Return the final data.
    return {
        'locations': locations,
        'latest': latest,
        'last_updated': datetime.utcnow().isoformat() + 'Z',
        # 'source': 'https://github.com/ExpDev07/coronavirus-tracker-api',
    }

@cached(cache=TTLCache(maxsize=1024, ttl=3600))
def get_locations():
    """
    Retrieves the locations from the categories. The locations are cached for 1 hour.

    :returns: The locations.
    :rtype: List[Location]
    """
    # Get all of the data categories locations.
    confirmed = get_category('confirmed')['locations']
    deaths    = get_category('deaths')['locations']
    recovered = get_category('recovered')['locations']

    # Final locations to return.
    locations = []
    res = mongo.db.nigeria.find()
    naija = list(res)
    print(naija[0]['latest'])
        # Go through locations.
    for index, location in enumerate(confirmed):
        # Get the timelines.
        timelines = {
            'confirmed' : confirmed[index]['history'],
            'deaths'    : deaths[index]['history'],
            'recovered' : recovered[index]['history'],
        }
        # print(confirmed[index]['history'])
        yesterday = { 
            'confirmed': list(confirmed[index]['history'].items())[-2][1],
            'deaths'   : list(deaths[index]['history'].items())[-2][1],
            'recovered': list(recovered[index]['history'].items())[-2][1]
        }

        

        
        # Grab coordinates.
        coordinates = location['coordinates']
        
        if location['country_code'] == 'NG':
            print('i entered here')
            location['latest'] = naija[0]['latest']
            yesterday = naija[0]['locations'][0]['yesterday']
            last_data = {
                'confirmed': TimeL(confirmed[index]['history'],  naija[0]['latest']['confirmed']),
                'deaths': TimeL(deaths[index]['history'], naija[0]['latest']['deaths']),
                'recovered': TimeL(recovered[index]['history'],naija[0]['latest']['recovered'])
            }
        else:
            last_data =    {
                'confirmed': Timeline({ datetime.strptime(date, '%m/%d/%y').isoformat() + 'Z': amount for date, amount in timelines['confirmed'].items() }),
                'deaths'   : Timeline({ datetime.strptime(date, '%m/%d/%y').isoformat() + 'Z': amount for date, amount in timelines['deaths'].items() }),
                'recovered': Timeline({ datetime.strptime(date, '%m/%d/%y').isoformat() + 'Z': amount for date, amount in timelines['recovered'].items() })
            }

            # last_data = naija[0]['latest']
        # Create location (supporting timelines) and append.
        locations.append(TimelinedLocation(
            # General info.
            index, location['country'], location['province'],
            
            # Coordinates.
            Coordinates(
                coordinates['lat'], 
                coordinates['long']
            ),

            # Last update.
            datetime.utcnow().isoformat() + 'Z', yesterday,
            
            # Timelines (parse dates as ISO).
            last_data
        ))
            
        
    
    # Finally, return the locations.
    return locations
        