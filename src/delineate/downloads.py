import json
import logging
import re
import tempfile
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import httpx

from .client import LinearClient

logger = logging.getLogger(__name__)

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


def _file_uuid(url: str) -> str:
    parsed = urlparse(url)
    path_parts = parsed.path.rstrip("/").split("/")
    return path_parts[-1]


def file_dir(base_dir: Path, url: str) -> Path:
    uuid = _file_uuid(url)
    prefix = uuid[:4]
    return base_dir / prefix / uuid


def download_file(
    client: LinearClient, url: str, display_name: str, dest_dir: Path
) -> str | None:
    filename = display_name or "file"
    file_directory = file_dir(dest_dir, url)
    dest = file_directory / filename
    if dest.exists():
        return filename
    # Download to temp file first, only create directory on success
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
        client.download(url, tmp_path)
    except httpx.HTTPStatusError as e:
        logger.warning("Failed to download %s: %s", url, e.response.status_code)
        tmp_path.unlink(missing_ok=True)
        return None
    file_directory.mkdir(parents=True, exist_ok=True)
    tmp_path.rename(dest)
    return filename


def load_manifest(dest_dir: Path) -> set[str]:
    manifest_path = dest_dir / "manifest.jsonl"
    urls: set[str] = set()
    if manifest_path.exists():
        for line in manifest_path.read_text().splitlines():
            if line.strip():
                entry = json.loads(line)
                urls.add(entry["url"])
    return urls


def append_manifest(dest_dir: Path, url: str, filename: str) -> None:
    manifest_path = dest_dir / "manifest.jsonl"
    entry = json.dumps({"url": url, "filename": filename})
    with manifest_path.open("a") as f:
        f.write(entry + "\n")


def download_all(
    client: LinearClient, urls: list[tuple[str, str]], dest_dir: Path
) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    already_downloaded = load_manifest(dest_dir)
    for display_name, base_url in urls:
        if base_url in already_downloaded:
            continue
        filename = download_file(client, base_url, display_name, dest_dir)
        if filename is not None:
            append_manifest(dest_dir, base_url, filename)
            already_downloaded.add(base_url)
