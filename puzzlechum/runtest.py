#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
Runs tests on provided problem id.
"""

from enum import Enum
from io import TextIOWrapper
import subprocess
import json
import os

from pathlib import Path

RED = '\x1b[38;5;3m'
BLUE = '\x1b[38;5;2m'
GREEN = '\x1b[38;5;1m'
YELLOW = '\x1b[38;5;4m'
BOLD = '\x1b[1m'
DIMMED = '\x1b[2m'
ITALICS = '\x1b[3m'
NULL = '\x1b[0m'

ACCEPTED_SRC_SUFFIXES = [
    '.cpp',
    '.rs',
    '.py'
]

# call .resolve() to make symlinking of scripts possible
TMP_PATH = Path.cwd() / 'chum_output'

HYPERFINE = 'hyperfine'

CPP_COMPILE_FLAGS = 'g++ -g -O2 -std=gnu++17 -static -lrt -Wl,--whole-archive -lpthread -Wl,--no-whole-archive'
RUST_COMPILE_FLAGS = 'rustc --crate-type bin --edition=2018'
PYTHON_COMPILE_FLAGS = 'pypy3'

class BenchmarkTask:
    def __init__(self, source_name: str, test_input: str, execution_command: str):
        self.task_name = source_name
        self.test_input = test_input
        self.task = execution_command

def get_ins_and_ans(test_dirs) -> list[tuple[str, str]]:
    ans = []
    ins = []

    for d in test_dirs:
        if d.is_dir():
            ans += d.glob('*.ans')
            ans += d.glob('*.out')
            ins += d.glob('*.in')

    # remove test files that don't have both .in and .ans
    ans = [a for a in ans if str(a.parent / a.stem) in [str(i.parent / i.stem) for i in ins]]
    ins = [i for i in ins if str(i.parent / i.stem) in [str(a.parent / a.stem) for a in ans]]

    ans = sorted(ans)
    ins = sorted(ins)

    return list(zip([str(x) for x in ins], [str(x) for x in ans]))

def check_create_tmp_dir() -> None:
    if not TMP_PATH.is_dir():
        try:
            TMP_PATH.mkdir()
        except (FileExistsError, FileNotFoundError) as err:
            print("Could not create {TMP_PATH}:", err)

def is_accepted_src_file(file_path, problem_name) -> bool:
    return \
        file_path.is_file() \
        and file_path.name.startswith(problem_name) \
        and file_path.suffix in ACCEPTED_SRC_SUFFIXES

def match_problems_folder(problems_root: Path, problem_name: str) -> tuple[Path, ...]:
    return tuple(p for p in problems_root.glob(f'*{problem_name}*') if p.is_dir())

def valid_problem_name(problems_root: Path, problem_name: str) -> bool:
    return (problems_root / problem_name).is_dir()

def get_source_files(problems_root: Path, problem_name) -> list[Path]:
    problem_dir = problems_root / problem_name
    return [x for x in problem_dir.iterdir() if is_accepted_src_file(x, problem_name)]

def relativeCwd(path: str | Path) -> str:
    if (path is Path):
        return str(path.relative_to(Path.cwd()))
    else:
        return str(Path(path).relative_to(Path.cwd()))

def compile_and_get_test_command(source_file, problem_dir) -> str:
    # TODO extend to handle more languages
    output_name = f'{source_file.stem}_{source_file.suffix[1:]}'
    output_executable = TMP_PATH / output_name

    if source_file.suffix == '.cpp':
        # see https://open.kattis.com/languages/cpp
        CC = CPP_COMPILE_FLAGS + f' -o {output_executable} -I {problem_dir}'
    elif source_file.suffix == '.rs':
        # see https://open.kattis.com/languages/rust
        CC = RUST_COMPILE_FLAGS + f' -o {output_executable}'
    elif source_file.suffix == '.py':
        # see https://open.kattis.com/languages/python3
        try:
            subprocess.run(["pypy3", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            raise Exception('Executing python code requires `pypy3` (as that is what kattis does, see https://open.kattis.com/languages/python3)')

        CC = PYTHON_COMPILE_FLAGS
    else:
        raise Exception(f'Programming language not supported: {source_file.suffix}')

    output = None
    if source_file.suffix not in ('.py'):
        output = subprocess.run(f'{CC} {source_file}', shell=True, capture_output=True)

    if output and output.returncode != 0: # execution error
        print()
        print(f'{RED}{source_file} FAILED TO COMPILE!{NULL}')
        print(output.stderr.decode("utf-8"))
        return ''
    else:
        if output and output.stderr:
            print()
            print(f'{YELLOW}{source_file} has compile warnings:{NULL}')
            print(output.stderr.decode("utf-8"))

        shell = os.environ.get('SHELL', '')

        if source_file.suffix == '.py':
            if shell == 'powershell':
                return f'Get-Content {"{}"} | pypy3 {relativeCwd(source_file)} | Out-File {"{}"}'
            else:
                return f'pypy3 {relativeCwd(source_file)} < {"{}"} > {"{}"}'
        else:
            if shell == 'powershell':
                return f'Get-Content {"{}"} | {relativeCwd(output_executable)} | Out-File {"{}"}'
            else:
                return f'{relativeCwd(output_executable)} < {"{}"} > {"{}"}'

def printFailure(
        ans_path: str,
        output_stack: list[str],
        line: int,
        output: str,
        expected: str,
        o_file: TextIOWrapper,
        a_file: TextIOWrapper) -> None:

    print(f'{YELLOW}{relativeCwd(ans_path)}{NULL}')
    for o in output_stack:
        print(o.rstrip())
    print(f'{RED}FAIL!{NULL}')
    print(f'    at: {RED}line {line+1}{NULL}')
    print(f'    got: {RED}{output.rstrip()}{NULL}')
    print(f'    expected: {GREEN}{expected.rstrip()}{NULL}')

    trailing_output = o_file.read().split('\n')
    output_joined = '\n'.join(trailing_output[:5])
    print(f'{RED}{output_joined}{NULL}')
    if (len(trailing_output) > 5):
        print(f'... [{len(trailing_output[5:])} more rows]')
        print()

    # Print rest of expected output
    a_dump = a_file.read()
    if (a_dump):
        print(f'ANSWERS: [from line {line+2} onwards]')
        a_dump = a_dump.split('\n')
        print('\n'.join(a_dump[:5]))
        if len(a_dump) > 5:
            print(f'... [{len(a_dump[5:])} more rows]')
        print()

def check_test(output_path, ans_path) -> bool:
    # output logging
    stack_max_size = 16
    output_stack = []
    success = True

    """
    If all correct, don't print.

    Print stack of previously correct lines as green.

    Print wrong output and all following as red.

    Print expected output.
    """
    with open(output_path, 'r') as o_file, open(Path(ans_path), 'r') as a_file:
        for line, a_line in enumerate(a_file):
            # only check when input has a non-whitespace
            if not a_line.isspace():
                o_line = o_file.readline()
                while o_line.isspace():
                    o_line = o_file.readline()

                # lines are not the same (excluding whitespace)
                if a_line.split() != o_line.split():
                    success = False
                    printFailure(ans_path, output_stack, line, o_line, a_line, o_file, a_file)

                # save output
                output_stack.append(o_line)
                if len(output_stack) > stack_max_size:
                    output_stack.pop(0)
        # When done reading answers, check that there are not any residual in output
        rest = o_file.read()
        if rest and not rest.isspace():
            success = False
            print(f'{YELLOW}{ans_path}{NULL} got trailing output:');
            print(f'{RED}{rest}{NULL}')
            print()

    return success

def benchmark_report(benchmark: BenchmarkTask) -> list[str]:
    """
    Runs the benchmark task and returns the report.
    """
    test_name = Path(benchmark.test_input).stem
    md_path = TMP_PATH / f'{benchmark.task_name}_{test_name}.md'

    execution_without_input_output = benchmark.task[:benchmark.task.find(' < ')]

    subprocess.run(f"{HYPERFINE} --shell=none --export-markdown={str(md_path)} --command-name '{benchmark.task_name} --> {test_name}' --input '{benchmark.test_input}' '{execution_without_input_output}'", shell=True)

    with open(md_path, 'r') as f:
        return f.readlines()

def benchmark_average(benchmark: BenchmarkTask) -> str:
    lines = benchmark_report(benchmark)
    mean_unit = lines[0].split('|')[2].split()[1][1:-1].strip()
    stats = lines[2]
    average = stats.split('|')[2].split()[0].strip()

    return f'{average} {mean_unit}'

def benchmark_fastest(benchmark: BenchmarkTask) -> str:
    lines = benchmark_report(benchmark)
    min_unit = lines[0].split('|')[3].split()[1][1:-1].strip()
    stats = lines[2]
    fastest = stats.split('|')[3].strip()

    return f'{fastest} {min_unit}'

def benchmark_path(problems_root: Path, benchmark_name: str) -> Path:
    return problems_root / '.chum' / 'benchmarks' / f'{benchmark_name}.json'

def has_old_benchmark(problems_root: Path, benchmark_name: str) -> bool:
    return benchmark_path(problems_root, benchmark_name).is_file()

def load_old_benchmark(problems_root: Path, benchmark_name: str) -> dict[tuple[str, str], str]:
    with open(benchmark_path(problems_root, benchmark_name), 'r') as json_file:
        serialized_data = json.load(json_file)

    res = {}
    for key, value in serialized_data.items():
        split_key = key.split('___')
        res[(split_key[0], split_key[1])] = value

    return res

def save_benchmark(problems_root: Path, benchmark_name: str, benchmarks: dict[tuple[str, str], str]) -> None:
    res = {}
    for (source_name, test_name), value in benchmarks.items():
        res[f'{source_name}___{test_name}'] = value

    with open(benchmark_path(problems_root, benchmark_name), 'w') as json_file:
        json.dump(res, json_file, indent=2)

def convert_time_unit(number: float, unit: str) -> float:
    if unit == 's':
        return number
    elif unit == 'ms':
        return number / 1000
    elif unit == '\u00b5s':
        return number / 1000000
    else:
        raise Exception(f'Cannot parse time unit: {unit}')

def time_to_string(number: float) -> str:
    suffixes = (
        ('Ts', 1e12),
        ('Gs', 1e9),
        ('Ms', 1e6),
        ('ks', 1e3),
        ('s', 1),
        ('ms', 1e-3),
        ('\u00b5s', 1e-6),
        ('ns', 1e-9),
        ('ps', 1e-1)
    )

    # find the suffix
    i = 0
    for i, (_, f) in enumerate(suffixes):
        if abs(number) >= f:
            break

    suffix = suffixes[i][0]
    factor = suffixes[i][1]

    formatted_value = f"{number / factor:.3f}"
    if (float(formatted_value) % 100 == 0) and i > 0:
        suffix = suffixes[i-1][0]
        factor = suffixes[i-1][1]
        formatted_value = f"{number / factor:.3f}"
    # strip trailing zeros and the decimal point
    formatted_value = formatted_value.rstrip('0').rstrip('.')

    return f"{formatted_value} {suffix}"

def benchmark_diff(old_speed: str, new_speed: str) -> str:
    old_unit = old_speed.split()[1]
    o_speed = float(old_speed.split()[0])
    new_unit = new_speed.split()[1]
    n_speed = float(new_speed.split()[0])

    diff = convert_time_unit(n_speed, new_unit) - convert_time_unit(o_speed, old_unit)

    if (diff < 0):
        return f'({GREEN}{time_to_string(diff)}{NULL})'
    elif (diff > 0):
        return f'(+{RED}{time_to_string(diff)}{NULL})'
    else:
        return f'(=0)'

def visual_length(text: str) -> int:
    """
    Strings with weird escape characters are chaos. Gotta do this to get correct visual length when printing them.
    """
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    stripped_s = ansi_escape.sub('', text)
    return len(stripped_s)

class Benchmark(Enum):
    Average = 0
    Fastest = 1

def run_and_print_benchmarks(problems_root: Path, benchmarks: list[BenchmarkTask], problem_name: str, measurement: Benchmark) -> None:
    benchmarks = sorted(benchmarks, key= lambda b: b.task_name + b.test_input)
    names = sorted(set([x.task_name for x in benchmarks]))
    tests = sorted(set([Path(x.test_input).stem for x in benchmarks]))

    speeds: dict[tuple[str, str], str] = {}
    for i, benchmark in enumerate(benchmarks):
        measure: str = ''
        if (measurement == Benchmark.Average):
            measure = benchmark_average(benchmark)
        elif (measurement == Benchmark.Fastest):
            measure = benchmark_fastest(benchmark)

        speeds[(benchmark.task_name, Path(benchmark.test_input).stem)] = measure

    # load old benchmark
    old_benchmark: dict[tuple[str, str], str] = {}
    if (has_old_benchmark(problems_root, problem_name)):
        old_benchmark = load_old_benchmark(problems_root, problem_name)

    # write new benchmark
    save_benchmark(problems_root, problem_name, speeds)

    column_offset = len(max(tests, key=len)) + 2
    column_width = 10 + ((len(old_benchmark) != 0) * 13)

    if (measurement == Benchmark.Fastest):
        print(f'{BOLD}Fastest executions{NULL}')
    elif (measurement == Benchmark.Average):
        print(f'{BOLD}Average executions{NULL}')

    # print problems
    for i, n in enumerate(names):
        print(f' ({i + 1}) {n}')

    # print table header
    print(f"{'':{column_offset}}", end='')
    for i in range(len(names)):
        print(f"{f'({i + 1})':{column_width}}", end='')
    print()

    for t in tests:
        print(f'{t:{column_offset}}', end='')
        for i, n in enumerate(names):
            s = ' '
            if (n, t) in speeds:
                s = speeds[(n, t)]
                if (n, t) in old_benchmark:
                    old_speed = old_benchmark[(n, t)]
                    s += f' {benchmark_diff(old_speed, s)}'
            print(s, end='')
            width = column_width - visual_length(s)
            print(f'{"":{width}}', end='')

        print()

def has_hyperfine() -> bool:
    from shutil import which
    return which('hyperfine') is not None

def run_and_test(problems_root: Path, problem_name: str, benchmark: bool, benchmark_average: bool, cleanup: bool = False) -> None:
    if not valid_problem_name(problems_root, problem_name):
        problem_suggestions = match_problems_folder(problems_root, problem_name)

        # auto-select problem
        if len(problem_suggestions) == 1:
            problem_name = problem_suggestions[0].name
            print(f'No such problem exists, using only match: {problem_name}\n')
        # print error with suggestions
        else:
            print(f'No such problem exists: {(problems_root / problem_name).name}')
            if len(problem_suggestions):
                problems_string = '\n\t'.join(str(p.name) for p in problem_suggestions)
                print(f'\nDid you mean any of:\n\t{problems_string}')

            exit(1)

    problem_dir = problems_root / problem_name
    test_dir = problems_root / '.chumtests' / problem_name
    test_dirs = [test_dir, problem_dir / 'test', problem_dir / 'tests']
    ins_ans_pairs = get_ins_and_ans(test_dirs)

    check_create_tmp_dir()

    source_files = get_source_files(problems_root, problem_name)
    sources_string = ', '.join(relativeCwd(src) for src in source_files)
    print(f'{DIMMED}Compiling source files: [{sources_string}]{NULL}')

    run_benchmark: bool = benchmark or benchmark_average

    test_commands = []
    for s in source_files:
        test_command = compile_and_get_test_command(s, problem_dir)
        if test_command:
            test_commands.append(test_command)

    if not sum(1 for _ in ins_ans_pairs):
        test_folder_paths = "', \n\t'".join(str(t) for t in test_dirs)
        print(f"No tests found! Make sure to add both .in and .ans files to any of the folders:\n\t'{test_folder_paths}'")
    else:
        # tuples of name, test name, execution command
        benchmarks: list[BenchmarkTask] = []
        tests_string = ', '.join(relativeCwd(test) for test, _ in ins_ans_pairs)
        print(f'{DIMMED}Running tests: [{tests_string}]{NULL}')
        print()

        for src_index, test_command in enumerate(test_commands):
            src: Path = source_files[src_index]
            success = [True for _ in ins_ans_pairs]
            for i, (in_file, ans_file) in enumerate(ins_ans_pairs):
                test_output_path = TMP_PATH / f'{src.stem}_{src.suffix[1:]}_{Path(in_file).stem}_output'
                execution_cmd = test_command.format(relativeCwd(in_file), relativeCwd(test_output_path))
                output = subprocess.run([f'({execution_cmd})'], shell=True, capture_output=True)
                if output.returncode != 0: # execution error
                    print()
                    print(f"{RED}{relativeCwd(src)} ERROR WHILE RUNNING TEST '{relativeCwd(in_file)}'!{NULL}")
                    print(output.stderr.decode("utf-8"))
                    print(output.stdout.decode("utf-8"))
                    print('while running:')
                    print(f'{DIMMED}{execution_cmd}{NULL}')
                    exit(1)
                else: # no execution error
                    success[i] = check_test(test_output_path, ans_file) and success[i]

                    if run_benchmark:
                        benchmarks.append(BenchmarkTask(src.name, in_file, execution_cmd))

            print(f'{BLUE}{relativeCwd(src)}{NULL}')
            for i, s in enumerate(success):
                in_path: str = relativeCwd(ins_ans_pairs[i][0])
                if s:
                    print(f'{GREEN}  ✔ - PASSED{NULL} {in_path}')
                else:
                    print(f'{RED}  ✗ - FAILED{NULL} {in_path}')

        if run_benchmark:
            print()

            if not has_hyperfine():
                print(f'{BOLD}hyperfine{NULL} is not installed on your system! It is required to benchmark tests.')
                exit(1)

            measure: Benchmark
            if benchmark_average:
                measure = Benchmark.Average
            else:
                measure = Benchmark.Fastest

            run_and_print_benchmarks(problems_root, benchmarks, problem_name, measure)

    # cleanup
    if cleanup:
        for x in TMP_PATH.iterdir():
            x.unlink()
        TMP_PATH.rmdir()
    else:
        print()
        print(f"See output files: '{TMP_PATH.relative_to(Path.cwd())}'")
