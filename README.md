# Pulsar Observation Database Front-end

Use cases:
* If something weird happens with a pulsar (like J1713), how can we find out who else observed it during a given period?
* If we discover something odd with a telescope/backend for a given period, how can we identify which data might be affected?


Requires an API key for posting, either through environment variable `$PULSAR_API_KEY` or `key=...` in `post()` methods

Examples:

Post an observation:
```
pulsardb.Observations.post(pulsar="J0406+30",telescope="Arecibo",frequency=200*u.MHz, project="NANOGrav", submitter="kaplan", start=Time("2022-02-01"), stop=Time("2022-02-02"))
```

Get observations with the VLA starting after a particular time in `pandas` format:
```
pulsardb.Observations.get(telescope="VLA",format='pandas',min_time=Time('2019-12-01'))
```

Add a new pulsar with optional aliases:
```
pulsardb.Pulsars.post(name="test",ra=1.234,dec=5.67,aliases=['test2'])
```

Get all pulsars in `astropy.Table` format:
```
pulsardb.Pulsars.get(format="table")
```

Get all telescopes in JSON format:
```
pulsardb.Telescopes.get()
```
