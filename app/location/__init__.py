from ..coordinates import Coordinates
from ..utils import countrycodes

class Location:
    """
    A location in the world affected by the coronavirus.
    """

    def __init__(self, id, country, province, coordinates, last_updated, yesterday, confirmed, deaths, recovered):
        # General info.
        self.id = id
        self.country = country.strip()
        self.province = province.strip()
        self.coordinates = coordinates

        # Last update.
        self.last_updated = last_updated

        # history
        self.yesterday = yesterday;

        # Statistics.
        self.confirmed = confirmed
        self.deaths = deaths
        self.recovered = recovered
        
    @property
    def country_code(self):
        """
        Gets the alpha-2 code represention of the country. Returns 'XX' if none is found.
        """
        return (countrycodes.country_code(self.country) or countrycodes.default_code).upper()

    def serialize(self):
        """
        Serializes the location into a dict.

        :returns: The serialized location.
        :rtype: dict
        """
        return {
            # General info.
            'id'          : self.id,
            'country'     : self.country, 
            'country_code': self.country_code,
            'province'    : self.province,

            # Coordinates.
            'coordinates': self.coordinates.serialize(),

            # Last updated.
            'last_updated': self.last_updated,

            # yesterday
            'yesterday': self.yesterday,

            # Latest data (statistics).
            'latest': {
                'confirmed': self.confirmed,
                'deaths'   : self.deaths,
                'recovered': self.recovered
            },
        }

class TimelinedLocation(Location):
    """
    A location with timelines.
    """

    def __init__(self, id, country, province, coordinates, last_updated, yesterday, timelines):
        super().__init__(
            # General info.
            id, country, province, coordinates, last_updated, yesterday,

            # Statistics (retrieve latest from timelines).
            confirmed=timelines.get('confirmed').latest or 0,
            deaths=timelines.get('deaths').latest or 0,
            recovered=timelines.get('recovered').latest or 0,
        )

        # Set timelines.
        self.timelines = timelines

    def serialize(self, timelines = False):
        """
        Serializes the location into a dict.

        :param timelines: Whether to include the timelines.
        :returns: The serialized location.
        :rtype: dict
        """
        serialized = super().serialize()

        # Whether to include the timelines or not.
        if timelines:
            serialized.update({ 'timelines': {
                # Serialize all the timelines.
                key: value.serialize() for (key, value) in self.timelines.items()
            }})

        # Return the serialized location.
        return serialized