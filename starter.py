#!/usr/bin/env python3
import argparse
import os
import re
import sys
import signal


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        pass


SERVER_CONFIG_FILE = 'config/environments/development/server.json'
DATABASE_CONFIG_FILE = 'config/environments/development/database.json'
parser = ArgumentParser(description='Start strapi with port set argument - only for development mode')
old_port = None
old_db = {}


def main():
    parser.add_argument('-p', '--port', type=int, help='Strapi server port', required=False)
    parser.add_argument('--dbusername', type=str, help='Strapi database username', required=False)
    parser.add_argument('--dbpassword', type=str, help='Strapi database password', required=False)
    args = parser.parse_args()
    strapi_args = ' '.join(['dev'] + sys.argv[1:])
    strapi_args = re.sub('(--port=[0-9]+|-p [0-9]+) ?', '', strapi_args)
    strapi_args = re.sub('(--dbusername=.* |--dbusername=.*$)', '', strapi_args)
    strapi_args = re.sub('(--dbpassword=.* |--dbpassword=.*$)', '', strapi_args)
    if not os.path.isfile(os.path.realpath(SERVER_CONFIG_FILE)):
        print("WARNING: Not found {}".format(SERVER_CONFIG_FILE))
    else:
        if args.port:
            change_port(args.port)
        if args.dbusername:
            change_db('username', args.dbusername)
        if args.dbpassword:
            change_db('password', args.dbpassword)
    cmd = 'strapi {}'.format(strapi_args)
    signal.signal(signal.SIGINT, signal_handler)
    os.system(cmd)
    restore()


def change_port(new_port):
    global old_port
    with open(SERVER_CONFIG_FILE) as cfile:
        config = cfile.read()
    match = re.search('["\']port["\']: *[0-9]+', config)
    if match:
        line = match.group(0)
        old_port = re.search('[0-9]+', line).group(0)
        new_line = line.replace(old_port, str(new_port))
        with open(SERVER_CONFIG_FILE, 'w') as cfile:
            cfile.write(config.replace(line, new_line))
        print("INFO: Change port from {} to {}".format(old_port, new_port))


def change_db(key, value):
    with open(DATABASE_CONFIG_FILE) as cfile:
        config = cfile.read()
    match = re.search('["\']{}["\']: *["\'].*["\']'.format(key), config)
    if match:
        line = match.group(0)
        old_db[key] = re.search(': *["\'].*["\']', line).group(0)
        new_line = line.replace(old_db[key], ': "{}"'.format(value))
        old_db[key] = re.sub(': *', '', old_db[key]).strip("\"'")
        with open(DATABASE_CONFIG_FILE, 'w') as cfile:
            cfile.write(config.replace(line, new_line))
        print("INFO: Change db {} from {} to {}".format(key, old_db[key], value))


def signal_handler(sig, frame):
    restore()
    exit()


def restore():
    if not os.path.isfile(os.path.realpath(SERVER_CONFIG_FILE)):
        return
    if old_port:
        change_port(old_port)
    for key, value in old_db.items():
        change_db(key, value)


if __name__ == '__main__':
    main()
