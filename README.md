# pulsardb

Examples:

Post an observation:
```
pulsardb.Observations.post(pulsar="J0406+30",telescope="Arecibo",frequency=200*u.MHz, project="NANOGrav", submitter="kaplan", start=Time("2022-02-01"), stop=Time("2022-02-02"))
```

Get observations with the VLA starting after a particular time in `pandas` format:
```
pulsardb.Observations.get(telescope="VLA",format='pandas',min_time=Time('2019-12-01'))
```
