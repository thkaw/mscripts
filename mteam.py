import os
import sys
import json
import time
import random
import shutil
import argparse
import requests
import xmltodict

__version__ = '1.0'
__description__ = ''
__epilog__ = 'Report bugs to <yehcj.tw@gmail.com>'

__url__ = {
    'detail': 'https://api.m-team.cc/api/torrent/detail',
    'download': 'https://api.m-team.cc/api/torrent/genDlToken',
    'free': 'https://api.m-team.cc/api/torrent/search'
}
__torrent__ = '{id}.torrent'
__synology__ = '{id}.torrent.loaded'
__log__ = '{id}: {discount}\n{name}'

class MTeam():
    def __init__(self):
        parser = argparse.ArgumentParser(
            description=__description__,
            epilog=__epilog__
        )
        parser.add_argument(
            'mode',
            type=str,
            choices={ 'latest', 'search', 'download' },
            default='search'
        )
        args = parser.parse_args(sys.argv[1:2])
        getattr(self, args.mode)()

    def load(self) -> dict:
        file = 'mteam.json'
        if os.path.exists(file):
            with open(file, 'r') as fp:
                config = json.load(fp)
            if config['key'] == '':
                print('missing key')
                exit()
            return config
        else:
            print('file to load config')
            exit()

    def _latest(self, key: str, rss: str) -> list[dict]:
        try:
            response = requests.get(rss, headers={ 'x-api-key': key })
            if response.status_code == 200:
                ret = xmltodict.parse(response.text, attr_prefix='')
                return ret['rss']['channel']['item']
            else:
                exit()
        except Exception as e:
            print(str(e))
            exit()

    def latest(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--key', type=str, required=False, default=None)
        parser.add_argument('--rss', type=str, required=False, default=None)
        parser.add_argument('--output', type=str, default=None)
        parser.add_argument('--free', action='store_true', default=False, help='')
        args = parser.parse_args(sys.argv[2:])

        # auto using config as input
        if args.key == None or args.rss == None:
            config = self.load()
            args.key = config['key']
            args.rss = config['rss']
            args.output = config['output']

        for item in self._latest(key=args.key, rss=args.rss):
            id = item['guid']
            detail = self.detail(key=args.key, id=id)

            if detail == None:
                continue
            print(__log__.format(
                id=id,
                discount=detail['status']['discount'],
                name=detail['name'])
            )
            if 'FREE' != detail['status']['discount']:
                print('skip')
                continue

            self._download(key=args.key, id=id, output=args.output)

    def _exist(self, path: str, id: str) -> bool:
        torrent = __torrent__.format(id=id)
        synology = __synology__.format(id=id)

        if path != '':
            torrent = os.path.join(path, torrent)
            synology = os.path.join(path, synology)

        return os.path.exists(torrent) or os.path.exists(synology)

    def _download(self, key: str, id: str, output: str) -> None:
        headers = { 'x-api-key': key }
        payload = { 'id': id }

        try:
            time.sleep(random.randint(2, 5))
            response = requests.request(
                'POST',
                __url__['download'],
                headers=headers,
                data=payload
            )
            if response.status_code == 200:
                response = response.json()
                if response['message'] == 'SUCCESS':
                    url = response['data'] + '&useHttps=true&type=ipv4'

                    response = requests.get(url)
                    if response.status_code == 200:
                        if not self._exist(output, id):
                            print('download')
                            torrent = __torrent__.format(id=id)
                            if output != '':
                                torrent = os.path.join(output, torrent)
                            with open(torrent, 'wb') as fp:
                                fp.write(response.content)
                        else:
                            print('exist')
                    else:
                        print('download fail')
            else:
                print('request fail')

        except Exception as e:
            print(str(e))

    def download(self) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument('--id', type=str, nargs='+', required=True, default=None)
        parser.add_argument('--key', type=str, required=False, default=None)
        parser.add_argument('--output', type=str, default=None)
        args = parser.parse_args(sys.argv[2:])

        # auto using config as input
        if args.key == None:
            config = self.load()
            args.key = config['key']
            args.output = config['output']

        for id in args.id:
            print(id)
            self._download(key=args.key, id=id, output=args.output)

    def detail(self, key: str, id: str) -> dict:
        payload = { 'id': id }
        headers = { 'x-api-key': key }
        try:
            time.sleep(random.randint(2, 5))
            response = requests.request(
                'POST',
                __url__['detail'],
                headers=headers,
                data=payload
            )
            if response.status_code == 200:
                ret = response.json()
                if ret['message'] == 'SUCCESS':
                    return ret['data']
                else:
                    # post error
                    pass
            else:
                # network error
                pass
        except Exception as e:
            print(str(e))

        return None

    def _search(
            self,
            key: str,
            mode: str,
            free: bool,
            index: int,
            size: int
        ) -> list[dict]:
        headers = { 'x-api-key': key }
        payload = {
            'mode': mode,
            'pageNumber': index,
            'pageSize': size
        }
        if free:
            payload['discount'] = 'FREE'

        try:
            time.sleep(random.randint(2, 5))
            response = requests.request(
                'POST',
                __url__['free'],
                headers=headers,
                json=payload
            )
            if response.status_code == 200:
                return response.json()['data']['data']
            else:
                exit()

        except Exception as e:
            print(str(e))
            exit()

    def search(self) -> None:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--key',
            type=str,
            required=False,
            default=None,
            help=''
        )
        parser.add_argument('--output', type=str, default=None, help='')
        parser.add_argument(
            '--mode',
            choices={
                'normal',
                'adult',
                'movie',
                'music',
                'tvshow',
                'waterfall',
                'rss',
                'rankings'
            },
            default='adult',
            help=''
        )
        parser.add_argument('--free', action='store_true', default=False, help='')
        parser.add_argument('--index', type=int, default=1, help='')
        parser.add_argument('--size', type=int, default=25, help='')
        args = parser.parse_args(sys.argv[2:])

        # auto using config as input
        if args.key == None or args.rss == None:
            config = self.load()
            args.key = config['key']
            args.output = config['output']

        items = self._search(
            key=args.key,
            mode=args.mode,
            free=args.free,
            index=args.index,
            size=args.size
        )

        for item in items:
            id = item['id']
            detail = self.detail(args.key, id)

            if detail == None:
                continue

            if 'FREE' != detail['status']['discount']:
                continue

            print(__log__.format(
                id=id,
                discount=detail['status']['discount'],
                name=detail['name']
            ))

            self._download(key=args.key, id=id, output=args.output)

def main():
    mt = MTeam()

if __name__ == '__main__':
    main()
