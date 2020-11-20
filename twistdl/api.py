import requests
import six
from tqdm import tqdm

from pathlib2 import Path
from six.moves import filter
from six.moves import map
from twistdl import Anime
from twistdl import Source

try:
    from pathlib import Path as py3Path
except ImportError:
    py3Path = None


class TwistDL(object):
    base_url = 'https://twist.moe'
    api_path = 'api'

    default_api_token = '1rj2vRtegS8Y60B3w3qNZm5T2Q0TN2NR'
    default_source_key = 'LXgIVP&PorO68Rq7dTx8N^lP!Fa5sGJ^*XK'

    _animes = None

    def __init__(self, api_token=None, source_key=None):
        self.api_token = api_token or self.default_api_token
        self.source_key = source_key or self.default_source_key

        self.headers = {'x-access-token': self.api_token}

    def _request(self, endpoint, headers=None, data=None):
        data = data or {}
        headers = headers or {}

        built_url = '{}/{}/{}'.format(self.base_url, self.api_path, endpoint)

        headers.update({'x-access-token': self.api_token})

        response = requests.get(url=built_url, data=data, headers=headers)
        response.raise_for_status()

        return response.json(), built_url

    def fetch_animes(self):
        response_data, url = self._request(endpoint='anime')
        self._animes = list(map(lambda anime: Anime.de_json(anime, (url, {}), self), response_data))

    @property
    def animes(self):
        if not self._animes:
            self.fetch_animes()
        return self._animes

    def anime_sources(self, anime):
        endpoint = 'anime/{}/sources'.format(anime.slug.slug)

        response_data, url = self._request(endpoint=endpoint)
        return list(map(lambda source: Source.de_json(source, (url, {}), self), response_data))

    def search_animes(self, title=None, slug=None):
        result = []

        title = (title or '').lower()
        slug = (slug or '').lower()

        for anime in self.animes:
            if title and title in anime.title.lower():
                result.append(anime)
                continue
            if slug and slug in anime.slug.slug:
                result.append(anime)
        return result

    def get_anime_by(self, field, value):
        return next(iter(filter(lambda anime: getattr(anime, field) == value, self.animes)), None)

    def download_stream(self, url, file, chunk_size=1024):
        """Download url to file and get download progress through generator

        Args:
            file: Can either be a pathlike obj, str or filelike obj

        Yield:
            Tuple like (chunks downloaded, total chunks)
        """
        file_str = str(file)
        if isinstance(file, Path) or (file is not None and isinstance(file, py3Path)):
            pass
        elif isinstance(file, six.string_types):
            file = Path(file)
        elif hasattr(file, 'write'):
            file_obj = file
        else:
            raise TypeError('File is neither pathlike, filelike or a sring')

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'Referer': self.base_url
        }

        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(file, 'wb') as f:
                pbar = tqdm(total=int(r.headers['Content-Length']), desc=file_str.split("/")[-1])
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

    def download(self, url, file):
        list(self.download_stream(url, file))

