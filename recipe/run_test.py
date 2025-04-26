import sys
from subprocess import call
import site
from pathlib import Path
import shutil

IN_SP_DIR = Path(site.getsitepackages()[0]) / "nbclassic"

FAIL_UNDER = 32
ERRORS_ON_DISCOVERY = [
    # ImportError: cannot import name 'urlencode_unix_socket' from 'nbclassic.notebookapp'
    IN_SP_DIR / "bundler/tests/test_bundler_api.py",
    # not worth the hassle of x11, random playwright binaries, etc.
    IN_SP_DIR / "tests/end_to_end",
]


COV = ["coverage"]
RUN = ["run", "--source=nbclassic", "--branch", "--append", "-m"]
PYTEST = ["pytest", "-vv", "--color=yes", "--tb=long"]
REPORT = ["report", "--show-missing", "--skip-covered", f"--fail-under={FAIL_UNDER}"]
IN_TREE_PYTEST = [*PYTEST, "--pyargs", "nbclassic"]

IN_TREE_SKIPS: list[str] = [
    # ensure -k has something to `or`
    # "not-really-a-test",
]

if IN_TREE_SKIPS:
    IN_TREE_PYTEST += ["-k", f"""not ({" or ".join(IN_TREE_SKIPS)})"""]


def do(args: list[str]):
    print(">>>", *args)
    return call(args)

if __name__ == "__main__":
    for path in ERRORS_ON_DISCOVERY:
        print("... removing untestable", path)
        shutil.rmtree(path) if path.is_dir() else path.unlink()

    sys.exit(
        max(
            # run the out-of-tree tests
            do([*COV, *RUN, *PYTEST]),
            # run the in-tree tests
            do([*COV, *RUN, *IN_TREE_PYTEST]),
            # check coverage
            do([*COV, *REPORT]),
        )
    )
