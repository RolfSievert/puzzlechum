# Puzzle Chum

Helper scripts to create, test, and benchmark your algorithms! (also downloads kattis test samples automatically ;) )

*(Only works for rust and cpp currently)*

## Usage

- `./newproblem [-h, --help] [--template {cpp,rs}] problem_name`
    - Creates file in `problems/` folder based on template in `templates/`
    - Automatically downloads tests from kattis name to `tests/problem_name/`

- `./runtest [-h, --help] [-b, --benchmark] [-n, --no-cleanup] problem_name`
    - Compiles and tests your solutions matching `problem_name*` within `problems/problem_name/`
    - Compares output of program given the `*.in`-files within `tests/problem_name/` and `problems/problem_name/tests/`, and compares to the `.ans`-files in the same folder
    - If test fails, prints first faulty output line and information
    - if `-b` or `--benchmark` is provided, outputs minimal runtime of problem file for all tests in a compact grid
    - if `-n` or `--no-cleanup` is provided, leave compilation and output files in '.runtest_tmp/'

### Examples

`newproblem` example:
```sh
./newproblem triarea
Copied template to '/home/rolfsievert/projects/kattis/problems/triarea/triarea.cpp'
Test samples successfully downloaded to '/home/rolfsievert/projects/kattis/tests/triarea'
```

`runtest` example:
```sh
./runtest twosum --benchmark
Compiling source files... [/home/rolfsievert/projects/kattis/problems/twosum/twosum.cpp, /home/rolfsievert/projects/kattis/problems/twosum/twosum.rs]
Running tests... [/home/rolfsievert/projects/kattis/tests/twosum/sample1.in, /home/rolfsievert/projects/kattis/tests/twosum/sample2.in]

/home/rolfsievert/projects/kattis/problems/twosum/twosum.cpp
  ✔ - PASSED
/home/rolfsievert/projects/kattis/problems/twosum/twosum.rs
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

```sh
./runtest twosum
Compiling source files... [/home/rolfsievert/projects/kattis/problems/twosum/twosum.cpp, /home/rolfsievert/projects/kattis/problems/twosum/twosum.rs]
Running tests... [/home/rolfsievert/projects/kattis/tests/twosum/sample1.in, /home/rolfsievert/projects/kattis/tests/twosum/sample2.in]

/home/rolfsievert/projects/kattis/tests/twosum/sample1.ans failed at line 1
EXPECTED: 2

3

/home/rolfsievert/projects/kattis/problems/twosum/twosum.cpp
  ✗ - FAILED
/home/rolfsievert/projects/kattis/problems/twosum/twosum.rs
  ✔ - PASSED
```

## Folder structure

```
problems/
    problem_name/
        tests/
            sample1.in
            sample1.ans
        problem_name*.cpp
        problem_name*.rs
tests/
    problem_name/
        sample1.in
        sample1.ans
```

## Requirements

- `hyperfine` - only for benchmarking!

## Tips

- If you already have a problems folder, just symlink it with the name `problems` to make it accessible by the scripts.

## TODO
- Extend language compatability
