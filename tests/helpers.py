from typing import Any

from click.testing import CliRunner, Result

from delineate.main import cli


def run_cli(*args: str, input: str | None = None) -> Result:
    runner = CliRunner()
    return runner.invoke(cli, list(args), input=input, catch_exceptions=False)


def make_paginated_response(
    connection_path: str,
    nodes: list[dict[str, Any]],
    has_next: bool = False,
    end_cursor: str | None = None,
) -> dict[str, Any]:
    return {
        "data": {
            connection_path: {
                "nodes": nodes,
                "pageInfo": {
                    "hasNextPage": has_next,
                    "endCursor": end_cursor,
                },
            }
        }
    }
