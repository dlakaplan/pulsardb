import numpy as np
import sys

from astropy import units as u
from astropy.time import Time, TimeDelta

from loguru import logger as log

import pint.toa
import pint.logging

import pulsardb


def fromtim(
    timfile,
    pulsar,
    submitter,
    out=None,
    durationflag="tobs",
    duration=1800,
    receiverflag="fe",
    receiver=None,
    backendflag="be",
    backend=None,
    projectflag="pta",
    project=None,
    telescope=None,
    db=False,
    apikey=None,
):

    telescopes = pulsardb.Telescopes.get(format="table")
    toas = pint.toa.get_TOAs(timfile)
    log.info(f"Read {len(toas)} TOAs from {timfile}")
    # these should uniquely identify the observations
    names = np.array(toas.get_flag_value("name")[0])
    if out is not None:
        fout = open(out, "w")
    else:
        fout = sys.stdout
    print(
        f"# Start, Stop, Pulsar, Project, Telescope, Receiver, Backend, Frequency, Submitter",
        file=fout,
    )
    defaulttelescope = telescope
    for name in np.unique(names):
        select = names == name
        frequency = toas[select].table["freq"].mean() * u.MHz
        start = Time(toas[select].get_mjds().min(), format="mjd")
        duration = (
            np.array(
                toas[select].get_flag_value(
                    durationflag, fill_value=duration, as_type=float
                )[0]
            )
            * u.s
        ).max()
        stop = start + duration
        # assume they all have the same values of these (check?)
        receiver = toas[select].get_flag_value(receiverflag, fill_value=receiver)[0][0]
        backend = toas[select].get_flag_value(backendflag, fill_value=backend)[0][0]
        project = toas[select].get_flag_value(projectflag, fill_value=project)[0][0]
        telescope = defaulttelescope
        for telname in telescopes["name"]:
            if (
                receiver
                in list(telescopes[telescopes["name"] == telname]["receivers"])[0]
                and backend
                in list(telescopes[telescopes["name"] == telname]["backends"])[0]
            ):
                telescope = telname

        log.info(
            f"Observation {name} at {start} with project={project}, telescope={telescope}, receiver={receiver}, backend={backend}, frequency={frequency}, duration={duration}"
        )
        if telescope is not None:
            print(
                f"{start.mjd}, {stop.mjd}, {pulsar}, {project}, {telescope}, {receiver}, {backend}, {frequency.to_value(u.MHz)}, {submitter}",
                file=fout,
            )
            if db:
                response = pulsardb.Observations.post(
                    pulsar=pulsar,
                    telescope=telescope,
                    frequency=frequency,
                    project=project,
                    start=start,
                    stop=stop,
                    receiver=receiver,
                    backend=backend,
                    submitter=submitter,
                    key=apikey,
                )
        else:
            log.warning(
                f"Cannot determine entry with undefined telescope for observation {name}"
            )
    if out is not None:
        log.info(f"Wrote to {out}")
