import pathlib
import subprocess
from typing import List

WATCHDIRS = [pathlib.Path().home()]


def fd() -> List[str]:
    args = ["fd", "-d", "1", "-t", "d", "-t", "l"]
    for d in WATCHDIRS:
        args.extend(("--search-path", str(d)))

    return [x.strip() for x in subprocess.check_output(args, text=True).splitlines()]


def zoxide() -> List[str]:
    args = ("zoxide", "query", "--list")
    return [x.strip() for x in subprocess.check_output(args, text=True).splitlines()]
