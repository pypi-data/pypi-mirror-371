import pathlib
import subprocess
from contextlib import redirect_stdout
from typing import Callable, Iterable


def fzf_choose(data_fetchers: Iterable[Callable], *opts: str) -> str:
    """Run Fzf with choices given by the data fetchers"""
    args = ("fzf", "--tmux", *opts)

    proc = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )

    # setup process stream
    with redirect_stdout(proc.stdin):
        for fetcher in data_fetchers:
            for opt in fetcher():
                print(opt, flush=True)

    if proc.stdin:
        proc.stdin.close()

    output = ""
    if proc.stdout:
        output = proc.stdout.read()
    return output


def minify_path(path: pathlib.Path) -> pathlib.Path:
    """Replace /home/$USER with ~ in a path"""
    path_string = str(path).replace(str(path.home()), "~")
    return pathlib.Path(path_string)


def session_name(session_path: pathlib.Path) -> str:
    """Sanitize `session_path` and create a session name using the basename"""
    # keep only basename
    name = session_path.name
    replace_dict = {".": "-", "/": "-", " ": "-"}
    for old, new in replace_dict.items():
        name = name.replace(old, new)

    return name
