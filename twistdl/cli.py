import re
import sys

from PyInquirer import prompt
from argparse import ArgumentParser
from pathlib2 import Path
from six.moves import filter
from six.moves import input
from six.moves import map
from six.moves import range
from tqdm import tqdm
from twistdl import TwistDL


class TwistDLCLI(object):

    def __init__(self):
        self.client = TwistDL()
        self.base_path = Path('anime')

    def main(self):
        user_input = self.parse_args()
        title, search_for_anime = self.parse_title(user_input.title)

        if search_for_anime:
            anime = self.choose_anime(title)
        else:
            anime = self.client.get_anime_by('slug_name', title)

        if not anime:
            print('Error: It looks like the title you entered is not found.')
            exit(1)

        episode_range = user_input.range
        if not episode_range:
            episode_range = self.choose_range(anime)

        if not episode_range:
            first_episode, last_episode = anime.first_episode.number, anime.last_episode.number
        else:
            first_episode, last_episode = self.validate_range(episode_range, anime)

        sources = self.get_sources_from_range(first_episode, last_episode, anime)

        if not user_input.directory:
            path = self.get_path(anime)
        else:
            path = Path(user_input.directory)
            path.mkdir(parents=True, exist_ok=True)

        self.download_files(path, sources)

    def get_path(self, anime):
        path = Path('anime') / anime.slug_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def download_files(self, path, sources):
        for source in sources:
            filename = path / '{} - {:0>2}.mp4'.format(source.anime.title, source.number).replace('/', '-')
            downloader = self.client.download_stream(source.url, filename, 1024 * 1024)

    def parse_title(self, title):
        url_match = re.findall('twist.moe/a/([a-z0-9-]+)', title)
        if url_match:
            return url_match[0], False
        return title, True

    def choose_anime(self, query):
        animes = self.client.search_animes(title=query, slug=query)
        if not animes:
            return None

        questions = [
            {
                'type': 'list',
                'name': 'title',
                'message': 'Anime(s) found. Please choose a series to download:',
                'choices': [{'name': anime.title, 'value': anime} for anime in animes]
            }
        ]
        answers = prompt(questions)
        if 'title' not in answers:
            exit()
        return answers['title']

    def choose_range(self, anime):
        episode_begin, episode_end = anime.first_episode.number, anime.last_episode.number
        episode_range = input(
            'Episode selection between {}-{}. To download a range enter "1-5", for a single episode enter "5" or leave '
            'it empty press "Enter" to download all episodes. \nInput: '.format(episode_begin, episode_end))
        return episode_range

    def validate_range(self, episode_range, anime):
        if isinstance(episode_range, int) or '-' not in episode_range:
            episode_number = self.validate_episode(episode_range, anime)
            return episode_number, episode_number
        else:
            try:
                episode_begin, episode_end = episode_range.split('-')
            except ValueError:
                print('"{}" does not match the range pattern "XX-YY"'.format(episode_range))
                exit(1)

            episode_begin = self.validate_episode(episode_begin, anime)
            episode_end = self.validate_episode(episode_end, anime)
            return episode_begin, episode_end

    def validate_episode(self, episode, anime):
        try:
            episode = int(episode)
            if not anime.episode(episode):
                print('"{}" has no episode "{}"'.format(anime.title, episode))
                exit(1)
            return episode
        except ValueError:
            print('Episode range "{}" invalid'.format(episode))
            exit(1)

    def get_sources_from_range(self, first_episode, last_episode, anime):
        episodes = list(range(first_episode, last_episode + 1))
        return list(filter(lambda source: source.number in episodes, anime.sources))

    def parse_args(self):
        usage = 'python cli.py [title] [--range RANGE][--directory DIRECTORY] [-h]'
        parser = ArgumentParser(
            description='Twist-dl is a small python tool for downloading video contents of series available on the website '
                        'twist.moe locally! To download a list of particular series, enter a keyword of the series name. '
                        'i.e. "code geass" can be found by simply entering "code".',
            usage=usage
        )
        parser.add_argument(
            'title',
            help='To download a particular series, use the series\'s url like so "https://twist.moe/a/made-in-abyss" '
                 'and to search for a series enter a part of its name as found in a twist.moe\'s url string like "fate".'
        )
        parser.add_argument(
            '--directory',
            dest='directory',
            help='Directory path to save downloaded contents',
            required=False,
            default=None
        )
        parser.add_argument(
            '--range',
            dest='range',
            help='Range of episodes to download. i.e. --range=1-24 or for a single episode --range=1',
            required=False,
            default=''
        )

        if len(sys.argv) < 2:
            parser.print_help()
            exit(1)

        return parser.parse_args()


def main():
    try:
        cli = TwistDLCLI()
        cli.main()
    except (KeyboardInterrupt, EOFError):
        print('Exit')

