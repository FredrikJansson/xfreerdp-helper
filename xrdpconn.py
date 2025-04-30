#!/usr/bin/env python3

from shlex import quote
from argparse import ArgumentParser
from tempfile import mkdtemp
import subprocess


class XFreeRDPWrapper:
    conn_host: str = ''

    configs = {}

    def __init__(self, ip: str, port: int = None):
        conn_host = ip
        if port is not None:
            conn_host += ':' + str(port)
        self.conn_host = quote(conn_host)

    def add_user(self, user: str) -> None:
        self.configs['user'] = f'/u:{user}'

    def add_pass(self, pw: str) -> None:
        self.configs['pass'] = f'/p:{pw}'

    def add_share(self, host_path: str, dest_share: str = 'share', add_num: bool = False) -> None:
        if self.configs.get('share', None) is None:
            self.configs['share'] = list()
        dest_share_name = dest_share
        if add_num is True:
            dest_share_name += str(len(self.configs['share']) + 1)
        self.configs['share'].append(
            f'/drive:{dest_share_name},{host_path}')

    def add_auto_share(self) -> None:
        pth = mkdtemp(prefix=self.conn_host + '-xrdpconn-')
        print('[!] Will mount temporary folder:', pth)
        print('\tIT WILL NOT BE REMOVED BY THIS SCRIPT.')
        self.add_share(pth, 'tmp_share')

    def add_dynamic_resolution(self) -> None:
        self.configs['dyn_res'] = '/dynamic-resolution'

    def clean_params(self) -> list:
        """
            Escapes parameters. Depends on type
            - str -> adds quote(str)
            - list -> loops list and adds quote(list[i])
        """
        params = []
        for v in self.configs.values():
            if type(v) is type(str()):
                params.append(quote(v))
            elif type(v) is type(list()):
                for d in v:
                    params.append(quote(d))
            else:
                print('[-] Invalid parameter:', v)
        return params

    def connect(self) -> int:
        # escape items
        params = self.clean_params()
        cmd = u' '.join(['xfreerdp', quote('/v:' + self.conn_host)])

        print(f'[+] Connecting to {self.conn_host}.')
        for v in params:
            if type(v) is type(str()):
                cmd = u' '.join([cmd, v])
                print('  [+] Launched with param:', v)
            elif type(v) is type(list()):
                for i in v:
                    cmd = u' '.join([cmd, i])
                    print('  [+] Launched with param:', i)
        print()
        op = subprocess.run(cmd, shell=True)
        return op.returncode


def main():
    parser = ArgumentParser(description='Helps me with xfreerdp')
    parser.add_argument('ip', help='IP to connect to')
    parser.add_argument('--port', help='Port to connect to', default=None, type=int)
    parser.add_argument('-u', '--user', help='Connecting user', type=str)
    parser.add_argument('-p', '--pass', help='Password for user, pref dont use', type=str, dest='pw')
    parser.add_argument('-dr', '--dynamic-resolution', help='Enables dynamic reoslution', action='store_true')
    parser.add_argument('-d', '--drive', help='Mounts a shared drive.', type=str, action='append')
    parser.add_argument('-da', '--drive-auto', help='Creates a temp folder and mounts it. /tmp/xrdpconn/', action='store_true')

    parsed = parser.parse_args()
    rdp = XFreeRDPWrapper(parsed.ip, parsed.port)

    if parsed.user:
        rdp.add_user(parsed.user)
    if parsed.pw:
        rdp.add_pass(parsed.pw)
    if parsed.dynamic_resolution:
        rdp.add_dynamic_resolution()
    if parsed.drive:
        for d in parsed.drive:
            rdp.add_share(d)
    if parsed.drive_auto:
        rdp.add_auto_share()

    return rdp.connect()


if __name__ == '__main__':
    exit(main())
