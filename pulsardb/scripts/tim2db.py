import argparse
import numpy as np
import sys

from astropy import units as u
from astropy.time import Time, TimeDelta

from loguru import logger as log

import pint.toa
import pint.logging

import pulsardb
import pulsardb.fromtim


def main():
    parser = argparse.ArgumentParser(
        description="""Make CSV database entries from tim file, and optionally upload to database.
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
        "--telescope", default=None, help="Telescope when not otherwise specified"
    )
    parser.add_argument(
        "--db",
        action="store_true",
        default=False,
        help="Directly upload to database (may be slow)?",
    )
    parser.add_argument(
        "--apikey",
        help="API key for direct submission (or specify via $PULSAR_API_KEY)",
    )

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
    outtxt = pulsardb.fromtim.fromtim(
        args.timfile,
        args.pulsar,
        args.submitter,
        durationflag=args.durationflag,
        duration=args.duration,
        receiverflag=args.receiverflag,
        receiver=args.receiver,
        backendflag=args.backendflag,
        backend=args.backend,
        projectflag=args.projectflag,
        project=args.project,
        telescope=args.telescope,
        db=args.db,
        apikey=args.apikey,
    )
    if args.out is None:
        outfile = sys.stdout
    else:
        outfile = open(args.out, "w")
    outfile.write(outtxt)
    if args.out is not None:
        log.info(f"Wrote to {args.out}")


if __name__ == "__main__":
    main()
