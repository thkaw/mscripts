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
__log__ = '{id}: {discount}'

class MTeam():
    def __init__(self):
        parser = argparse.ArgumentParser(
            description=__description__,
            epilog=__epilog__
        )
        parser.add_argument('mode', type=str, choices={ 'latest', 'free' }, default='free')
        args = parser.parse_args(sys.argv[1:])

        getattr(self, args.mode)()

    def load(self):
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

    def _latest(self, key, rss):
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
        args = parser.parse_args(sys.argv[2:])

        # auto using config as input
        if args.key == None or args.rss == None:
            config = self.load()
            args.key = config['key']
            args.rss = config['rss']
            args.output = config['output']

        for item in self._latest(args.key, args.rss):
            id = item['guid']['#text']
            detail = self.detail(args.key, id)

            if detail == None:
                continue

            print(__log__.format(id=id, discount=detail['status']['discount']))
            if 'FREE' == detail['status']['discount']:
                self.download(args.key, id, args.output)

    def download(self, key, id, output):
        headers = { 'x-api-key': key }
        payload = { 'id': id }

        try:
            time.sleep(random.randint(5, 10))
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
                        file = __torrent__.format(id=id)
                        if output != '':
                            file = os.path.join(output, file)

                        if not os.path.exists(file):
                            with open(file, 'wb') as fp:
                                fp.write(response.content)

        except Exception as e:
            print(str(e))

    def detail(self, key, id):
        payload = { 'id': id }
        headers = { 'x-api-key': key }
        try:
            time.sleep(random.randint(5, 10))
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

    def _free(self, key):
        headers = { 'x-api-key': key }
        payload = {
            'mode': 'adult',
            'pageNumber': 1,
            'pageSize': 25
        }

        try:
            time.sleep(random.randint(5, 10))
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

    def free(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--key', type=str, required=False, default=None)
        parser.add_argument('--output', type=str, default=None)
        args = parser.parse_args(sys.argv[2:])

        # auto using config as input
        if args.key == None or args.rss == None:
            config = self.load()
            args.key = config['key']
            args.output = config['output']

        items = self._free(args.key)

        for item in items:
            id = item['id']
            detail = self.detail(args.key, id)

            if detail == None:
                continue

            print(__log__.format(id=id, discount=detail['status']['discount']))
            if 'FREE' == detail['status']['discount']:
                self.download(args.key, id, args.output)

def main():
    mt = MTeam()

if __name__ == '__main__':
    main()