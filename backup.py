import os
import sys
import glob
import shutil
import hashlib
import argparse
import datetime
import subprocess

from PIL import Image

__version__ = '1.0'
__description__ = ''
__epilog__ = 'Report bugs to <yehcj.tw@gmail.com>'

class Video():
    def __init__(self):
        self.extension = ['mp4', 'MP4', 'mov', 'MOV']
        self.cmd = 'ffprobe -v quiet -select_streams v:0 -show_entries stream_tags=creation_time -of default=noprint_wrappers=1:nokey=1 \"{file}\"'

    def valid(self, name):
        return len(name) > 4 and name[-3:] in self.extension

    def timestamp(self, video):
        ret = None
        try:
            result = subprocess.check_output(self.cmd.format(
                file=os.path.join(video['path'], video['name']),
                shell=True
            ))
            ret = result.decode()[:10]
        except:
            print(video)
        return ret

class Photo():
    def __init__(self):
        self.extension = ['JPG', 'jpg', 'HEIC']
        self.cmd = 'ffprobe -v quiet -select_streams v:0 -show_entries stream_tags=creation_time -of default=noprint_wrappers=1:nokey=1 \"{file}\"'

    def valid(self, name):
        return len(name) > 4 and (name[-3:] in self.extension or name[-4:] in self.extension)

    def timestamp(self, photo):
        ret = None
        exif = None

        try:
            exif = Image.open(os.path.join(photo['path'], photo['name'])).getexif()

            # Exif.Image.DateTimeOriginal
            if 36867 in exif:
                ret = datetime.strptime(exif[36867], '%Y:%m:%d %H:%M:%S').strftime('%Y-%m-%d')
            # Exif.Image.DateTime
            elif 306 in exif:
                ret = datetime.strptime(exif[306], '%Y:%m:%d %H:%M:%S').strftime('%Y-%m-%d')
        except:
            print(photo)
            print(exif)

        return ret

class API():
    def __init__(self):
        self.video = Video()
        self.photo = Photo()
        self.files = []
        self.days = {}
        self.command = ['mdls', '-name', 'kMDItemContentCreationDate']
        self.stat = {
            'all': 0,
            'valid': 0,
            'duplicate': 0,
            'copy': 0
        }

    def load(self, src):
        files = []
        for target in src:
            files += glob.glob(target)

        for file in files:
            name = os.path.basename(file)
            path = os.path.abspath(os.path.join(file, os.pardir))

            if self.video.valid(name):
                self.files.append({
                    'type': 'video',
                    'name': name,
                    'path': path
                })
            elif self.photo.valid(name):
                self.files.append({
                    'type': 'photo',
                    'name': name,
                    'path': path
                })

        self.stat['all'] = len(files)

    def timestamp(self, file):
        target = os.path.join(file['path'], file['name'])
        output = subprocess.check_output(self.command + [target])
        output = output.decode().split(' = ')[1]
        output = output.split(' ')
        return output[0]

    def sort(self):
        for file in self.files:
            # day = getattr(self, file['type']).timestamp(file)
            day = self.timestamp(file)

            if day == None:
                continue
            elif day not in self.days.keys():
                self.days[day] = []

            self.days[day].append(file)
            self.stat['valid'] += 1

    def copy(self, out):
        jobs = []

        for day in self.days:
            path = os.path.join(out, day)

            if not os.path.exists(path):
                os.mkdir(path)

            for file in self.days[day]:
                src = os.path.join(file['path'], file['name'])
                dst = os.path.join(path, file['name'])

                if os.path.isfile(dst):
                    src_md5 = hashlib.md5(open(src, 'rb').read()).hexdigest()
                    dst_md5 = hashlib.md5(open(dst, 'rb').read()).hexdigest()

                    if src_md5 == dst_md5:
                        self.stat['duplicate'] += 1
                    else:
                        print('Error: %s > %s' % (src, dst))
                else:
                    jobs.append({ 'src': src, 'dst': dst })

        self.stat['copy'] = len(jobs)
        for job in jobs:
            shutil.copyfile(job['src'], job['dst'])

    def clear(self):
        self.files = []

def main():
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog=__epilog__
    )
    parser.add_argument('src', type=str, nargs='+', help='')
    parser.add_argument('dst', type=str, help='')
    parser.add_argument(
        '-v', '-V', '--version',
        action='version',
        help='show version of program',
        version='v{}'.format(__version__)
    )
    args = parser.parse_args(sys.argv[1:])

    api = API()
    api.load(args.src)
    api.sort()
    api.copy(args.dst)

    print(api.stat)

if __name__ == '__main__':
    main()