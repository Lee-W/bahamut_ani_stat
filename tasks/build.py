from __future__ import annotations

from invoke.collection import Collection
from invoke.context import Context
from invoke.tasks import task


@task
def clean(ctx: Context) -> None:
    """Remove all the tmp files in .gitignore"""
    ctx.run("git clean -Xdf")


@task
def dist(ctx: Context) -> None:
    """Build distribution"""
    ctx.run("uv build")


@task
def docker(ctx: Context) -> None:
    """Build docker image"""
    ctx.run("uv lock")
    user_name = "lee_w"
    proj_name = "bahamut_ani_stat"
    repo_name = f"{user_name}/{proj_name}"
    ctx.run(f"docker build -t {repo_name}:latest .")


build_ns = Collection("build")
build_ns.add_task(clean)  # type: ignore[arg-type]
build_ns.add_task(dist)  # type: ignore[arg-type]
build_ns.add_task(docker)  # type: ignore[arg-type]
