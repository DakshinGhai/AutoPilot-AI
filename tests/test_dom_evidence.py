from app.models.browser import ElementInfo
from app.recovery.dom_evidence import DOMEvidenceExtractor


def create_element(index: int) -> ElementInfo:
    return ElementInfo(
        element_id=f"element_{index}",
        tag="button",
        id=f"button-{index}",
        class_name="test-button",
        name=None,
        role="button",
        aria_label=None,
        aria_labelledby=None,
        aria_describedby=None,
        accessible_name=f"Button {index}",
        accessible_description="",
        label_text="",
        placeholder=None,
        title=None,
        text=f"Button {index}",
        inner_text=f"Button {index}",
        value=None,
        href=None,
        type=None,
        alt=None,
        data_testid=None,
        data_test=None,
        data_cy=None,
        visible=True,
        enabled=True,
        bounding_box=None,
        parent_tag="div",
        parent_text=None,
        nearby_text=None,
        dom_path=f"/html/body/button[{index}]",
        attributes={},
    )


def test_dom_evidence_preserves_element_information():

    element = create_element(1)

    extractor = DOMEvidenceExtractor()

    result = extractor.extract([element])

    assert len(result) == 1

    evidence = result[0]

    assert evidence.element_id == "element_1"
    assert evidence.tag == "button"
    assert evidence.role == "button"
    assert evidence.accessible_name == "Button 1"
    assert evidence.text == "Button 1"
    assert evidence.visible is True
    assert evidence.enabled is True


def test_dom_evidence_is_bounded():

    elements = [create_element(index) for index in range(100)]

    extractor = DOMEvidenceExtractor(max_elements=30)

    result = extractor.extract(elements)

    assert len(result) == 30

    assert result[0].element_id == "element_0"
    assert result[-1].element_id == "element_29"


def test_dom_evidence_supports_custom_limit():

    elements = [create_element(index) for index in range(20)]

    extractor = DOMEvidenceExtractor(max_elements=5)

    result = extractor.extract(elements)

    assert len(result) == 5


def test_dom_evidence_prioritizes_accessible_name_match():

    elements = [
        create_element(1),
        create_element(2),
        create_element(3),
    ]

    elements[0].accessible_name = "Search"
    elements[1].accessible_name = "Product"
    elements[2].accessible_name = "Cart"

    extractor = DOMEvidenceExtractor(max_elements=3)

    result = extractor.extract(
        elements,
        target="Product",
    )

    assert result[0].accessible_name == "Product"


def test_dom_evidence_prioritizes_visible_text_match():

    elements = [
        create_element(1),
        create_element(2),
    ]

    elements[0].accessible_name = "Search"
    elements[0].text = "Search"

    elements[1].accessible_name = "Product"
    elements[1].text = "Product"

    extractor = DOMEvidenceExtractor(max_elements=2)

    result = extractor.extract(
        elements,
        target="Product",
    )

    assert result[0].text == "Product"


def test_dom_evidence_prioritizes_label_match():

    elements = [
        create_element(1),
        create_element(2),
    ]

    elements[0].label_text = "Search"
    elements[1].label_text = "Product"

    extractor = DOMEvidenceExtractor(max_elements=2)

    result = extractor.extract(
        elements,
        target="Product",
    )

    assert result[0].label_text == "Product"


def test_dom_evidence_keeps_bounded_result_after_ranking():

    elements = [create_element(index) for index in range(100)]

    elements[75].accessible_name = "Product"

    extractor = DOMEvidenceExtractor(max_elements=10)

    result = extractor.extract(
        elements,
        target="Product",
    )

    assert len(result) == 10

    assert result[0].accessible_name == "Product"
