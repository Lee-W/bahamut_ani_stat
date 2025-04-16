from __future__ import annotations

from invoke.context import Context
from invoke.tasks import task

from tasks.common import VENV_PREFIX

ENV_VAR_PREFIX = "SITE_URL=http://127.0.0.1:8000 "


@task(optional=["clean"])
def build(ctx: Context, clean: bool = True, local: bool = True) -> None:
    """Build documentation locally"""
    arguments = " --clean" if clean else ""
    cmd = f"{VENV_PREFIX} mkdocs build {arguments}"
    if local:
        cmd = f"{ENV_VAR_PREFIX}{cmd}"
    ctx.run(cmd)


@task(default=True)
def serve(ctx: Context, local: bool = True) -> None:
    """Run local server"""
    cmd = f"{VENV_PREFIX} mkdocs serve"
    if local:
        cmd = f"{ENV_VAR_PREFIX}{cmd}"
    ctx.run(cmd)


@task
def deploy(ctx: Context) -> None:
    """Deploy to github page"""
    ctx.run(f"{VENV_PREFIX} mkdocs gh-deploy")
