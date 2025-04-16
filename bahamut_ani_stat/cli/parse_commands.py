from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

import click

from bahamut_ani_stat.cli import options
from bahamut_ani_stat.parser import parser


@click.group(name="parse")
def parse_command_group() -> None:
    pass


def _append_or_overwrite_outputfile(
    data_key: str, data_value: Any, output_filename: str, handle_exist_output: str
) -> None:
    result = [
        {
            data_key: data_value,
            "retrieve_time": datetime.now().astimezone().isoformat(),
        }
    ]
    if handle_exist_output == "append" and os.path.exists(output_filename):
        with open(output_filename) as input_file:
            original_data = json.load(input_file)

        result = original_data[:] + result

    with open(output_filename, "w") as output_file:
        json.dump(result, output_file, indent=4, ensure_ascii=False)


@parse_command_group.command(name="get-premium-rate")
@options.print_output_option
@options.outputfile_option
def get_premium_rate_command(print_output: bool, output_filename: str, handle_exist_output: str) -> None:
    """Get 巴哈姆特動畫瘋 premium rate"""
    if not any([print_output, output_filename]):
        click.echo("Either --print-out or --output-file needs to be provided")
        return

    premium_rate = parser.get_premium_rate()

    if print_output:
        click.echo(premium_rate)

    if output_filename:
        _append_or_overwrite_outputfile("premium_rate", premium_rate, output_filename, handle_exist_output)


@parse_command_group.command(name="get-new-animes")
@options.print_output_option
@options.outputfile_option
def get_new_animes_command(print_output: bool, output_filename: str, handle_exist_output: str) -> None:
    """Parse 本季新番 table and print out or export as json file"""
    if not any([print_output, output_filename]):
        click.echo("Either --print-output or --output-filename needs to be provided")
        return

    new_animes = parser.get_new_animes()

    if print_output:
        for anime in new_animes:
            click.echo(anime)

    if output_filename:
        _append_or_overwrite_outputfile("new_animes", new_animes, output_filename, handle_exist_output)
