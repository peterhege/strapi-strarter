#!/usr/bin/env python3
import argparse
import os
import re
import sys
import signal


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        pass


CONFIG_FILE = 'config/environments/development/server.json'
parser = ArgumentParser(description='Start strapi with port set argument - only for development mode')
old_port = None


def main():
    parser.add_argument('-p', '--port', type=int, help='Strapi server port', required=False)
    args = parser.parse_args()
    strapi_args = ' '.join(['dev'] + sys.argv[1:])
    strapi_args = re.sub('(--port=[0-9]+|-p [0-9]+) ?', '', strapi_args)
    print(strapi_args)
    if args.port:
        change_port(args.port)
    cmd = 'strapi {}'.format(strapi_args)
    signal.signal(signal.SIGINT, signal_handler)
    os.system(cmd)
    if old_port:
        change_port(old_port)


def change_port(new_port):
    global old_port
    if not os.path.isfile(os.path.realpath(CONFIG_FILE)):
        print("WARNING: Not found {}".format(CONFIG_FILE))
        return None
    with open(CONFIG_FILE) as cfile:
        config = cfile.read()
    match = re.search('["\']port["\']: *[0-9]+', config)
    if match:
        line = match.group(0)
        old_port = re.search('[0-9]+', line).group(0)
        new_line = line.replace(old_port, str(new_port))
        with open(CONFIG_FILE, 'w') as cfile:
            cfile.write(config.replace(line, new_line))
        print("INFO: Change port from {} to {}".format(old_port, new_port))
    return old_port


def signal_handler():
    if old_port:
        change_port(old_port)
    exit()


if __name__ == '__main__':
    main()
