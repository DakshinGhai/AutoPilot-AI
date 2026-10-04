import re
from typing import Dict


class TestDataManager:

    PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_.-]+)\s*\}\}")

    def __init__(self, data: Dict[str, str] | None = None):
        self.data = data or {}

    def resolve(self, value: str | None) -> str | None:

        if value is None:
            return None

        def replace(match):
            key = match.group(1)

            if key not in self.data:
                raise KeyError(f"Test data parameter not found: {key}")

            return str(self.data[key])

        return self.PLACEHOLDER_PATTERN.sub(replace, value)

    def add(self, key: str, value: str):
        self.data[key] = value

    def get(self, key: str):
        return self.data.get(key)
