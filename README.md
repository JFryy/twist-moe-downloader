# Twist.Moe Downloader Helper

### Description
[![Build Status](https://travis-ci.org/JFryy/twist-moe-downloader.svg?branch=master)](https://travis-ci.org/JFryy/twist-moe-downloader) [![Downloads](https://pepy.tech/badge/twistdl)](https://pepy.tech/project/twistdl) 
![](examples/tty.gif) [![PyPI version](https://badge.fury.io/py/twistdl.svg)](https://badge.fury.io/py/twistdl)
This is a python cli tool and client for downloading video contents of series available on the website `twist.moe` locally.
To download a particular series, use the series's url like so `https://twist.moe/a/made-in-abyss` and to search for
a series enter a part of its name as found in a twist.moe's url string like `fate`.

Additional to the commandline interface this package also provides a pure python object oriented api for `twist.moe`.

Remember to support twist.moe with donations if you can, as they do a great job of operating their site!

### Installation
The scripts has been tested against python 2.7 and 3.7.

`pip install twistdl --user`

And you're done! You can started with something as simple as the command below.

`$ twistdl fate`

### Running the script

```bash
$ twistdl

usage: twistdl [title] [--range RANGE][--directory DIRECTORY] [-h]

Twist-dl is a small python tool for downloading video contents of series
available on the website twist.moe locally! To download a list of particular
series, enter a keyword of the series name. i.e. 'code geass' can be found by
simply entering 'code'.

positional arguments:
  title                 To download a particular series, use the series's url
                        like so "https://twist.moe/a/made-in-abyss" and to
                        search for a series enter a part of its name as found
                        in a twist.moe's url string like "fate".

optional arguments:
  -h, --help            show this help message and exit
  --directory DIRECTORY
                        Directory path to save downloaded contents
  --range RANGE         Range of episodes to download. i.e. --range=1-24 or
                        for a single episode --range=1

```

### Example Usage:

#### Search and download with CLI

Download by passing the series title as found from search. Not specifying a range with `--range` will prompt you with
to a enter range. If no range is entrered all episodes will be downloaded.
```bash
$ twistdl code
? Anime(s) found. Please choose a series to download:  Code Geass: Hangyaku no Lelouch R2
Episode selection between 1-25. To download a range enter "1-5", for a single episode enter "5" or leave it empty press "Enter" to download all episodes.
Input: 1-5
anime/code-geass-hangyaku-no-lelouch-r2/Code Geass: Hangyaku no Lelouch R2 - 01.mp4:   6%|▋         | 30/478 [00:12<03:13,  2.32MB/s]
...
```

#### Search and download with API

```python
from pathlib import Path
from twistdl import TwistDL

# Credentials can be supplied incase they expire. (good luck acquiring them though....)
client = TwistDL()
animes = client.search_animes(title='code geass')

for anime in animes:
    for episode in anime.episodes:
        file = Path(f'anime/{anime.slug_name}/{anime.title} - {episode.number}')
        print(f'{anime.title} - {episode.number}')
        file.parent.mkdir(exist_ok=True, parents=True)
        episode.download(file)
```

##### Disclaimer
Downloading copyright videos may be illegal in your country. This tool is for educational purposes only.

##### Additional Notes
Special thanks to Nachtalb for refactoring this codebase to be modularized and include a client api.
