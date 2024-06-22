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
    'detail': 'https://kp.m-team.cc/api/torrent/detail',
    'download': 'https://kp.m-team.cc/api/torrent/genDlToken'
}
__torrent__ = '{id}.torrent'

class MTeam():
    def __init__(self, args):
        self._rss = args.rss
        self._key = args.key

    def items(self):
        try:
            response = requests.get(self._rss, headers={ 'x-api-key': self._key })
            if response.status_code == 200:
                ret = xmltodict.parse(response.text, attr_prefix='')
                return ret['rss']['channel']['item']
        except Exception as e:
            print(str(e))
        return []

    def download(self, id, output):
        headers = { 'x-api-key': self._key }
        payload = { 'id': id }
        try:
            time.sleep(random.randint(10, 15))
            response = requests.request(
                'POST',
                __url__['download'],
                headers=headers,
                data=payload
            )
            if response.status_code == 200:
                response = response.json()
                if response['message'] == 'SUCCESS':
                    url, para = response['data'].split('?')
                    url = url + '?useHttps=true&type=ipv4&' + para

                    response = requests.get(url)
                    if response.status_code == 200:
                        file = __torrent__.format(id=id)
                        if output != '':
                            file = os.path.join(output, file)
                        with open(file, 'wb') as fp:
                            fp.write(response.content)

        except Exception as e:
            print(str(e))

    def detail(self, id):
        payload = { 'id': id }
        headers = { 'x-api-key': self._key }
        try:
            time.sleep(random.randint(5, 10))
            response = requests.request(
                'POST',
                __url__['detail'],
                headers=headers,
                data=payload
            )
            ret = response.json()
            if ret['message'] == 'SUCCESS':
                return ret['data']
        except Exception as e:
            print(str(e))

        return None

def main():
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog=__epilog__
    )
    parser.add_argument('--rss', type=str, required=False, default='')
    parser.add_argument('--key', type=str, required=False, default='')
    parser.add_argument('--output', type=str, default='')
    parser.add_argument('--config', action='store_true', default=False)
    args = parser.parse_args()

    if args.config:
        with open('mteam.json', 'r') as fp:
            config = json.load(fp)
            args = argparse.Namespace(**config)

    if args.rss == '' or args.key == '':
        exit()

    mt = MTeam(args)
    for item in mt.items():
        id = item['guid']['#text']
        detail = mt.detail(id)

        print('{id}: {discount}'.format(
            id=id,
            discount=detail['status']['discount'])
        )

        if True or 'FREE' in detail['status']['discount']:
            mt.download(id, args.output)

if __name__ == '__main__':
    main()