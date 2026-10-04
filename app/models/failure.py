from typing import List, Optional

from pydantic import BaseModel


class DOMEvidence(BaseModel):
    element_id: str
    tag: str

    role: Optional[str] = None
    accessible_name: Optional[str] = None

    text: Optional[str] = None
    label_text: Optional[str] = None
    placeholder: Optional[str] = None

    element_id_attribute: Optional[str] = None
    name: Optional[str] = None

    visible: bool = False
    enabled: bool = False

    dom_path: Optional[str] = None


class FailureEvidence(BaseModel):
    error_message: str

    failure_type: str

    page_url: Optional[str] = None
    page_title: Optional[str] = None

    action: Optional[str] = None
    target: Optional[str] = None

    locator_type: Optional[str] = None
    locator_value: Optional[str] = None

    match_count: Optional[int] = None
    is_unique: Optional[bool] = None
    is_visible: Optional[bool] = None
    is_enabled: Optional[bool] = None
    is_valid: Optional[bool] = None

    dom_evidence: List[DOMEvidence] = []


class FailureContext(BaseModel):
    test_case_id: str
    test_case_name: str

    step: int
    action: str
    target: Optional[str] = None

    evidence: FailureEvidence
