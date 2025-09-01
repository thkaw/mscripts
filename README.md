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

Example 1
get latest free torrent(With assigned RSS source, specific classify), AKA 指定分類撕咬, --free mean free torrent only:

```bash
docker run --rm -v $(pwd)/mteam.json:/app/mteam.json -v $(pwd)/torrent/:/torrent/ mscripts mteam.py latest --free --output /torrent/
```

Example 2
get specific id 1026806 torrent:

```bash
docker run --rm -v $(pwd)/mteam.json:/app/mteam.json -v $(pwd)/torrent/:/torrent/ mscripts mteam.py download --id 1026806 --output /torrent/
```

Example 3
get all classify search, without assigned RSS source, download all free torrent whatever it is (AKA 全面瘋狂撕咬):

```bash
docker run --rm -v $(pwd)/mteam.json:/app/mteam.json -v $(pwd)/torrent/:/torrent/ mscripts mteam.py search --output /torrent/
```

