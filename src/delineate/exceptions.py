from typing import Any


class LinearAPIError(Exception):
    def __init__(self, errors: list[dict[str, Any]] | str) -> None:
        if isinstance(errors, str):
            super().__init__(errors)
        else:
            messages = [e.get("message", str(e)) for e in errors]
            super().__init__("; ".join(messages))
        self.errors = errors
