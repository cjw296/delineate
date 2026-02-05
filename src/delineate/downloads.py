import json
import re
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from .client import LinearClient

UPLOAD_URL_PATTERN = re.compile(r'!?\[([^\]]*)\]\((https://uploads\.linear\.app/[^)]+)\)')


def extract_upload_urls(text: str) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    for match in UPLOAD_URL_PATTERN.finditer(text):
        display_name = match.group(1)
        url = match.group(2)
        parsed = urlparse(url)
        base_url = urlunparse(parsed._replace(query="", fragment=""))
        results.append((display_name, base_url))
    return results


def _local_filename(url: str, display_name: str) -> str:
    parsed = urlparse(url)
    path_parts = parsed.path.rstrip("/").split("/")
    file_uuid = path_parts[-1][:8]
    name = display_name or file_uuid
    return f"{file_uuid}_{name}"


def download_file(client: LinearClient, url: str, display_name: str, dest_dir: Path) -> str:
    filename = _local_filename(url, display_name)
    dest = dest_dir / filename
    if dest.exists():
        return filename
    dest_dir.mkdir(parents=True, exist_ok=True)
    client.download(url, dest)
    return filename


def download_all(
    client: LinearClient, urls: list[tuple[str, str]], dest_dir: Path
) -> dict[str, str]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, str] = {}
    for display_name, base_url in urls:
        if base_url in manifest:
            continue
        filename = download_file(client, base_url, display_name, dest_dir)
        manifest[base_url] = filename
    return manifest


def write_manifest(manifest: dict[str, str], dest_dir: Path) -> None:
    manifest_path = dest_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
