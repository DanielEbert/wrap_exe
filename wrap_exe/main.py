from __future__ import annotations

from typing import Sequence
import argparse
import sys


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Wrap executable to add arguments, env variables, etc')
    parser.add_argument('--prefix', '-p', nargs='+', help='Prefix command line arguments')
    parser.add_argument('--suffix', '-s', nargs='+', help='Suffix command line arguments')
    parser.add_argument('--env', '-e', nargs='+', help='key:value environment variable(s)')
    parser.add_argument('--cwd', '-c', help='Current Working Directory')
    parser.add_argument('--tee', '-t', action='store_true', help='Copy stdout and stderr to socket')
    parser.add_argument('--socket_path', default='/tmp/wrap_exe_socket')

    if len(sys.argv) == 1:
        parser.print_help()
        exit(1)

    args = parser.parse_args()

    print(args)

    return 0
