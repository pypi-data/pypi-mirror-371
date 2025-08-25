import os
import shutil

import nox

nox.options.default_venv_backend = "uv"

PYTHON_VERSIONS = (
    "3.9",
    "3.10",
    "3.11",
    "3.12",
    "3.13",
    "3.13t",
    "3.14",
    "3.14t",
    "pypy3.10",
    "pypy3.11",
)


def cargo(session: nox.Session, *args: str) -> None:
    session.run("cargo", *args, external=True)


def install(
    session: nox.Session, *, groups: str | tuple[str, ...] | None = None
) -> None:
    args: list[str] = []

    if groups:
        if isinstance(groups, str):
            args += ["--group", groups]
        elif isinstance(groups, tuple):
            for group in groups:
                args += ["--group", group]

    session.run_install(
        "uv",
        "sync",
        "--locked",
        "--no-default-groups",
        *args,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )


@nox.session(venv_backend=None, default=False)
def clean(session: nox.Session) -> None:
    cargo(session, "clean")

    paths = (
        "./.mypy_cache",
        "./.pytest_cache",
        "./.ruff_cache",
        "./dist",
        "./tests/__pycache__",
        "./__pycache__",
        "./python/__pycache__",
        "./.nox",
    )

    for p in paths:
        try:
            shutil.rmtree(p)
        except FileNotFoundError:
            pass


@nox.session(python="3.13")
def lint(session: nox.Session) -> None:
    install(session, groups="lint")

    if os.getenv("CI"):
        # Do not modify files in CI, simply fail.
        cargo(session, "fmt", "--check")
        cargo(session, "clippy")
        session.run("ruff", "check", ".")
        session.run("ruff", "format", ".", "--check")
    else:
        # Fix any fixable errors if running locally.
        cargo(session, "fmt")
        cargo(session, "clippy", "--fix", "--lib", "-p", "myne")
        session.run("ruff", "check", ".", "--fix")
        session.run("ruff", "format", ".")


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    install(session, groups="test")
    session.run("pytest", *session.posargs)
