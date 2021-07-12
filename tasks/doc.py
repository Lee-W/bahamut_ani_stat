from invoke import task

from tasks.common import VENV_PREFIX

ENV_VAR_PREFIX = "SITE_URL=http://127.0.0.1:8000 "


@task(optional=["clean"])
def build(ctx, clean=True, local=True):
    """Build documentation"""
    argument = ""
    if clean:
        argument += " --clean"

    cmd = f"{VENV_PREFIX} mkdocs build {argument}"
    if local:
        cmd = f"{ENV_VAR_PREFIX}{cmd}"

    ctx.run(cmd)


@task(default=True)
def serve(ctx, local=True):
    """Run local server"""
    cmd = f"{VENV_PREFIX} mkdocs serve"
    if local:
        cmd = f"{ENV_VAR_PREFIX}{cmd}"
    ctx.run(cmd)


@task
def deploy(ctx):
    """Deploy to github page"""
    ctx.run(f"{VENV_PREFIX} mkdocs gh-deploy")
