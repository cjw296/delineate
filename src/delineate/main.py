import json
import logging
from pathlib import Path

import click
import enlighten

from .client import LinearClient, client_from_auth
from .downloads import download_all, extract_upload_urls
from .exceptions import LinearAPIError
from .export import EXPORTS, LatestData, write_entity
from .queries import VIEWER


@click.group()
@click.option(
    '--auth',
    'auth_path',
    type=click.Path(path_type=Path),
    default=Path('.delineate.json'),
    help='Path to the authentication file.',
)
@click.option(
    '-l',
    '--log-level',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
    default='WARNING',
)
@click.pass_context
def cli(ctx: click.Context, auth_path: Path, log_level: str) -> None:
    ctx.obj = auth_path
    logging.basicConfig(level=getattr(logging, log_level))


@cli.command()
def version() -> None:
    """Show the version."""
    from importlib.metadata import version as get_version

    click.echo(get_version('delineate'))


@cli.command()
@click.pass_context
def auth(ctx: click.Context) -> None:
    """Authenticate with Linear."""
    api_key = click.prompt("Enter your Linear API key", hide_input=True)
    client = LinearClient(api_key=api_key)
    try:
        result = client.query(VIEWER)
    except LinearAPIError as e:
        raise click.ClickException(f"Authentication failed: {e}") from e
    viewer = result["viewer"]
    click.echo(f"Authenticated as {viewer['name']} ({viewer['email']})")
    auth_path: Path = ctx.obj
    auth_path.write_text(json.dumps({"api_key": api_key}, indent=2) + "\n")
    click.echo(f"Credentials saved to {auth_path}")


@cli.command()
@click.pass_context
def whoami(ctx: click.Context) -> None:
    """Show the authenticated user."""
    client = client_from_auth(ctx.obj)
    result = client.query(VIEWER)
    viewer = result["viewer"]
    click.echo(f"{viewer['name']} ({viewer['email']})")


@cli.command()
@click.argument('entities', nargs=-1)
@click.option(
    '--path',
    'export_path',
    type=click.Path(path_type=Path),
    default=Path('.'),
    help='Output directory for exported data.',
)
@click.option(
    '--update',
    is_flag=True,
    help='Incremental update mode using latest.json cursors.',
)
@click.pass_context
def export(
    ctx: click.Context,
    entities: tuple[str, ...],
    export_path: Path,
    update: bool,
) -> None:
    """
    Export data from Linear.

    Optionally specify entity types to export (e.g. issues comments).
    If none specified, all entity types are exported.
    """
    client = client_from_auth(ctx.obj)
    latest_path = export_path / "latest.json"
    latest = LatestData.load(latest_path) if update else LatestData()

    exports_to_run = EXPORTS
    if entities:
        unknown = set(entities) - set(EXPORTS)
        if unknown:
            raise click.BadParameter(f"Unknown entities: {', '.join(sorted(unknown))}")
        exports_to_run = {name: EXPORTS[name] for name in entities}

    all_upload_urls: list[tuple[str, str]] = []
    manager = enlighten.get_manager()

    try:
        for name, exp in exports_to_run.items():
            counter = manager.counter(desc=name, unit="entities")
            for entity in exp.items(client, latest):
                write_entity(export_path, exp.entity_type, entity)
                for field_name in exp.markdown_fields:
                    text: str | None = entity.get(field_name)
                    if text:
                        all_upload_urls.extend(extract_upload_urls(text))
                counter.update()
            counter.close()

        if all_upload_urls:
            files_dir = export_path / "files"
            download_counter = manager.counter(
                desc="files", unit="files", total=len(all_upload_urls)
            )
            download_all(client, all_upload_urls, files_dir)
            download_counter.update(len(all_upload_urls))
            download_counter.close()
    finally:
        manager.stop()

    latest.save(latest_path)
