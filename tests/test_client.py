from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock
from testfixtures import Replacer

from delineate.client import LinearClient
from delineate.exceptions import LinearAPIError

from .helpers import make_paginated_response


class TestQuery:
    def test_basic(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json={"data": {"viewer": {"id": "123", "name": "Test"}}},
        )
        client = LinearClient(api_key="lin_api_test")
        result = client.query("{ viewer { id name } }")
        assert result == {"viewer": {"id": "123", "name": "Test"}}

    def test_rate_limit_retry(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json={
                "errors": [
                    {
                        "message": "Rate limited",
                        "extensions": {"code": "RATELIMITED"},
                    }
                ]
            },
        )
        httpx_mock.add_response(
            json={"data": {"viewer": {"id": "123"}}},
        )
        client = LinearClient(api_key="lin_api_test")
        with Replacer() as r:
            r.replace("time.sleep", lambda x: None)
            result = client.query("{ viewer { id } }")
        assert result == {"viewer": {"id": "123"}}

    def test_rate_limit_exhausted(self, httpx_mock: HTTPXMock) -> None:
        for _ in range(3):
            httpx_mock.add_response(
                json={
                    "errors": [
                        {
                            "message": "Rate limited",
                            "extensions": {"code": "RATELIMITED"},
                        }
                    ]
                },
            )
        client = LinearClient(api_key="lin_api_test")
        with Replacer() as r:
            r.replace("time.sleep", lambda x: None)
            with pytest.raises(LinearAPIError, match="Rate limited after max retries"):
                client.query("{ viewer { id } }")

    def test_graphql_error(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json={
                "errors": [
                    {"message": "Field 'foo' not found on type 'Query'"}
                ]
            },
        )
        client = LinearClient(api_key="lin_api_test")
        with pytest.raises(LinearAPIError, match="Field 'foo' not found"):
            client.query("{ foo }")


class TestPaginate:
    def test_single_page(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json=make_paginated_response(
                "issues",
                [{"id": "1", "title": "First"}, {"id": "2", "title": "Second"}],
            ),
        )
        client = LinearClient(api_key="lin_api_test")
        results = list(client.paginate("query", "issues"))
        assert results == [{"id": "1", "title": "First"}, {"id": "2", "title": "Second"}]

    def test_multiple_pages(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json=make_paginated_response(
                "issues",
                [{"id": "1", "title": "First"}],
                has_next=True,
                end_cursor="cursor1",
            ),
        )
        httpx_mock.add_response(
            json=make_paginated_response(
                "issues",
                [{"id": "2", "title": "Second"}],
            ),
        )
        client = LinearClient(api_key="lin_api_test")
        results = list(client.paginate("query", "issues"))
        assert results == [{"id": "1", "title": "First"}, {"id": "2", "title": "Second"}]


class TestDownload:
    def test_download(self, httpx_mock: HTTPXMock, tmp_path: Path) -> None:
        httpx_mock.add_response(content=b"file contents here")
        client = LinearClient(api_key="lin_api_test")
        dest = tmp_path / "test_file.bin"
        client.download("https://uploads.linear.app/ws/uuid/file-uuid", dest)
        assert dest.read_bytes() == b"file contents here"
