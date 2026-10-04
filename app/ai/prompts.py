import json

from app.models.ai import LocatorSelectionRequest

SYSTEM_INSTRUCTION = """
You are a locator selection engine for a Playwright-based test automation framework.

Your job is ONLY to select the best locator candidate from the candidates provided.

STRICT RULES:

1. You MUST select an existing candidate_id.
2. NEVER invent a locator.
3. NEVER modify a locator value.
4. NEVER create XPath, CSS, text, role, label, or any other selector yourself.
5. Prefer candidates that are:
   - valid
   - unique
   - visible
   - enabled
   - semantically meaningful
   - supported by strong accessibility evidence
6. Use the test step and target description to understand which element is intended.
7. If several candidates identify the same element, choose the most resilient candidate.
8. Do not select a candidate that is not present in the supplied candidate list.
9. Return only the requested structured response.
"""


def build_locator_selection_prompt(
    request: LocatorSelectionRequest,
) -> str:
    payload = {
        "test_step": request.test_step,
        "target": request.target,
        "page_url": request.page_url,
        "page_title": request.page_title,
        "candidates": [
            candidate.model_dump(mode="json") for candidate in request.candidates
        ],
    }

    return (
        SYSTEM_INSTRUCTION
        + "\n\nBrowser-backed locator candidates:\n"
        + json.dumps(payload, indent=2)
    )
