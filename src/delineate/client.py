import json
import logging
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

from .exceptions import LinearAPIError

logger = logging.getLogger(__name__)

GRAPHQL_URL = "https://api.linear.app/graphql"
MAX_RETRIES = 3


@dataclass
class LinearClient:
    api_key: str
    _http: httpx.Client = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._http = httpx.Client(
            headers={"Authorization": self.api_key},
        )

    def query(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        for attempt in range(MAX_RETRIES):
            response = self._http.post(GRAPHQL_URL, json=payload)
            data: dict[str, Any] = response.json()

            if "errors" in data:
                errors: list[dict[str, Any]] = data["errors"]
                if any(e.get("extensions", {}).get("code") == "RATELIMITED" for e in errors):
                    wait = 2**attempt
                    logger.warning("Rate limited, retrying in %ds...", wait)
                    time.sleep(wait)
                    continue
                raise LinearAPIError(errors)

            response.raise_for_status()
            result: dict[str, Any] = data["data"]
            return result

        raise LinearAPIError("Rate limited after max retries")

    def paginate(
        self,
        query: str,
        connection_path: str,
        variables: dict[str, Any] | None = None,
        page_size: int = 100,
    ) -> Iterator[dict[str, Any]]:
        variables = dict(variables or {})
        variables["first"] = page_size
        while True:
            result = self.query(query, variables)
            connection = result[connection_path]
            yield from connection["nodes"]
            page_info = connection["pageInfo"]
            if not page_info["hasNextPage"]:
                break
            variables["after"] = page_info["endCursor"]

    def download(self, url: str, dest: Path) -> None:
        with self._http.stream("GET", url) as response:
            response.raise_for_status()
            with dest.open("wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)


def client_from_auth(path: Path) -> LinearClient:
    data = json.loads(path.read_text())
    return LinearClient(api_key=data["api_key"])
