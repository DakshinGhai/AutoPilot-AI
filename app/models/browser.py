from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None


class ElementInfo(BaseModel):
    element_id: str

    tag: str

    id: Optional[str] = None
    class_name: Optional[str] = None
    name: Optional[str] = None

    role: Optional[str] = None

    aria_label: Optional[str] = None
    aria_labelledby: Optional[str] = None
    aria_describedby: Optional[str] = None

    accessible_name: str = ""
    accessible_description: str = ""
    label_text: str = ""

    placeholder: Optional[str] = None
    title: Optional[str] = None

    text: Optional[str] = None
    inner_text: Optional[str] = None
    value: Optional[str] = None

    href: Optional[str] = None
    type: Optional[str] = None
    alt: Optional[str] = None

    data_testid: Optional[str] = None
    data_test: Optional[str] = None
    data_cy: Optional[str] = None

    visible: bool = False
    enabled: bool = False

    bounding_box: Optional[BoundingBox] = None

    parent_tag: Optional[str] = None
    parent_text: Optional[str] = None

    nearby_text: Optional[str] = None

    dom_path: Optional[str] = None

    attributes: Dict[str, Any] = Field(default_factory=dict)


class PageInfo(BaseModel):
    url: str
    title: str

    elements: List[ElementInfo] = Field(default_factory=list)

    headings: List[ElementInfo] = Field(default_factory=list)

    buttons: List[ElementInfo] = Field(default_factory=list)

    links: List[ElementInfo] = Field(default_factory=list)

    inputs: List[ElementInfo] = Field(default_factory=list)

    textareas: List[ElementInfo] = Field(default_factory=list)

    selects: List[ElementInfo] = Field(default_factory=list)

    checkboxes: List[ElementInfo] = Field(default_factory=list)

    radio_buttons: List[ElementInfo] = Field(default_factory=list)

    forms: List[ElementInfo] = Field(default_factory=list)

    dialogs: List[ElementInfo] = Field(default_factory=list)

    menus: List[ElementInfo] = Field(default_factory=list)

    tabs: List[ElementInfo] = Field(default_factory=list)
