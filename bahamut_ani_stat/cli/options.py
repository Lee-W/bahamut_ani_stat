from __future__ import annotations

from typing import TYPE_CHECKING, Any

import click

if TYPE_CHECKING:
    from collections.abc import Callable


def print_output_option(function: Callable[..., Any]) -> Callable[..., Any]:
    function = click.option(
        "--print-output",
        default=True,
        help="print result to screen",
        flag_value="print-output",
    )(function)
    return function


def outputfile_option(function: Callable[..., Any]) -> Callable[..., Any]:
    function = click.option(
        "--overwrite",
        "handle_exist_output",
        help="Overwrite file if the output file already exists",
        flag_value="overwrite",
    )(function)
    function = click.option(
        "--append",
        "handle_exist_output",
        help="Append data if the output file already exists",
        default=True,
        flag_value="append",
    )(function)
    function = click.option(
        "--output-filename",
        help="Output to file only if --output-filename is provided",
        default=None,
        type=str,
    )(function)
    return function
