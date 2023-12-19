# change_ip.py
import argparse
import fileinput
import re

def replace_ip(filename, new_ip):
    with fileinput.input(files=(filename,), inplace=True) as f:
        for line in f:
            if line.strip().startswith('SERVER_IP'):
                line = re.sub(r"'(.*?)'", f"'{new_ip}'", line)
            print(line, end='')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Change SERVER_IP in settings.py.')
    parser.add_argument('-ip', '--server_ip', required=True, help='New server IP')
    args = parser.parse_args()

    replace_ip('./web_toker_django/settings.py', args.server_ip)
