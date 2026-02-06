from pathlib import Path

from pytest_httpx import HTTPXMock

from delineate.client import LinearClient
from delineate.downloads import (
    download_all,
    download_file,
    extract_upload_urls,
    write_manifest,
)


class TestExtractUploadUrls:
    def test_image(self) -> None:
        text = "Here is ![screenshot](https://uploads.linear.app/ws/uuid1/file1?signature=jwt123)"
        result = extract_upload_urls(text)
        assert result == [("screenshot", "https://uploads.linear.app/ws/uuid1/file1")]

    def test_file_link(self) -> None:
        text = "Download [report.pdf](https://uploads.linear.app/ws/uuid2/file2?signature=jwt456)"
        result = extract_upload_urls(text)
        assert result == [("report.pdf", "https://uploads.linear.app/ws/uuid2/file2")]

    def test_strips_signature(self) -> None:
        text = "![img](https://uploads.linear.app/ws/uuid3/file3?signature=abc&other=def)"
        result = extract_upload_urls(text)
        assert result == [("img", "https://uploads.linear.app/ws/uuid3/file3")]

    def test_no_matches(self) -> None:
        text = "No uploads here, just [a link](https://example.com/file.pdf)"
        result = extract_upload_urls(text)
        assert result == []

    def test_multiple(self) -> None:
        text = (
            "![img1](https://uploads.linear.app/ws/u1/f1?signature=a) "
            "and [doc.pdf](https://uploads.linear.app/ws/u2/f2?signature=b)"
        )
        result = extract_upload_urls(text)
        assert result == [
            ("img1", "https://uploads.linear.app/ws/u1/f1"),
            ("doc.pdf", "https://uploads.linear.app/ws/u2/f2"),
        ]

    def test_no_signature(self) -> None:
        text = "![img](https://uploads.linear.app/ws/uuid/fileid)"
        result = extract_upload_urls(text)
        assert result == [("img", "https://uploads.linear.app/ws/uuid/fileid")]

    def test_empty_alt(self) -> None:
        text = "![](https://uploads.linear.app/ws/uuid/abcd1234?signature=jwt)"
        result = extract_upload_urls(text)
        assert result == [("", "https://uploads.linear.app/ws/uuid/abcd1234")]


class TestDownloadFile:
    def test_download(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        httpx_mock.add_response(content=b"pdf contents")
        client = LinearClient(api_key="lin_api_test")
        filename = download_file(
            client,
            "https://uploads.linear.app/ws/uuid/abcd1234",
            "report.pdf",
            tmp_path,
        )
        assert filename == "abcd1234_report.pdf"
        assert (tmp_path / "abcd1234_report.pdf").read_bytes() == b"pdf contents"

    def test_skip_existing(self, tmp_path: Path) -> None:
        dest_dir = tmp_path
        existing = dest_dir / "abcd1234_report.pdf"
        existing.write_bytes(b"old contents")
        client = LinearClient(api_key="lin_api_test")
        filename = download_file(
            client,
            "https://uploads.linear.app/ws/uuid/abcd1234",
            "report.pdf",
            dest_dir,
        )
        assert filename == "abcd1234_report.pdf"
        assert existing.read_bytes() == b"old contents"

    def test_empty_display_name(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        httpx_mock.add_response(content=b"data")
        client = LinearClient(api_key="lin_api_test")
        filename = download_file(
            client,
            "https://uploads.linear.app/ws/uuid/abcd1234",
            "",
            tmp_path,
        )
        assert filename == "abcd1234_abcd1234"

    def test_http_error(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        httpx_mock.add_response(status_code=401)
        client = LinearClient(api_key="lin_api_test")
        filename = download_file(
            client,
            "https://uploads.linear.app/ws/uuid/abcd1234",
            "report.pdf",
            tmp_path,
        )
        assert filename is None
        assert not (tmp_path / "abcd1234_report.pdf").exists()


class TestDownloadAll:
    def test_basic(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        httpx_mock.add_response(content=b"file1 data")
        httpx_mock.add_response(content=b"file2 data")
        client = LinearClient(api_key="lin_api_test")
        urls = [
            ("img.png", "https://uploads.linear.app/ws/u1/aaaa1111"),
            ("doc.pdf", "https://uploads.linear.app/ws/u2/bbbb2222"),
        ]
        manifest = download_all(client, urls, tmp_path / "files")
        assert manifest == {
            "https://uploads.linear.app/ws/u1/aaaa1111": "aaaa1111_img.png",
            "https://uploads.linear.app/ws/u2/bbbb2222": "bbbb2222_doc.pdf",
        }
        assert (tmp_path / "files" / "aaaa1111_img.png").read_bytes() == b"file1 data"
        assert (tmp_path / "files" / "bbbb2222_doc.pdf").read_bytes() == b"file2 data"

    def test_dedup(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        httpx_mock.add_response(content=b"data")
        client = LinearClient(api_key="lin_api_test")
        urls = [
            ("img.png", "https://uploads.linear.app/ws/u1/aaaa1111"),
            ("img.png", "https://uploads.linear.app/ws/u1/aaaa1111"),
        ]
        manifest = download_all(client, urls, tmp_path / "files")
        assert len(manifest) == 1

    def test_with_failures(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        httpx_mock.add_response(content=b"file1 data")
        httpx_mock.add_response(status_code=401)
        httpx_mock.add_response(content=b"file3 data")
        client = LinearClient(api_key="lin_api_test")
        urls = [
            ("img.png", "https://uploads.linear.app/ws/u1/aaaa1111"),
            ("bad.pdf", "https://uploads.linear.app/ws/u2/bbbb2222"),
            ("doc.txt", "https://uploads.linear.app/ws/u3/cccc3333"),
        ]
        manifest = download_all(client, urls, tmp_path / "files")
        assert manifest == {
            "https://uploads.linear.app/ws/u1/aaaa1111": "aaaa1111_img.png",
            "https://uploads.linear.app/ws/u3/cccc3333": "cccc3333_doc.txt",
        }
        assert (tmp_path / "files" / "aaaa1111_img.png").read_bytes() == b"file1 data"
        assert not (tmp_path / "files" / "bbbb2222_bad.pdf").exists()
        assert (tmp_path / "files" / "cccc3333_doc.txt").read_bytes() == b"file3 data"


class TestWriteManifest:
    def test_write(self, tmp_path: Path) -> None:
        files_dir = tmp_path / "files"
        files_dir.mkdir()
        manifest = {"https://uploads.linear.app/ws/u1/f1": "f1_img.png"}
        write_manifest(manifest, files_dir)
        written = (files_dir / "manifest.json").read_text()
        assert '"https://uploads.linear.app/ws/u1/f1"' in written
        assert '"f1_img.png"' in written
