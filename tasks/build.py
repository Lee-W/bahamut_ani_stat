from invoke import Collection, task


@task
def clean(ctx):
    """Remove all the tmp files in .gitignore"""
    ctx.run("git clean -Xdf")


@task
def dist(ctx):
    """Build distribution"""
    ctx.run("poetry build")


@task
def docker(ctx):
    """Build docker image"""
    ctx.run("poetry export -f requirements.txt -o requirements.txt")
    user_name = "lee_w"
    proj_name = "bahamut_ani_stat"
    repo_name = f"{user_name}/{proj_name}"
    ctx.run(f"docker build -t {repo_name}:latest .")


build_ns = Collection("build")
build_ns.add_task(clean)
build_ns.add_task(dist)
build_ns.add_task(docker)
