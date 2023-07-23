import re
from io import StringIO
from typing import Any, Generator, Tuple, Optional, List
import requests
from requests.adapters import HTTPAdapter
from streamlit.connections import ExperimentalBaseConnection
from streamlit.runtime.caching import cache_data
import pandas as pd
from urllib3 import Retry

class NASA_APIConnection(ExperimentalBaseConnection[requests.Session]):
    """Basic st.experimental_connection implementation for NASA API"""

    def __init__(self, connection_name: str,
                 api_key: str,
                 base_url: str = 'https://api.nasa.gov/',
                 total_retries: int = 5,
                 backoff_factor: float = 0.25,
                 status_forcelist: List[int] = None,
                 **kwargs):

        self.api_key = api_key
        self.base_url = base_url

        if status_forcelist is None:
            status_forcelist = [500, 502, 503, 504]

        self.retries = Retry(total=total_retries, backoff_factor=backoff_factor, status_forcelist=status_forcelist)

        super().__init__(connection_name, **kwargs)

    def _connect(self, **kwargs: Any) -> requests.Session:
        """Connects to the Session

        :returns: requests.Session
        """
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=self.retries))
        return session

    def query_apod(self, date: str, cache_time: int = 3600, **kwargs: Any) -> pd.DataFrame:
        """Queries the Astronomy Picture Of The Day API and returns a DataFrame.

        :param date: specific date in the format 'YYYY-MM-DD' or 'latest' for the latest APOD
        :param cache_time: time to cache the result
        :param kwargs: other optional parameters
        :returns: result as a DataFrame
        """

        @cache_data(ttl=cache_time)
        def _query_apod(date: str, **kwargs: Any) -> pd.DataFrame:
            params = {'api_key': self.api_key, **kwargs}
            
            if date.lower() == 'latest':
                url = self.base_url + 'planetary/apod'
            else:
                url = self.base_url + 'planetary/apod'
                params = {'date': date, 'api_key': self.api_key, **kwargs}

            try:
                response = self._instance.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                # Create a DataFrame from the JSON response
                result = pd.DataFrame(data, index=[0])

                return result
            except Exception as e:
                print(f"An error occurred: {e}")
                return None

        return _query_apod(date, **kwargs)


    def query_neows(self, start_date: str, end_date: str, cache_time: int = 3600, **kwargs: Any) -> pd.DataFrame:
        """Queries the Near-Earth Object Web Service (NEOWS) API and returns a DataFrame.

        :param start_date: start date in the format 'YYYY-MM-DD'
        :param end_date: end date in the format 'YYYY-MM-DD'
        :param cache_time: time to cache the result
        :param kwargs: other optional parameters
        :returns: result as a DataFrame
        """

        @cache_data(ttl=cache_time)
        def _query_neows(start_date: str, end_date: str, **kwargs: Any) -> pd.DataFrame:
            params = {'start_date': start_date, 'end_date': end_date, 'api_key': self.api_key, **kwargs}

            url = self.base_url + 'neo/rest/v1/feed'

            try:
                response = self._instance.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                # Flatten the nested JSON response to create a DataFrame
                neows_data = data['near_earth_objects']
                neows_list = []
                for date in data['near_earth_objects']:
                    for obj in data['near_earth_objects'][date]:
                        obj_data = {
                            'id': obj['id'],
                            'name': obj['name'],
                            'neo_reference_id': obj['neo_reference_id'],
                            'close_approach_date': obj['close_approach_data'][0]['close_approach_date'],
                            'nasa_jpl_url': obj['nasa_jpl_url'],
                            'absolute_magnitude_h': obj['absolute_magnitude_h'],
                            'estimated_diameter_min_km': obj['estimated_diameter']['kilometers']['estimated_diameter_min'],
                            'estimated_diameter_max_km': obj['estimated_diameter']['kilometers']['estimated_diameter_max'],
                            'estimated_diameter_min_m': obj['estimated_diameter']['meters']['estimated_diameter_min'],
                            'estimated_diameter_max_m': obj['estimated_diameter']['meters']['estimated_diameter_max'],
                            'is_potentially_hazardous_asteroid': obj['is_potentially_hazardous_asteroid'],
                            'relative_velocity_kms': obj['close_approach_data'][0]['relative_velocity']['kilometers_per_second'],
                            'miss_distance_km': obj['close_approach_data'][0]['miss_distance']['kilometers'],
                            'orbiting_body': obj['close_approach_data'][0]['orbiting_body']
                        }

                        neows_list.append(obj_data)

                result = pd.DataFrame(neows_list)

                return result
            except Exception as e:
                print(f"An error occurred: {e}")
                return None

        return _query_neows(start_date, end_date, **kwargs)


    def query_mars_rover_photos(self, rover_name: str, sol: str, cache_time: int = 3600, **kwargs: Any) -> pd.DataFrame:
        """Queries the Mars Rover Photos API and returns a DataFrame containing photos for the specified rover and sol.

        :param rover_name: name of the rover (Curiosity, Opportunity, or Spirit)
        :param sol: Martian sol (a Martian day) to get photos for
        :param cache_time: time to cache the result
        :param kwargs: other optional parameters
        :returns: result as a DataFrame
        """

        @cache_data(ttl=cache_time)
        def _query_mars_rover_photos(rover_name: str, sol: str, **kwargs: Any) -> pd.DataFrame:
            params = {'sol': sol, 'api_key': self.api_key, **kwargs}

            url = self.base_url + f'mars-photos/api/v1/rovers/{rover_name}/photos'

            try:
                response = self._instance.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                # Extract photos from the JSON response
                photos = data.get('photos', [])

                # Create a DataFrame from the list of photos
                result = pd.DataFrame(photos[0:100])

                return result
            except Exception as e:
                print(f"An error occurred: {e}")
                return None

        return _query_mars_rover_photos(rover_name, sol, **kwargs)

    def query_donki(self, start_date: str = None, end_date: str = None, type: str = "all", cache_time: int = 3600, **kwargs: Any) -> pd.DataFrame:
        """Queries the NASA DONKI API and returns a DataFrame containing space weather events.

        :param start_date: start date in the format 'YYYY-MM-DD' (default: 30 days prior to current UTC date)
        :param end_date: end date in the format 'YYYY-MM-DD' (default: current UTC date)
        :param type: type of event (default is 'all')
        :param cache_time: time to cache the result
        :param kwargs: other optional parameters
        :returns: result as a DataFrame
        """

        @cache_data(ttl=cache_time)
        def _query_donki(start_date: str, end_date: str, type: str, **kwargs: Any) -> pd.DataFrame:
            params = {
                'startDate': start_date,
                'endDate': end_date,
                'api_key': self.api_key,
                **kwargs
            }

            url = self.base_url + f'DONKI/{type}'

            try:
                response = self._instance.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Create a DataFrame from the JSON response
                try:
                    result = pd.DataFrame(data)
                except:
                    result = data

                return result
            except Exception as e:
                print(f"An error occurred: {e}")
                return None

        return _query_donki(start_date, end_date, type, **kwargs)
    def query_exoplanet_data(self, table: str, where: str = None, select: str = None, order: str = None, format: str = "csv", cache_time: int = 3600, **kwargs: Any) -> pd.DataFrame:
        """Queries the NASA Exoplanet Archive API and returns a DataFrame containing exoplanet data.

        :param table: name of the data table to query (e.g., 'cumulative')
        :param where: 'where' clause to specify filtering conditions (optional)
        :param select: 'select' clause to specify columns to return (optional)
        :param order: 'order' clause to specify the order of rows (optional)
        :param format: preferred output file format ('csv' or 'ipac') (default: 'csv')
        :param cache_time: time to cache the result
        :param kwargs: other optional parameters
        :returns: result as a DataFrame
        """

        @cache_data(ttl=cache_time)
        def _query_exoplanet_data(table: str, where: str, select: str, order: str, **kwargs: Any) -> pd.DataFrame:
            base_url = "https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?"
            params = {
                'select': select,
                'order': order,
                'api_key': self.api_key,
                **kwargs
            }

            # Construct the query URL with table and other parameters
            url = base_url + f'table={table}'
            if where:
                url += f'&where={where}'

            try:
                response = self._instance.get(url, params=params)
                response.raise_for_status()
                data = response.text

                # Handle different output formats (csv or ipac)
                if format == "csv":
                    result = pd.read_csv(StringIO(data))

                return result
            except Exception as e:
                print(f"An error occurred: {e}")
                return None

        return _query_exoplanet_data(table, where, select, order, **kwargs)
