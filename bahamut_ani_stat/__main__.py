from __future__ import annotations

import click

from bahamut_ani_stat.cli.db_commands import db_command_group
from bahamut_ani_stat.cli.parse_commands import parse_command_group
from bahamut_ani_stat.cli.plot_commands import plot_command_group


@click.group()
def main() -> None:
    pass


main.add_command(parse_command_group)
main.add_command(db_command_group)
main.add_command(plot_command_group)


if __name__ == "__main__":
    main()
