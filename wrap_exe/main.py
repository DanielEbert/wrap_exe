from __future__ import annotations

from typing import Sequence
import argparse
import sys
import os
import shutil
import hashlib
import stat
import re


def is_wrapped(path: str) -> bool:
    with open(path, errors='ignore') as f:
        content = f.read()
    ret = 'fuzz_wrap generated' in content

    print(f'{path} is {"not " if not ret else ""}wrapped already.')

    return ret


def get_original_executable_path_in_wrapped_file(path: str) -> str:
    orig_exe_regex = re.compile(r'# fuzz_wrap generated: (?P<orig>.*)')

    with open(path) as f:
        lines = [line.rstrip() for line in f]

    for line in lines:
        match = orig_exe_regex.match(line)
        if match:
            return match.group('orig')

    raise Exception(f'No fuzz_wrap generated line in {path}')


def get_file_hash(path: str) -> str:
    with open(path, 'rb') as f:
        content = f.read()

    return hashlib.sha1(content, usedforsecurity=False).hexdigest()


def get_original_executable_path(executable_path: str) -> str:
    fuzz_wrap_folder = '/tmp/wrapped_files/'

    try:
        os.mkdir(fuzz_wrap_folder)
    except Exception:
        ...

    new_path = os.path.join(fuzz_wrap_folder, f'{os.path.basename(executable_path)}_{get_file_hash(executable_path)}')
    shutil.move(executable_path, new_path)
    return new_path


def wrapper_code(original_executable_path: str, socket_path: str, prefix: list[str], suffix: list[str]) -> str:
    return f'''\
#!/usr/bin/env python3

# fuzz_wrap generated: {original_executable_path}

import os
import socket
import sys

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

try:
    sock.connect("{socket_path}")
    os.dup2(sock.fileno(), sys.stdout.fileno())
    os.dup2(sock.fileno(), sys.stderr.fileno())
except Exception as e:
    print(f"Failed to connect to socket {socket_path}: {{e}}")

calling_args = sys.argv
calling_args[0] = "{original_executable_path}"

program_args = {prefix} + calling_args + {suffix}
program = program_args[0]
env_vars = os.environ

print(f'running {{program_args}}')

os.execve(program, program_args, env_vars)
'''


def create_exe(executable_path: str, code: str) -> None:
    with open(executable_path, 'w') as f:
        f.write(code)

    os.chmod(executable_path, os.stat(executable_path).st_mode | stat.S_IEXEC)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Wrap an executable to add arguments, environment variables, etc.')
    parser.add_argument('--prefix', '-p', nargs='+', help='Prefix command line arguments')
    parser.add_argument('--suffix', '-s', nargs='+', help='Suffix command line arguments')
    parser.add_argument('--env', nargs='+', help='key:value environment variable(s)')
    parser.add_argument('--cwd', '-c', help='Current Working Directory')
    parser.add_argument('--tee', '-t', action='store_true', help='Copy stdout and stderr to socket')
    parser.add_argument('--socket_path', default='/tmp/wrap_exe_socket')
    parser.add_argument('--executable_path', '-e', required=True, help='The executable to wrap.')
    # TODO: option to run command in bash? maybe that can be done with prefix bash

    if len(sys.argv) == 1:
        parser.print_help()
        exit(1)

    args = parser.parse_args(argv)
    args.executable_path = os.path.abspath(args.executable_path)
    args.prefix = args.prefix or []
    args.suffix = args.suffix or []

    assert os.path.isfile(args.executable_path)

    if is_wrapped(args.executable_path):
        original_executable_path = get_original_executable_path_in_wrapped_file(args.executable_path)
    else:
        original_executable_path = get_original_executable_path(args.executable_path)

    code = wrapper_code(original_executable_path, args.socket_path, args.prefix, args.suffix)

    create_exe(args.executable_path, code)

    return 0
