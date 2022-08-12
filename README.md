# Pulsar Observation Database Front-end

Use cases:
* If something weird happens with a pulsar (like J1713), how can we find out who else observed it during a given period?
* If we discover something odd with a telescope/backend for a given period, how can we identify which data might be affected?


Requires an API key for posting, either through environment variable `$PULSAR_API_KEY` or `key=...` in `post()` methods

Querying (through RESTful API or python):
* `pulsar=<name>`: query a pulsar by exact name (but this will also query by aliases)
* `pulsar_contains=<name>`: query a pulsar by partial match (will not also query aliases)
* `project=<name>`: query by one or more (logical OR)
* `min_time=<time>`: start time (`astropy` `Time`, float (MJD), or string that `astropy` can parse)
* `max_time=<time>`: end time (`astropy` `Time`, float (MJD), or string that `astropy` can parse)
* `min_frequency=<frequency>`: (`astropy` `Quantity` or float (MHz))
* `max_frequency=<frequency>`: (`astropy` `Quantity` or float (MHz))
* `backend=<name>`: query by one or more (logical OR)
* `receiver=<name>`: query by one or more (logical OR)
* `telescope=<name>`: query a telescope by exact name (but this will also query by aliases)
* `telescopes=<name>`: query a telescope by one or more exact names (logical OR, will not also query aliases)
* `sort=<key>`: can be `frequency`, `pulsar`, `telescope`, `project`, `submitter`, `datetime_range__startswith`, `datetime_range__endswith`.  Start key with `-` to do descending

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
