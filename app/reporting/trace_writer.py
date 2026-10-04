import json
from pathlib import Path

from app.models.trace import ExecutionTrace


class ExecutionTraceWriter:
    """Persist execution traces as JSON artifacts."""

    def save(
        self,
        trace: ExecutionTrace,
        output_path: str | Path,
    ) -> Path:
        path = Path(output_path)

        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(
                trace.model_dump(mode="json"),
                file,
                indent=2,
                ensure_ascii=False,
            )

        return path
