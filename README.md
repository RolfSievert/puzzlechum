# Puzzle Chum

Helper scripts to create, test, and benchmark your algorithms! (also downloads kattis test samples automatically ;) )

*(Only works for **rust**, **c++** and **python** currently, but feel free to open an Issue for further language support)*

## Installation

### Arch linux

Two options:
1. Run `just install-arch` to install using pacman. (requires [just](https://github.com/casey/just))
2. Run the following code
```bash
python3 -m build
makepkg --syncdeps --force --clean
sudo pacman -U puzzlechum-*-x86_64.pkg.tar.zst
```

### Using pip

I recommend installing with [pipx](https://github.com/pypa/pipx), and it is used just like pip is used.
```bash
python3 -m build
pipx install .
```

but if you want to, you can exchange `pipx` with `pip`.

## Requirements

Required regardless of what language you are programming with:
- `requests` - python `requests` package

Optional dependencies:
- [hyperfine](https://github.com/sharkdp/hyperfine) - only required for benchmarking!

### Testing python code
- [pypy3](https://www.pypy.org/) - required for python code compilation

## Usage

Install the package and run `chum --help` to see available commands.

`chum` runs anywhere beneath the problems root, which you set with `chum init`. This is so that chum knows where to search for your solutions.

Main commands:
- `chum new [problem name]` - create a new problem, and tests are downloaded automatically if the `[problem name]` matches an open kattis problem ID.
- `chum test [problem name]` - compile and run tests, see the `--benchmark` flag for also outputting performance numbers and solution comparisons.
    - you may have several solutions in your problem folder, just make sure that each begin with `[problem name]` so that `chum` recognizes them as solutions to be compared.


### Examples

`newproblem` example:
```
chum new triarea
Copied template to '.../problems/triarea/triarea.cpp'
Test samples successfully downloaded to '.../problems/.chumtests/triarea'
```

`runtest` example:
```
chum test twosum --benchmark
Compiling source files... [/home/rolfsievert/projects/puzzlechum/problems/twosum/twosum.cpp, /home/rolfsievert/projects/puzzlechum/problems/twosum/twosum.rs]
Running tests... [/home/rolfsievert/projects/puzzlechum/tests/twosum/sample1.in, /home/rolfsievert/projects/puzzlechum/tests/twosum/sample2.in]

/home/rolfsievert/projects/puzzlechum/problems/twosum/twosum.cpp
  ✔ - PASSED
/home/rolfsievert/projects/puzzlechum/problems/twosum/twosum.rs
  ✔ - PASSED

...

Fastest executions
 (1) twosum.cpp
 (2) twosum.rs
          (1)     (2)
sample1  0.6 ms  1.0 ms
sample2  0.6 ms  1.0 ms
```

Failing `runtest` example:

```
chum test twosum
Compiling source files... [/home/rolfsievert/projects/puzzlechum/problems/twosum/twosum.cpp, /home/rolfsievert/projects/puzzlechum/problems/twosum/twosum.rs]
Running tests... [/home/rolfsievert/projects/puzzlechum/tests/twosum/sample1.in, /home/rolfsievert/projects/puzzlechum/tests/twosum/sample2.in]

/home/rolfsievert/projects/puzzlechum/tests/twosum/sample1.ans failed at line 1
EXPECTED: 2

3

/home/rolfsievert/projects/puzzlechum/problems/twosum/twosum.cpp
  ✗ - FAILED
/home/rolfsievert/projects/puzzlechum/problems/twosum/twosum.rs
  ✔ - PASSED
```

## Folder structure

```
problems/
    problem1_name/
        tests/
            sample1.in
            sample1.ans
        problem1_name*.cpp
        problem1_name*.rs
        problem1_name*.py

    problem2_name/
        ...
    ...
```
