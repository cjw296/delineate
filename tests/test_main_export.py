import json
from pathlib import Path

from pytest_httpx import HTTPXMock

from delineate.export import LatestData, entity_path

from .helpers import make_paginated_response, run_cli


def _make_auth_file(tmp_path: Path) -> Path:
    auth_file = tmp_path / ".delineate.json"
    auth_file.write_text(json.dumps({"api_key": "lin_api_test"}))
    return auth_file


class TestEntityPath:
    def test_basic(self, tmp_path: Path) -> None:
        path = entity_path(tmp_path, "issues", "a01126f0-8a0a-4c98-ac24-b15a7706d048")
        assert path == tmp_path / "issues" / "a011" / "a01126f0-8a0a-4c98-ac24-b15a7706d048.json"
        assert path.parent.exists()

    def test_different_prefix(self, tmp_path: Path) -> None:
        path = entity_path(tmp_path, "comments", "ff991234-0000-0000-0000-000000000000")
        assert path == tmp_path / "comments" / "ff99" / "ff991234-0000-0000-0000-000000000000.json"


class TestLatestData:
    def test_load_missing(self, tmp_path: Path) -> None:
        latest = LatestData.load(tmp_path / "latest.json")
        assert latest == {}

    def test_load_existing(self, tmp_path: Path) -> None:
        path = tmp_path / "latest.json"
        path.write_text(json.dumps({"issues": "2024-01-01T00:00:00Z"}))
        latest = LatestData.load(path)
        assert latest["issues"] == "2024-01-01T00:00:00Z"

    def test_save(self, tmp_path: Path) -> None:
        latest = LatestData({"issues": "2024-06-01T00:00:00Z"})
        path = tmp_path / "latest.json"
        latest.save(path)
        data = json.loads(path.read_text())
        assert data == {"issues": "2024-06-01T00:00:00Z"}


class TestExportCommand:
    def test_single_entity(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        auth_file = _make_auth_file(tmp_path)
        export_dir = tmp_path / "export"
        export_dir.mkdir()

        httpx_mock.add_response(
            json=make_paginated_response(
                "teams",
                [
                    {
                        "id": "83914fc0-4a65-463c-b1d3-ffe9e75070ab",
                        "name": "Engineering",
                        "key": "ENG",
                        "createdAt": "2024-01-01T00:00:00Z",
                        "updatedAt": "2024-01-01T00:00:00Z",
                    },
                ],
            ),
        )

        result = run_cli(
            "--auth", str(auth_file), "export", "--path", str(export_dir), "teams"
        )
        assert result.exit_code == 0

        entity_file = (
            export_dir
            / "teams"
            / "8391"
            / "83914fc0-4a65-463c-b1d3-ffe9e75070ab.json"
        )
        assert entity_file.exists()
        data = json.loads(entity_file.read_text())
        assert data["name"] == "Engineering"

    def test_unknown_entity(self, tmp_path: Path) -> None:
        auth_file = _make_auth_file(tmp_path)
        result = run_cli(
            "--auth", str(auth_file), "export", "nonexistent"
        )
        assert result.exit_code != 0

    def test_update_mode_saves_latest(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        auth_file = _make_auth_file(tmp_path)
        export_dir = tmp_path / "export"
        export_dir.mkdir()

        httpx_mock.add_response(
            json=make_paginated_response(
                "issues",
                [
                    {
                        "id": "a01126f0-8a0a-4c98-ac24-b15a7706d048",
                        "identifier": "ENG-1",
                        "title": "Test Issue",
                        "description": None,
                        "updatedAt": "2024-06-15T12:00:00Z",
                    },
                ],
            ),
        )

        result = run_cli(
            "--auth",
            str(auth_file),
            "export",
            "--path",
            str(export_dir),
            "--update",
            "issues",
        )
        assert result.exit_code == 0

        latest = LatestData.load(export_dir / "latest.json")
        assert latest["issues"] == "2024-06-15T12:00:00Z"

    def test_update_mode_uses_cursor(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        auth_file = _make_auth_file(tmp_path)
        export_dir = tmp_path / "export"
        export_dir.mkdir()

        latest_path = export_dir / "latest.json"
        latest_path.write_text(json.dumps({"issues": "2024-01-01T00:00:00Z"}))

        httpx_mock.add_response(
            json=make_paginated_response(
                "issues",
                [
                    {
                        "id": "a01126f0-8a0a-4c98-ac24-b15a7706d048",
                        "identifier": "ENG-1",
                        "title": "Updated Issue",
                        "description": None,
                        "updatedAt": "2024-06-20T12:00:00Z",
                    },
                ],
            ),
        )

        result = run_cli(
            "--auth",
            str(auth_file),
            "export",
            "--path",
            str(export_dir),
            "--update",
            "issues",
        )
        assert result.exit_code == 0

        request = httpx_mock.get_request()
        assert request is not None
        body = json.loads(request.content)
        assert body["variables"]["filter"] == {
            "updatedAt": {"gt": "2024-01-01T00:00:00Z"}
        }

        latest = LatestData.load(latest_path)
        assert latest["issues"] == "2024-06-20T12:00:00Z"

    def test_entity_overwrite_on_update(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        auth_file = _make_auth_file(tmp_path)
        export_dir = tmp_path / "export"
        export_dir.mkdir()

        entity_dir = export_dir / "teams" / "8391"
        entity_dir.mkdir(parents=True)
        entity_file = entity_dir / "83914fc0-4a65-463c-b1d3-ffe9e75070ab.json"
        entity_file.write_text(json.dumps({"id": "83914fc0-4a65-463c-b1d3-ffe9e75070ab", "name": "Old"}))

        httpx_mock.add_response(
            json=make_paginated_response(
                "teams",
                [
                    {
                        "id": "83914fc0-4a65-463c-b1d3-ffe9e75070ab",
                        "name": "Renamed",
                        "updatedAt": "2024-06-01T00:00:00Z",
                    },
                ],
            ),
        )

        result = run_cli(
            "--auth", str(auth_file), "export", "--path", str(export_dir), "teams"
        )
        assert result.exit_code == 0

        data = json.loads(entity_file.read_text())
        assert data["name"] == "Renamed"

    def test_export_with_markdown_downloads(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        auth_file = _make_auth_file(tmp_path)
        export_dir = tmp_path / "export"
        export_dir.mkdir()

        httpx_mock.add_response(
            json=make_paginated_response(
                "issues",
                [
                    {
                        "id": "a01126f0-8a0a-4c98-ac24-b15a7706d048",
                        "identifier": "ENG-1",
                        "title": "Issue with image",
                        "description": "See ![screenshot](https://uploads.linear.app/ws/uuid/abcd1234?signature=jwt)",
                        "updatedAt": "2024-06-15T12:00:00Z",
                    },
                ],
            ),
        )
        httpx_mock.add_response(content=b"png image data")

        result = run_cli(
            "--auth",
            str(auth_file),
            "export",
            "--path",
            str(export_dir),
            "issues",
        )
        assert result.exit_code == 0

        files_dir = export_dir / "files"
        assert (files_dir / "abcd1234_screenshot").exists()
        assert (files_dir / "manifest.json").exists()
        manifest = json.loads((files_dir / "manifest.json").read_text())
        assert "https://uploads.linear.app/ws/uuid/abcd1234" in manifest
