# check-depz: Easy outdated dependencies check for Python projects 

Project `check-depz` is a simple command line tool to easily check if your Python project contains too many outdated dependencies. 

## Usage

Add `check-depz` to your project:

```
$ poetry add --group=dev check-depz 
```

Run dependencies check:

```
$ poetry run check-depz
Outdated top level dependencies: 0/10
Outdated all dependencies: 1/20
        typing-extensions 4.12.2 4.13.0 Backported and Experimental Type Hints for P...
All dependency checks passed.
```

### Outdated dependencies limit 

By default `check-depz` allows up to 10 outdated dependencies for top level dependencies and 20 outdated dependencies for all dependencies in the project. You can adjust limits with `--top-level-limit` and `--all-limit` options:

```bash
check-depz --top-level-limit 15 --all-limit 30
```

### Exit codes

Please note `check-depz` returns exit code `0` on succesfull checks and code `1` on failure, so you can rely on this behavior:

```
check-depz && echo "Dependencies are up to date!"
```

...or...


```
#!/bin/bash
set -e  # Exit on command failure

check-depz
echo "This will NOT run if there are too many out of date dependencies."

```