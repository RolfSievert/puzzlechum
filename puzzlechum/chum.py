#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import argparse
from pathlib import Path

from .find_problems_root import find_problems_root
from .newproblem import new_problem, Template
from .runtest import run_and_test

def has_valid_problems_root() -> bool:
    cwd = Path.cwd()

    if not (cwd / '.chum').is_dir():
        return False
    if not (cwd / '.chum' / 'tests').is_dir():
        return False
    if not (cwd / '.chum' / 'benchmarks').is_dir():
        return False

    return True

def create_problems_root() -> None:
    cwd = Path.cwd()

    if not (cwd / '.chum').is_dir():
        (cwd / '.chum').mkdir()
    if not (cwd / '.chum' / 'tests').is_dir():
        (cwd / '.chum' / 'tests').mkdir()
    if not (cwd / '.chum' / 'benchmarks').is_dir():
        (cwd / '.chum' / 'benchmarks').mkdir()

def set_last_problem(problems_root: Path, problem_name: str) -> None:
    last_path = problems_root / '.chum' / 'last_problem'

    with open(last_path, 'w') as file:
        file.write(problem_name)

def last_problem(problems_root: Path) -> str|None:
    last_path = problems_root / '.chum' / 'last_problem'

    with open(last_path, 'r') as file:
        problem_name = file.read().strip()

    return problem_name

def build_parser(subparsers) -> None:
    subparsers.add_parser(
        'init',
        help='Create a problems root. Do so somewhere in any parent above the folder where your problems are')

    new_parser = subparsers.add_parser(
        'new',
        help='Create a new problem. Downloads automatically if it is a kattis problem ID')

    new_parser.add_argument(
        'problem_name',
        type=str,
        help='Kattis problem ID, check the url after \'problems/\'')
    new_parser.add_argument(
        '--template',
        choices=list(t.value for t in Template),
        default=None,
        help='what template to use, must exist in \'templates/\' folder')

    test_parser = subparsers.add_parser(
        'test',
        help='Test one of your solutions')

    test_parser.add_argument('problem_name', nargs='?', default=None, help='defaults to last problem used with command `new` or `test`')
    test_parser.add_argument('-n', '--no-cleanup', action='store_true', help="leave compilation and output files in 'chum_output/'")

    exclusive_group = test_parser.add_mutually_exclusive_group(required=False)
    exclusive_group.add_argument('-b', '--benchmark', action='store_true', help='print minimal time execution benchmarks using hyperfine')
    exclusive_group.add_argument('-a', '--benchmark-average', action='store_true', help='print average time execution benchmarks using hyperfine')

def main():
    parser = argparse.ArgumentParser(
        prog='chum',
        description='A tool for downloading and testing programming problems')
    subparsers = parser.add_subparsers(dest='command', required=True, help='Subcommands')

    build_parser(subparsers)
    args = parser.parse_args()

    if args.command == 'init':
        if has_valid_problems_root():
            print('Problems root is already initialized, go solve your problems!')
        else:
            create_problems_root()
            print('Problems root initialized, go solve your problems!')
            print()
            print('Remember:')
            print(f" - You can override the default solution templates by adding templates to '{Path.cwd() / '.chumtemplates/'}'")
        exit()

    problems_root = find_problems_root()
    if problems_root == None:
        print('ERROR: not a problems folder')
        print(' - run `chum init` to set a problems root')
        print()
        parser.print_help()
        exit(1)

    if args.command == 'new':
        template = None
        if args.template:
            template = Template(args.template)

        new_problem(problems_root, args.problem_name, template)
        set_last_problem(problems_root, args.problem_name)
    elif args.command == 'test':
        problem_name = args.problem_name
        if (problem_name is None):
            problem_name = last_problem(problems_root)
            if (problem_name is None):
                print('Missing argument: problem name')
                exit()
        else:
            set_last_problem(problems_root, problem_name)
        run_and_test(problems_root, problem_name, args.benchmark, args.benchmark_average, not args.no_cleanup)

if __name__ == '__main__':
    main()
