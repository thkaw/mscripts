# mscripts

This project contains two Python scripts:

- `mteam.py`: interact with the M-Team API to fetch or search torrents.
- `backup.py`: organize photos and videos into folders by creation date.

## Container usage

Build the image:

```bash
docker build -t mscripts .
```

Run the default `mteam.py` script (the configuration file `mteam.json` can be mounted to provide API key and paths):

```bash
docker run --rm -v $(pwd)/mteam.json:/app/mteam.json mscripts --help
```

To execute `backup.py`, override the command:

```bash
docker run --rm -v /path/to/src:/src -v /path/to/dst:/dst mscripts backup.py /src /dst
```

Example, get latest free torrent:

```bash
docker run --rm -v $(pwd)/mteam.json:/app/mteam.json -v $(pwd)/torrent/:/torrent/ mscripts mteam.py latest --output /torrent/
```
