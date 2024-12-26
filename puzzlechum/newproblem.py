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

TEMPLATES_ROOT = Path(__file__).parent / 'templates'

TESTS_URL = 'https://open.kattis.com/problems/{}/file/statement/samples.zip'

DEFAULT_LANGUAGE_KEY = 'default_language'

class Template(Enum):
    cpp = 'cpp'
    rs = 'rs'
    py = 'py'

def problem_test_directory(problems_root: Path, problem_name: str) -> Path:
    test_root = problems_root / '.chumtests'
    test_dir = test_root / problem_name
    if not test_root.is_dir():
        test_root.mkdir()
    if not test_dir.is_dir():
        test_dir.mkdir()

    return test_dir

def download_tests(problems_root: Path, problem_name: str) -> bool:
    tests_dir = problem_test_directory(problems_root, problem_name)

    zip_path = Path('samples.zip')

    with open(zip_path, 'wb') as file:
        url = TESTS_URL.format(problem_name)
        response = requests.get(url)
        if response.status_code >= 400:
            print('Warning: Could not download test samples from kattis')
            print(f" - Does '{problem_name}' exist at kattis?")
            print(' - Do you have an internet connection?\n')
            return False
        else:
            file.write(response.content)

    # extract sample input to tests folder
    f = zipfile.ZipFile(zip_path)

    f.extractall(tests_dir)

    # remove zip
    Path(zip_path).unlink()

    return True

def create_problem_folders(problems_root: Path, problem_name: str):
    if not (problems_root / problem_name).is_dir():
        (problems_root / problem_name).mkdir()

def problem_path(problems_root: Path, problem_name: str, file_suffix: str):
    return problems_root / problem_name / f'{problem_name}.{file_suffix}'

def config_path(problems_root: Path) -> Path:
    return problems_root / '.chumconfig'

def get_config(problems_root: Path) -> dict:
    config = config_path(problems_root)
    if config.is_file():
        with open(config, 'r') as f:
            return json.load(f)
    else:
        return {}

def write_config(problems_root: Path, config: dict) -> None:
    with open(config_path(problems_root), 'w') as f:
        json.dump(config, f)

def default_language(problems_root: Path) -> Template|None:
    config = get_config(problems_root)
    if DEFAULT_LANGUAGE_KEY in config:
        try:
            return Template(config[DEFAULT_LANGUAGE_KEY])
        except Exception:
            raise Exception(f"'{config[DEFAULT_LANGUAGE_KEY]}' is not a valid template! Must be any of {list(t.value for t in Template)}")
    else:
        return None

def set_default_language(problems_root: Path, language: str) -> None:
    config = get_config(problems_root)
    config[DEFAULT_LANGUAGE_KEY] = language
    write_config(problems_root, config)

def template_path(problems_root: Path, template: Template) -> Path:
    custom_template_path = problems_root / '.chumtemplates' / f'template.{template.value}'
    if custom_template_path.is_file():
        return custom_template_path
    else:
        return TEMPLATES_ROOT / f'template.{template.value}'

def copy_template(problems_root: Path, template: Template, destination: Path):
    success = False

    if not destination.is_file():
        shutil.copyfile(template_path(problems_root, template), destination)
        success = True

    return success

def new_problem(problems_root: Path, problem_name: str, template: Template|None = None) -> None:
    create_problem_folders(problems_root, problem_name)

    dl = default_language(problems_root)
    if dl is None:
        if template is None:
            print(f'You have not set a default programming language. The following argument must be set the first time you run this script:\n  --template [{", ".join(t.value for t in Template)}]')
            exit()
        else:
            set_default_language(problems_root, template.value)
            print(f"New default programming language set: '{template.value}'")
            print(f" - To change this setting, remove or modify the file '{config_path(problems_root)}'")
            print()
    elif template is None:
        template = dl

    problem_file = problem_path(problems_root, problem_name, template.value)
    template_success = copy_template(problems_root, template, problem_file)

    if template_success:
        print(f'Copied template to \'./{problem_file.relative_to(Path.cwd())}\'')
    else:
        print(f'Problem already exists at {problem_file}')

    tests_success = download_tests(problems_root, problem_name)
    if tests_success:
        print(f"Test samples successfully downloaded to '{problem_test_directory(problems_root, problem_name)}'")
    else:
        print("Test samples was not found, skipping...")

    if template_success:
        print(f"Done creating problem at '{problems_root}/{problem_name}'")
