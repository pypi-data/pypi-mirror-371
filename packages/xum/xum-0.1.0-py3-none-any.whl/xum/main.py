import os
import pathlib

import libtmux
import typer

import xum.utils as utils
from xum.fetchers import fd, zoxide

APP_NAME = "xum"

app = typer.Typer(
    name=APP_NAME,
    add_completion=False,
    help="Manage Tmux sessions with fuzzy powers.",
)


@app.command(help="Create a new session")
def create():
    # connect to tmux server
    server = libtmux.Server()

    # prompt for session with fzf
    fetchers = (fd, zoxide)
    if out := utils.fzf_choose(fetchers):
        session_path = pathlib.Path(out).absolute()
        assert session_path.exists()
    else:
        return

    # sanitize session name
    session_name = utils.session_name(session_path)

    # check if session already exists
    if not server.has_session(session_name):
        assert session_path.is_absolute()
        server.new_session(session_name, start_directory=session_path)

    # switch client or attach to new session
    if os.getenv("TMUX"):
        server.switch_client(session_name)
    else:
        server.attach_session(session_name)


@app.command(help="Switch to session")
def switch():
    # connect to tmux server
    server = libtmux.Server()

    def session_fetcher():
        return (s.name for s in server.sessions)

    # prompt for session with fzf
    session_name = utils.fzf_choose((session_fetcher,)).strip()
    if session_name:
        assert server.has_session(session_name)
    else:
        return

    # switch client or attach to session
    if os.getenv("TMUX"):
        server.switch_client(session_name)
    else:
        server.attach_session(session_name)


@app.command(help="Close existing sessions")
def close():
    # connect to tmux server
    server = libtmux.Server()

    def session_fetcher():
        return (s.name for s in server.sessions)

    session_names = map(
        str.strip, utils.fzf_choose((session_fetcher,), "-m").splitlines()
    )

    for name in session_names:
        assert server.has_session(name.strip())
        print(f"XUM: quitting session '{name.strip()}'")
        server.kill_session(name.strip())


@app.command(help="Create session at the current working directory")
def here():
    server = libtmux.Server()

    session_path = pathlib.Path().absolute()
    assert session_path.exists()

    session_name = utils.session_name(session_path).strip()
    if not server.has_session(session_name):
        server.new_session(session_name, start_directory=session_path)

    if os.getenv("TMUX"):
        server.switch_client(session_name)
    else:
        server.attach_session(session_name)
