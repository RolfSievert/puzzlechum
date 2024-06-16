#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from pathlib import Path
import argparse
import re
import pyperclip

def parse_args():
    parser = argparse.ArgumentParser(
        prog='toclipboard',
        description='Replace includes in given file (and recursive ones) and copy it to clipboard for quick uploads. NOTE: Files using the same local includes are not supported!')

    parser.add_argument('file_path', type=Path, help='path to file to upload')

    return parser.parse_args()

def cpp_content(content, file_path):
    includes = re.findall('#include ".*"', content)
    for i in includes:
        include_str = re.search('(?<=").*(?=")', i)[0]
        include_path = file_path.parent / include_str

        if include_path.is_file():
            include_content = ''
            with open(include_path, 'r') as f:
                include_content = f.read()

            # clean string from pragma
            include_content = include_content.replace('#pragma once', '')

            # fetch recursive includes
            include_content = cpp_content(include_content, include_path);

            content = content.replace(i, include_content)

    return content

if __name__ == '__main__':
    args = parse_args()

    if not args.file_path.is_file():
        raise(f'{str(args.file_path)} does not exist.')

    content = ''
    with open(args.file_path, 'r') as f:
        content = f.read()

    if args.file_path.suffix == '.cpp':
        content = cpp_content(content, args.file_path)
    else:
        raise(f"Support of type '{args.file_path.suffix}' is not implemented")

    pyperclip.copy(content)
