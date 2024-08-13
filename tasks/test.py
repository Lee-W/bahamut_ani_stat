from __future__ import annotations

from invoke import task

from tasks.common import VENV_PREFIX


@task(default=True)
def run(ctx, allow_no_tests=False):
    """Run test cases"""
    result = ctx.run(f"{VENV_PREFIX} pytest", pty=True, warn=True)
    if allow_no_tests and result.exited == 5:
        exit(0)
    exit(result.exited)


@task
def cov(ctx):
    """Run test coverage check"""
    ctx.run(f"{VENV_PREFIX} pytest --cov=bahamut_ani_stat tests/", pty=True)
