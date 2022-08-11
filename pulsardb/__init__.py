import requests
import numpy as np
from astropy import units as u, constants as c
from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy.table import Table
import pandas as pd
import os
import datetime

from loguru import logger

_url = "http://localhost:8000/api/"
# _url = "https://observations.nanograv.org/api/"

_json_header = {"Accept": "application/json"}
_api_key_name = "PULSAR_API_KEY"

if _api_key_name in os.environ:
    # https://florimondmanca.github.io/djangorestframework-api-key/guide/#api-key-custom-keyword
    API_KEY = os.environ[_api_key_name]
    _auth_header = {"Authorization": f"Api-Key {API_KEY}"}
else:
    API_KEY = None
    _auth_header = None


def _convert_time(t):
    """Convert an input time from one of a number of format to ISO formatted string

    Parameters
    ----------
    t : Time, str, float
        Input time.  If float, MJD is assumed

    Returns
    -------
    str :
        ISO formatted string
    """
    if isinstance(t, Time):
        return t.isot
    elif isinstance(t, datetime.datetime):
        return t.isoformat()
    elif isinstance(t, str):
        # hope astropy can convert
        return Time(t).isot
    elif isinstance(t, float):
        # assume MJD
        return Time(t, format="mjd").isot


class Pulsars:
    """
    Database of pulsar names
    """

    endpoint = "pulsars-api/"
    aliasendpoint = "pulsaraliases-api/"

    @classmethod
    def get(self, pulsar=None, format="json"):
        """
        Retrieve list of pulsar names, plus any aliases and associated projects

        Parameters
        ----------
        pulsar : str, optional
            Pulsar name to match
        format : str, optional
            Format of output.  'JSON', 'pandas', 'table'


        Returns
        -------
        output :
            pulsar data (if successfully retrieved), otherwise result of `requests.get()` query

        """
        assert format.lower() in ["json", "pandas", "table"]
        data = {}
        if pulsar is not None:
            data["name"] = pulsar

        response = requests.get(_url + self.endpoint, params=data, headers=_json_header)
        if response.status_code == 200:
            if format.lower() == "json":
                return response.json()
            elif format.lower() == "pandas":
                return pd.json_normalize(response.json()["results"])
            elif format.lower() == "table":
                return Table.from_pandas(pd.json_normalize(response.json()["results"]))
        else:
            logger.warning(
                f"Attempt to retrieve Pulsars from database did not succeed (code={response.status_code})"
            )
        return response

    @classmethod
    def post(self, name, ra, dec, aliases=None, key=None):
        """
        Submit a pulsar to the database

        Parameters
        ----------
        name : str
        ra : float
            RA in degrees
        dec : float
            Dec in degrees
        aliases : iterable, optional
            List of pulsar name aliases
        key : str, optional
            API key (if '$PULSAR_API_KEY' is not defined)

        Returns
        -------
        respose :
            result of `requests.post()`
        """
        data = {"name": name, "ra": ra, "dec": dec}
        if (_auth_header is None) and (key is None):
            logger.error(
                f"${_api_key_name} is required for POST, or a value supplied by 'key=...'"
            )
            return None
        if key is not None:
            auth_header = {"Authorization": f"Api-Key {key}"}
        elif _auth_header is not None:
            auth_header = _auth_header

        response = requests.post(_url + self.endpoint, json=data, headers=auth_header)
        if response.status_code != 201:
            logger.warning(
                f"Attempt to add '{name}' to database did not succeed (code={response.status_code})"
            )
        if aliases is not None and len(aliases) > 0:
            response = [response]
            for alias in aliases:
                data = {"name": alias, "pulsar": name}
                response.append(
                    requests.post(
                        _url + self.aliasendpoint, json=data, headers=auth_header
                    )
                )
                if response[-1].status_code != 201:
                    logger.warning(
                        f"Attempt to add '{alias}' as alias of '{name}' to database did not succeed (code={response[-1].status_code})"
                    )

        return response


class Telescopes:
    """
    Database of Telescope names and aliases
    """

    endpoint = "telescopes-api/"

    @classmethod
    def get(self, format="json"):
        """
        Retrieve list of telescope names, plus any aliases

        Parameters
        ----------
        format : str, optional
            Format of output.  'JSON', 'pandas', 'table'


        Returns
        -------
        output :
            telescope data (if successfully retrieved), otherwise result of `requests.get()` query

        """

        assert format.lower() in ["json", "pandas", "table"]
        response = requests.get(_url + self.endpoint, headers=_json_header)
        if response.status_code == 200:
            if format.lower() == "json":
                return response.json()
            elif format.lower() == "pandas":
                return pd.json_normalize(response.json()["results"])
            elif format.lower() == "table":
                return Table.from_pandas(pd.json_normalize(response.json()["results"]))
        else:
            logger.warning(
                f"Attempt to retrieve Telescopes from database did not succeed (code={response.status_code})"
            )

        return response


