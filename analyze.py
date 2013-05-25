#!/usr/bin/python

import sys
import bz2
import os
import json

import config

def d(*msg):
    print >>sys.stderr, ' '.join(map(str, msg))

def get_path(dist, section, arch):
    return os.path.join(config.DOWNLOAD_DIR, dist, section,
                        'binary-%s' % arch, 'Packages.bz2')

def read_packages(f):
    data = {}
    description = None

    for line in f:
        if len(data) == 0 and (line.strip() == '' or line[0] == ' '):
            continue

        if description is not None:
            if line[0] == ' ':
                line = line.strip()
                if line == '.':
                    description.append('')
                else:
                    description.append(line)
                continue

            else:
                data['LongDescription'] = '\n'.join(description)
                description = None

        line = line.strip()
        if line == '':
            yield data
            data = {}
            description = None
            continue

        p = line.split(': ')
        field = p[0]
        value = ': '.join(p[1:])

        if field == 'Description':
            description = []

        data[field] = value

def analyze(dist, section, arch):
    path = get_path(dist, section, arch)

    f = bz2.BZ2File(path)

    count = 0
    size = 0L

    for package in read_packages(f):
        count += 1
        size += long(package['Size'])

    return dict(count=count,
                size=size)

def collect_data():
    total = len(config.DISTS) * len(config.SECTIONS) * len(config.ARCHS)
    index = 0

    sizes = {}
    packages = {}

    for arch in config.ARCHS:
        sizes[arch] = {}
        packages[arch] = {}

        for dist in config.DISTS:
            sizes[arch][dist] = {}
            packages[arch][dist] = {}

            for section in config.SECTIONS:
                data = analyze(dist, section, arch)

                sizes[arch][dist][section] = data['size']
                packages[arch][dist][section] = data['count']

                index += 1
                d('%s of %s: %s %s %s' % (index, total,
                                          dist, section, arch))

    return dict(sizes=sizes,
                packages=packages)

def main():
    data = collect_data()
    print json.dumps(data)

if __name__ == '__main__':
    main()

