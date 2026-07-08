[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)
[![New pull request received](https://github.com/Lee-W/bahamut_ani_stat/actions/workflows/python-check.yaml/badge.svg)](https://github.com/Lee-W/bahamut_ani_stat/actions/workflows/python-check.yaml)
[![PyPI Package latest release](https://img.shields.io/pypi/v/bahamut_ani_stat.svg?style=flat-square)](https://pypi.org/project/bahamut_ani_stat/)
[![PyPI Package download count (per month)](https://img.shields.io/pypi/dm/bahamut_ani_stat?style=flat-square)](https://pypi.org/project/bahamut_ani_stat/)
[![Supported versions](https://img.shields.io/pypi/pyversions/bahamut_ani_stat.svg?style=flat-square)](https://pypi.org/project/bahamut_ani_stat/)

# bahamut_ani_stat

Toolkit for Bahamut ani gamer data

## Getting Started

### Prerequisites
* [Python](https://www.python.org/downloads/)
* [uv](https://github.com/astral-sh/uv)

## Usage

Install the package and inspect the available CLI commands:

```sh
uvx --from bahamut_ani_stat bahamut-ani-stat --help
```

Common local development commands:

```sh
uv run bahamut-ani-stat parse get-premium-rate --print-output
uv run bahamut-ani-stat db create-tables sqlite:///anime.db
uv run bahamut-ani-stat db add-new-animes sqlite:///anime.db
uv run bahamut-ani-stat db add-animes-detail sqlite:///anime.db
uv run bahamut-ani-stat plot anime sqlite:///anime.db docs/assets/anime.html
```

The historical `anime.db` dataset is maintained on the `accumulate-data` branch. Daily data
collection is currently driven outside this repository, so changes on `main` do not by themselves
record new daily data.

## Contributing
See [Contributing](contributing.md)

## Maintenance
See [Data maintenance](data-maintenance.md) and [Schema maintenance](schema-maintenance.md).

## Authors
Wei Lee <weilee.rx@gmail.com>

Created from [Lee-W/cookiecutter-python-template](https://github.com/Lee-W/cookiecutter-python-template/tree/3.0.0) version 3.0.0
