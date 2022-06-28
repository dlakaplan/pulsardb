import argparse
import numpy as np
import sys

from astropy import units as u
from astropy.time import Time, TimeDelta

from loguru import logger as log

import pint.toa
import pint.logging

import pulsardb


def main():
    parser = argparse.ArgumentParser(
        description="""Add observations to database from tim file.  
        Can be read using e.g.,
            `Table.read('test.csv',format='ascii.commented_header',delimiter=',')`""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("timfile", help="Name of tim file")
    parser.add_argument("--pulsar", required=True, help="Name of pulsar (required)")
    parser.add_argument(
        "--submitter", required=True, help="Username of submitter (required)"
    )
    parser.add_argument("--out", default=None, help="Destination file (if not stdout)")
    parser.add_argument(
        "--durationflag", default="tobs", help="Flag for observation duration"
    )
    parser.add_argument(
        "--duration",
        default=1800,
        type=int,
        help="[s] Duration when not otherwise specified",
    )
    parser.add_argument("--receiverflag", default="fe", help="Flag for receiver")
    parser.add_argument("--receiver", help="Reciver when not otherwise specified")
    parser.add_argument("--backendflag", default="be", help="Flag for backend")
    parser.add_argument("--backend", help="Backend when not otherwise specified")
    parser.add_argument("--projectflag", default="pta", help="Flag for project")
    parser.add_argument("--project", help="Project when not otherwise specified")

    parser.add_argument(
        "--log-level",
        type=str,
        choices=("TRACE", "DEBUG", "INFO", "WARNING", "ERROR"),
        default=pint.logging.script_level,
        help="Logging level",
        dest="loglevel",
    )
    args = parser.parse_args()
    pint.logging.setup(level=args.loglevel)

    telescopes = pulsardb.Telescopes.get(format="table")
    toas = pint.toa.get_TOAs(args.timfile)
    log.info(f"Read {len(toas)} TOAs from {args.timfile}")
    # these should uniquely identify the observations
    names = np.array(toas.get_flag_value("name")[0])
    if args.out is not None:
        fout = open(args.out, "w")
    else:
        fout = sys.stdout
    print(
        f"# Start, Stop, Pulsar, Project, Telescope, Receiver, Backend, Frequency, Submitter",
        file=fout,
    )
    for name in np.unique(names):
        select = names == name
        frequency = toas[select].table["freq"].mean() * u.MHz
        start = Time(toas[select].get_mjds().min(), format="mjd")
        duration = (
            np.array(
                toas[select].get_flag_value(
                    args.durationflag, fill_value=args.duration, as_type=float
                )[0]
            )
            * u.s
        ).max()
        stop = start + duration
        # assume they all have the same values of these (check?)
        receiver = toas[select].get_flag_value(
            args.receiverflag, fill_value=args.receiver
        )[0][0]
        backend = toas[select].get_flag_value(
            args.backendflag, fill_value=args.backend
        )[0][0]
        project = toas[select].get_flag_value(
            args.projectflag, fill_value=args.project
        )[0][0]
        telescope = None
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
                f"{start.mjd}, {stop.mjd}, {args.pulsar}, {project}, {telescope}, {receiver}, {backend}, {frequency.to_value(u.MHz)}, {args.submitter}",
                file=fout,
            )
        else:
            log.warning(
                f"Cannot post entry with undefined telescope for observation {name}"
            )
    if args.out is not None:
        log.info(f"Wrote to {args.out}")


if __name__ == "__main__":
    main()
