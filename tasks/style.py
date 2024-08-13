from invoke import task

from tasks.common import COMMON_TARGETS_AS_STR, VENV_PREFIX


@task
def ruff(ctx):
    """Check style through ruff"""
    ctx.run(f"{VENV_PREFIX} ruff check {COMMON_TARGETS_AS_STR}")


@task
def mypy(ctx):
    """Check style through mypy"""
    ctx.run(f"{VENV_PREFIX} mypy")


@task
def commit_check(ctx, remote="origin"):
    """Check commit message through commitizen"""
    ctx.run(
        f"{VENV_PREFIX} cz -nr 3 check --rev-range {remote}/main..",
        warn=True
    )


@task(pre=[ruff, mypy, commit_check], default=True)
def run(ctx):
    """Check style through linter (Note that pylint is not included)"""
    pass


@task(pre=[ruff])
def format(ctx):
    """Reformat python files through ruff"""
    pass
