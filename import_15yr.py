import os
import sys
import pulsardb.fromtim
import pint.logging

pint.logging.setup(level="WARNING")

submitter = "kaplan"
for filename in sys.argv[1:]:
    pulsar = os.path.split(filename)[-1].split(".")[0]
    outtxt = pulsardb.fromtim.fromtim(
        filename,
        pulsar,
        submitter,
    )
    outname = filename.replace(".tim", ".csv")
    with open(outname, "w") as f:
        f.write(outtxt)
        print(f"Wrote data for {pulsar} from {filename} to {outname}")
