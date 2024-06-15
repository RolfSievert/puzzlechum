#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
Provided a problem id, downloads tests and creates a test file if it doesn't exist already.
"""

from enum import Enum
import shutil
import requests
from pathlib import Path
import zipfile
import json

# Root folders
# call .resolve() if newproblem is symlinked
TEMPLATES_ROOT = Path(__file__).resolve().parent / 'templates'

TESTS_URL = 'https://open.kattis.com/problems/{}/file/statement/samples.zip'

CONFIG_PATH = Path(__file__).resolve().parent / '.puzzle_config'
DEFAULT_LANGUAGE_KEY = 'default_language'

class Template(Enum):
    cpp = 'cpp'
    rs = 'rs'
    py = 'py'

def problem_test_directory(problems_root: Path, problem_name: str):
    return problems_root / 'tests' / problem_name

def download_tests(problems_root: Path, problem_name: str) -> bool:
    tests_dir = problem_test_directory(problems_root, problem_name)

    if tests_dir.is_dir():
        return False

    zip_path = Path('samples.zip')

    with open(zip_path, 'wb') as file:
        url = TESTS_URL.format(problem_name)
        response = requests.get(url)
        if response.status_code >= 400:
            print(f'Warning: Could not download test samples from kattis')
            print(f" - Does '{problem_name}' exist at kattis?")
            print(' - Do you have an internet connection?\n')
            return False
        else:
            file.write(response.content)

    # extract sample input to tests folder
    f = zipfile.ZipFile(zip_path)

    tests_dir.mkdir()
    f.extractall(tests_dir)

    # remove zip
    Path(zip_path).unlink()

    return True

def create_problem_folders(problems_root: Path, problem_name: str):
    if not (problems_root / problem_name).is_dir():
        (problems_root / problem_name).mkdir()

def problem_path(problems_root: Path, problem_name: str, file_suffix: str):
    return problems_root / problem_name / f'{problem_name}.{file_suffix}'

def get_config() -> dict:
    if CONFIG_PATH.is_file():
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    else:
        return {}

def write_config(config: dict) -> None:
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f)

def default_language() -> Template|None:
    config = get_config()
    if DEFAULT_LANGUAGE_KEY in config:
        return config[DEFAULT_LANGUAGE_KEY]
    else:
        return None

def set_default_language(language: str) -> None:
    config = get_config()
    config[DEFAULT_LANGUAGE_KEY] = language
    write_config(config)

def copy_template(template_suffix, destination):
    success = False
    problem_path = destination

    if not problem_path.is_file():
        template = TEMPLATES_ROOT / f'template.{template_suffix}'
        if not template.is_file():
            raise Exception(f"Template '{template}' does not exist! Perhaps create one?")
        else:
            shutil.copyfile(template, problem_path)

        success = True

    return success

def new_problem(problems_root: Path, problem_name: str, template: Template|None = None) -> None:
    create_problem_folders(problems_root, problem_name)

    dl = default_language()
    if dl == None:
        if template is None:
            print(f'You have not set a default programming language. The following argument must be set the first time you run this script:\n  --template [{", ".join(t.value for t in Template)}]')
            exit()
        else:
            set_default_language(template.value)
            print(f"New default programming language set: '{template.value}'. To change this setting, either remove or modify the file '{CONFIG_PATH}'.\n")
    elif template == None:
        template = dl

    problem_file = problem_path(problems_root, problem_name, template.value)
    template_success = copy_template(template, problem_file)

    if template_success:
        print(f'Copied template to \'{problem_file}\'')
    else:
        print(f'Problem already exists at {problem_file}')

    tests_success = download_tests(problems_root, problem_name)
    if tests_success:
        print(f"Test samples successfully downloaded to '{problem_test_directory(problems_root, problem_name)}'")
    else:
        print(f"Test samples already exists, skipping...")
