from typing import Optional

from pydantic import BaseModel


class SemanticEvidence(BaseModel):
    role: Optional[str] = None
    accessible_name: str = ""
    accessible_description: str = ""

    name_source: Optional[str] = None

    aria_label: Optional[str] = None
    aria_labelledby: Optional[str] = None
    aria_describedby: Optional[str] = None

    label_text: str = ""

    placeholder: Optional[str] = None

    visible_text: str = ""
