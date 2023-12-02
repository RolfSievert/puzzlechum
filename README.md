# Puzzle Chum

Helper scripts to create, test, and benchmark your algorithms! (also downloads kattis test samples automatically ;) )

*(Only works for **rust**, **c++** and **python** currently, but feel free to open an Issue for further language support)*


## Optional requirements

- [hyperfine](https://github.com/sharkdp/hyperfine) - only required for benchmarking!


## Usage

Just clone this repo (there are no prerequisites). See the following commands to get started:

- `./newproblem [-h, --help] [--template {cpp,rs,py}] problem_name`
    - Creates file in `problems/` folder based on template in `templates/`
    - Automatically downloads tests from `open.kattis.com/problems/[problem_name]` to `tests/[problem_name]/`

- `./runtest [-h, --help] [-b, --benchmark] [-n, --no-cleanup] problem_name`
    - Compiles and tests your solutions matching `problem_name*` within `problems/problem_name/`
    - Compares output of program given the `*.in`-files within `tests/problem_name/` and `problems/problem_name/tests/` to the `*.ans`-files in the same folder
    - If test fails, prints first faulty output line and information
    - if `-b` or `--benchmark` is provided, outputs minimal runtime of problem file for all tests in a compact grid
    - if `-n` or `--no-cleanup` is provided, leave compilation and output files in `.runtest_tmp/`


### Examples

`newproblem` example:
```
./newproblem triarea
Copied template to '/home/rolfsievert/projects/puzzlechum/problems/triarea/triarea.cpp'
Test samples successfully downloaded to '/home/rolfsievert/projects/puzzlechum/tests/triarea'
```

`runtest` example:
```
./runtest twosum --benchmark
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
./runtest twosum
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
    problem_name/
        tests/
            sample1.in
            sample1.ans
        problem_name*.cpp
        problem_name*.rs
        problem_name*.py
    ...
tests/
    problem_name/
        sample1.in
        sample1.ans
    ...
```

> If you already have a problems folder, just symlink it to `.../puzzlechum/problems` to make it accessible by the scripts.