class Observations:
    """
    Database of pulsar observations
    """

    endpoint = "observations-api/"

    @classmethod
    def get(
        self,
        pulsar=None,
        telescope=None,
        receiver=None,
        backend=None,
        project=None,
        min_time=None,
        max_time=None,
        min_frequency=None,
        max_frequency=None,
        format="json",
    ):
        """
        Retrieve list of observations

        Parameters
        ----------
        pulsar : str, optional
            Pulsar name to match
        telescope : str, optional
            Telescope name to match
        receiver : str, optional
            Receiver name to match
        backend : str, optional
            Backend name to match
        project : str, optional
            Project name to match
        min_time : `astropy.time.Time`, float, str, optional
            Minimum start time of observation (`float` is assumed to be MJD)
        max_time : `astropy.time.Time`, float, str, optional
            Maximum stop time of observation (`float` is assumed to be MJD)
        min_frequency : float or `astropy.units.quantity.Quantity`, optional
            Minimum frequency of observation (`float` is assumed to be MHz)
        max_frequency : float or `astropy.units.quantity.Quantity`, optional
            Maximum frequency of observation (`float` is assumed to be MHz)
        format : str, optional
            Format of output.  'JSON', 'pandas', 'table'

        Returns
        -------
        output :
            observation data (if successfully retrieved), otherwise result of `requests.get()` query

        """

        assert format.lower() in ["json", "pandas", "table"]
        data = {}
        if pulsar is not None:
            data["pulsar"] = pulsar
        if telescope is not None:
            data["telescope"] = telescope
        if receiver is not None:
            data["receiver"] = receiver
        if backend is not None:
            data["backend"] = backend
        if project is not None:
            data["project"] = project
        if min_time is not None:
            if isinstance(min_time, Time):
                data["min_MJD"] = min_time.mjd
            else:
                data["min_MJD"] = min_time
        if max_time is not None:
            if isinstance(max_time, Time):
                data["max_MJD"] = max_time.mjd
            else:
                data["max_MJD"] = max_time
        if min_frequency is not None:
            if isinstance(min_frequency, u.quantity.Quantity):
                data["min_frequency"] = min_frequency.to_value(u.MHz)
            else:
                data["min_frequency"] = min_frequency
        if max_frequency is not None:
            if isinstance(max_frequency, u.quantity.Quantity):
                data["max_frequency"] = max_frequency.to_value(u.MHz)
            else:
                data["max_frequency"] = max_frequency

        response = requests.get(_url + self.endpoint, params=data, headers=_json_header)
        if response.status_code == 200:
            if format.lower() == "json":
                return response.json()
            elif format.lower() == "pandas":
                return pd.json_normalize(response.json()["results"])
            elif format.lower() == "table":
                return Table.from_pandas(pd.json_normalize(response.json()["results"]))
        else:
            logger.warning(
                f"Attempt to retrieve Observations from database did not succeed (code={response.status_code})"
            )
        return response

    @classmethod
    def post(
        self,
        pulsar,
        telescope,
        receiver,
        backend,
        frequency,
        submitter,
        project,
        start,
        stop,
        notes="",
        key=None,
    ):
        """
        Submit a pulsar observation to the database

        Parameters
        ----------
        pulsar : str
            Pulsar name or alias
        telescope : str
            Telescope name or alias
        receiver : str
            Reciver name or alias
        backend : str
            Backend name
        frequency : float or `astropy.units.quantity.Quantity`
            Frequency (if `float` assumed to be MHz)
        submitter : int or str
            Name or ID of submitter
        project : str
            Project name
        start :  `astropy.time.Time`, float, str
            Start time of observation (`float` is assumed to be MJD)
        stop :  `astropy.time.Time`, float, str
            Stop time of observation (`float` is assumed to be MJD)
        notes : str, optional
            Any additional notes
        key : str, optional
            API key (if '$PULSAR_API_KEY' is not defined)

        Returns
        -------
        respose :
            result of `requests.post()`
        """

        if (_auth_header is None) and (key is None):
            logger.error(
                f"${_api_key_name} is required for POST, or a value supplied by 'key=...'"
            )
            return None
        if key is not None:
            auth_header = {"Authorization": f"Api-Key {key}"}
        elif _auth_header is not None:
            auth_header = _auth_header
        tstart = _convert_time(start)
        tstop = _convert_time(stop)
        if isinstance(frequency, u.quantity.Quantity):
            frequency = frequency.to_value(u.MHz)
        content = {
            "pulsar": pulsar,
            "telescope": telescope,
            "receiver": receiver,
            "backend": backend,
            "frequency": frequency,
            "submitter": submitter,
            "project": project,
            "datetime_range": {"lower": tstart, "upper": tstop},
            "notes": notes,
        }
        response = requests.post(
            _url + self.endpoint, json=content, headers=auth_header
        )
        if response.status_code != 201:
            logger.warning(
                f"Cannot add observation of {pulsar} starting at {tstart} to database: code={response.status_code}"
            )
        return response
