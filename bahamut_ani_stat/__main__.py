import json
import os
from datetime import datetime

import click

from bahamut_ani_stat.parser import parser


@click.group()
def main():
    pass


@click.group()
def parse():
    pass


@parse.command(name="get-premium-rate")
@click.option(
    "--output-filename",
    help="Output to file only if --output-filename is provided",
    default=None,
    type=str,
)
@click.option(
    "--append",
    "handle_exist_output",
    help="Append data if the output file already exists",
    default=True,
    flag_value="append",
)
@click.option(
    "--overwrite",
    "handle_exist_output",
    help="Overwrite file if the output file already exists",
    flag_value="overwrite",
)
def get_premium_rate_command(output_filename: str, handle_exist_output: str):
    prenium_rate = parser.get_premium_rate()
    click.echo(prenium_rate)

    if output_filename:
        result = [
            {
                "premium_rate": prenium_rate,
                "retrieve_time": datetime.now().astimezone().isoformat(),
            }
        ]
        if handle_exist_output == "append" and os.path.exists(output_filename):
            with open(output_filename, "r") as input_file:
                original_data = json.load(input_file)

            result = original_data[:] + result

        with open(output_filename, "w") as output_file:
            json.dump(result, output_file, indent=4, ensure_ascii=False)


main.add_command(parse)


if __name__ == "__main__":
    main()
