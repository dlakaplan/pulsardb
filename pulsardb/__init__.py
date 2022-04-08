import requests
import numpy as np
from astropy import units as u, constants as c
from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy.table import Table
import pandas as pd
import os
import datetime
import loguru

from loguru import logger

_url = "http://localhost:8000/api/"
_json_header = {'Accept': 'application/json'}
_api_key_name = "PULSAR_API_KEY"

API_KEY = None
_auth_header = None
if _api_key_name in os.environ:
    # https://florimondmanca.github.io/djangorestframework-api-key/guide/#api-key-custom-keyword
    API_KEY = os.environ[_api_key_name]
    _auth_header = {"Authorization": f"Api-Key {API_KEY}"}

def _convert_time(t):
    if isinstance(t, Time):
        return  t.isot
    elif isinstance(t, datetime.datetime):
        return t.isoformat()
    elif isinstance(t, str):
        # hope astropy can convert
        return Time(t).isot
    elif isinstance(t, float):
        # assume MJD
        return Time(t, format='mjd').isot

class Pulsars():

    endpoint = "pulsars/"
    aliasendpoint = "pulsaraliases/"    
        
    @classmethod
    def get(self, format="json"):
        assert format.lower() in ["json","pandas","table"]
        response = requests.get(_url + self.endpoint, headers=_json_header)
        if response.status_code == 200:
            if format.lower() == "json":
                return response.json()
            elif format.lower() == "pandas":
                return pd.json_normalize(response.json())
            elif format.lower() == "table":
                return Table.from_pandas(pd.json_normalize(response.json()))
        else:
            logger.warning(f"Attempt to retrieve Pulsars from database did not succeed (code={response.status_code})")
        return response
            
    @classmethod
    def post(self, name, ra, dec, aliases=None):
        data = {"name": name,
                "ra": ra,
                "dec": dec}
        if _auth_header is None:
            logger.error(f"${_api_key_name} is required for POST")
            return None
        response = requests.post(_url + self.endpoint,
                                 json = data,
                                 headers=_auth_header)
        if response.status_code != 201:
            logger.warning(f"Attempt to add '{name}' to database did not succeed (code={response.status_code})")
        if aliases is not None and len(aliases)>0:
            response = [response]
            for alias in aliases:
                data = {"name": alias,
                        "pulsar": name}
                response.append(requests.post(_url + self.aliasendpoint,
                                              json = data,
                                 headers=_auth_header))
                if response[-1].status_code != 201:
                    logger.warning(f"Attempt to add '{alias}' as alias of '{name}' to database did not succeed (code={response[-1].status_code})")
                
        return response
    
        
class Telescopes():

    endpoint = "telescopes/"
        
    @classmethod
    def get(self, format="json"):
        assert format.lower() in ["json","pandas","table"]
        response = requests.get(_url + self.endpoint, headers=_json_header)
        if response.status_code == 200:
            if format.lower() == "json":
                return response.json()
            elif format.lower() == "pandas":
                return pd.json_normalize(response.json())
            elif format.lower() == "table":
                return Table.from_pandas(pd.json_normalize(response.json()))
        else:
            logger.warning(f"Attempt to retrieve Pulsars from database did not succeed (code={response.status_code})")

        return response

class Observations():

    endpoint = "observations/"
        
    @classmethod
    def get(self, pulsar=None, telescope=None, project=None,
            min_time=None, max_time=None, min_frequency=None, max_frequency=None,
            format="json"):
        assert format.lower() in ["json","pandas","table"]
        data = {}
        if pulsar is not None:
            data["pulsar"] = pulsar
        if telescope is not None:
            data["telescope"] = telescope
        if project is not None:
            data["project"] = project
        if min_time is not None:
            if isinstance(min_time,Time):
                data["min_MJD"] = min_time.mjd
            else:
                data["min_MJD"] = min_time
        if max_time is not None:
            if isinstance(max_time,Time):
                data["max_MJD"] = max_time.mjd
            else:
                data["max_MJD"] = max_time
        if min_frequency is not None:
            if isinstance(min_frequency, u.quantity.Quantity):
                data['min_frequency'] = min_frequency.to_value(u.MHz)
            else:
                data['min_frequency'] = min_frequency
        if max_frequency is not None:
            if isinstance(max_frequency, u.quantity.Quantity):
                data['max_frequency'] = max_frequency.to_value(u.MHz)
            else:
                data['max_frequency'] = max_frequency
                
        response = requests.get(_url + self.endpoint, params = data, headers=_json_header)
        if response.status_code == 200:
            if format.lower() == "json":
                return response.json()
            elif format.lower() == "pandas":
                return pd.json_normalize(response.json())
            elif format.lower() == "table":
                return Table.from_pandas(pd.json_normalize(response.json()))
        else:
            logger.warning(f"Attempt to retrieve Observations from database did not succeed (code={response.status_code})")
        return response

    @classmethod
    def post(self, pulsar, telescope, frequency, submitter, project, start, stop, notes=""):
        if _auth_header is None:
            logger.error(f"${_api_key_name} is required for POST")
            return None
        tstart = _convert_time(start)
        tstop = _convert_time(stop)
        if isinstance(frequency, u.quantity.Quantity):
            frequency = frequency.to_value(u.MHz)
        content = {"pulsar": pulsar,
                   "telescope": telescope,
                   "frequency": frequency,
                   "submitter": submitter,
                   "project": project,
                   "datetime_range": {"lower": tstart,
                                      "upper": tstop},
                   "notes": notes,
                   }
        response = requests.post(_url + self.endpoint,
                                 json = content,
                                 headers=_auth_header)
        if response.status_code != 201:
            logger.warning(f"Cannot add observation of {pulsar} starting at {tstart} to database: code={response.status_code}")
        return response
    
