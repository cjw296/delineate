import json
from pathlib import Path

from pytest_httpx import HTTPXMock

from .helpers import run_cli


class TestAuth:
    def test_auth(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        httpx_mock.add_response(
            json={
                "data": {
                    "viewer": {
                        "id": "user-123",
                        "name": "Test User",
                        "email": "test@example.com",
                    }
                }
            },
        )
        auth_file = tmp_path / ".delineate.json"
        result = run_cli(
            "--auth", str(auth_file), "auth", input="lin_api_test\n"
        )
        assert result.exit_code == 0
        assert "Authenticated as Test User" in result.output
        assert auth_file.exists()
        data = json.loads(auth_file.read_text())
        assert data["api_key"] == "lin_api_test"

    def test_auth_invalid_key(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        httpx_mock.add_response(
            json={
                "errors": [{"message": "Authentication required"}]
            },
        )
        auth_file = tmp_path / ".delineate.json"
        result = run_cli(
            "--auth", str(auth_file), "auth", input="bad_key\n"
        )
        assert result.exit_code != 0
        assert "Authentication failed" in result.output
        assert not auth_file.exists()


class TestWhoami:
    def test_whoami(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        httpx_mock.add_response(
            json={
                "data": {
                    "viewer": {
                        "id": "user-123",
                        "name": "Test User",
                        "email": "test@example.com",
                    }
                }
            },
        )
        auth_file = tmp_path / ".delineate.json"
        auth_file.write_text(json.dumps({"api_key": "lin_api_test"}))
        result = run_cli("--auth", str(auth_file), "whoami")
        assert result.exit_code == 0
        assert "Test User (test@example.com)" in result.output
