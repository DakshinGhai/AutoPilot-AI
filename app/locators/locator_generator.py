from typing import List

from app.models.browser import ElementInfo
from app.models.locator import LocatorCandidate
from app.models.semantic import SemanticEvidence


class LocatorGenerator:

    def generate(
        self,
        element: ElementInfo,
    ) -> List[LocatorCandidate]:

        candidates: List[LocatorCandidate] = []

        self._add_id_candidate(
            element,
            candidates,
        )

        self._add_testid_candidate(
            element,
            candidates,
        )

        self._add_role_candidate(
            element,
            candidates,
        )

        self._add_label_candidate(
            element,
            candidates,
        )

        self._add_placeholder_candidate(
            element,
            candidates,
        )

        self._add_text_candidate(
            element,
            candidates,
        )

        self._add_css_candidate(
            element,
            candidates,
        )

        self._add_xpath_candidate(
            element,
            candidates,
        )

        return self._remove_duplicates(candidates)

    # --------------------------------------------------
    # ID
    # --------------------------------------------------

    def _add_id_candidate(
        self,
        element: ElementInfo,
        candidates: List[LocatorCandidate],
    ):

        if not element.id:
            return

        candidates.append(
            LocatorCandidate(
                element_id=element.element_id,
                strategy="id",
                value=f"#{element.id}",
                locator_type="css",
                priority=1,
                reason="Stable DOM id attribute",
            )
        )

    # --------------------------------------------------
    # TEST ID
    # --------------------------------------------------

    def _add_testid_candidate(
        self,
        element: ElementInfo,
        candidates: List[LocatorCandidate],
    ):

        if element.data_testid:

            candidates.append(
                LocatorCandidate(
                    element_id=element.element_id,
                    strategy="testid",
                    value=element.data_testid,
                    locator_type="testid",
                    priority=2,
                    reason="data-testid attribute",
                )
            )

        if element.data_test:

            candidates.append(
                LocatorCandidate(
                    element_id=element.element_id,
                    strategy="data-test",
                    value=element.data_test,
                    locator_type="css",
                    priority=3,
                    reason="data-test attribute",
                )
            )

        if element.data_cy:

            candidates.append(
                LocatorCandidate(
                    element_id=element.element_id,
                    strategy="data-cy",
                    value=element.data_cy,
                    locator_type="css",
                    priority=4,
                    reason="data-cy attribute",
                )
            )

    # --------------------------------------------------
    # ROLE
    # --------------------------------------------------
    def _add_role_candidate(
        self,
        element: ElementInfo,
        candidates: List[LocatorCandidate],
    ) -> None:

        if not element.role:
            return

        # A semantic role locator must be based on a real
        # accessible name. Do not fall back to raw descendant
        # text because containers can contain unrelated text
        # from many child elements.
        name = element.accessible_name

        if not name:
            return

        name = name.strip()

        if not name:
            return

        # Avoid generating role locators from excessively
        # large accessible names.
        if len(name) > 150:
            return
        semantic_evidence = self._build_semantic_evidence(element)
        candidates.append(
            LocatorCandidate(
                element_id=element.element_id,
                strategy="role",
                value=f"{element.role.strip()}:{name}",
                locator_type="role",
                priority=5,
                reason="Semantic role with accessible name",
                semantic_role=element.role.strip(),
                accessible_name=name,
                evidence_source=self._get_accessibility_evidence(element),
                semantic_evidence=semantic_evidence,
            )
        )

    def _add_placeholder_candidate(
        self,
        element: ElementInfo,
        candidates: List[LocatorCandidate],
    ) -> None:

        if not element.placeholder:
            return

        placeholder = element.placeholder.strip()

        if not placeholder:
            return

        if len(placeholder) > 150:
            return
        semantic_evidence = self._build_semantic_evidence(element)
        candidates.append(
            LocatorCandidate(
                element_id=element.element_id,
                strategy="placeholder",
                value=placeholder,
                locator_type="placeholder",
                priority=7,
                reason="Input placeholder",
                semantic_role=element.role,
                accessible_name=element.accessible_name,
                evidence_source="placeholder",
                semantic_evidence=semantic_evidence,
            )
        )

    def _get_accessibility_evidence(
        self,
        element: ElementInfo,
    ) -> str:
        """
        Determine the strongest known source for the
        element's accessible name.

        This is deterministic metadata only.
        """

        if element.aria_label:
            return "aria-label"

        if element.aria_labelledby:
            return "aria-labelledby"

        if element.label_text:
            return "html-label"

        if element.accessible_name:
            if element.tag in {
                "button",
                "a",
                "option",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
            }:
                return "native-element-text"

            return "computed-accessible-name"

        return "none"

    # --------------------------------------------------
    # LABEL
    # --------------------------------------------------
    def _add_label_candidate(
        self,
        element: ElementInfo,
        candidates: List[LocatorCandidate],
    ) -> None:

        # --------------------------------------------------
        # HTML LABEL
        # --------------------------------------------------

        if element.label_text:

            label_text = element.label_text.strip()

            if label_text and len(label_text) <= 150:
                semantic_evidence = self._build_semantic_evidence(element)
                candidates.append(
                    LocatorCandidate(
                        element_id=element.element_id,
                        strategy="label",
                        value=label_text,
                        locator_type="label",
                        priority=6,
                        reason="Associated HTML label",
                        semantic_role=element.role,
                        accessible_name=element.accessible_name,
                        evidence_source="html-label",
                        semantic_evidence=semantic_evidence,
                    )
                )
        # --------------------------------------------------
        # PLACEHOLDER
        # --------------------------------------------------

        # --------------------------------------------------
        # ARIA LABEL
        # --------------------------------------------------

        if element.aria_label:

            aria_label = element.aria_label.strip()

            if aria_label and len(aria_label) <= 150:
                semantic_evidence = self._build_semantic_evidence(element)
                candidates.append(
                    LocatorCandidate(
                        element_id=element.element_id,
                        strategy="aria-label",
                        value=aria_label,
                        locator_type="aria-label",
                        priority=6,
                        reason="ARIA label",
                        semantic_role=element.role,
                        accessible_name=element.accessible_name,
                        evidence_source="aria-label",
                        semantic_evidence=semantic_evidence,
                    )
                )

    # --------------------------------------------------
    # TEXT
    # --------------------------------------------------

    def _add_text_candidate(
        self,
        element: ElementInfo,
        candidates: List[LocatorCandidate],
    ):

        text = element.inner_text or element.text

        if not text:
            return

        text = text.strip()

        if not text:
            return

        if len(text) > 150:
            return
        semantic_evidence = self._build_semantic_evidence(element)
        candidates.append(
            LocatorCandidate(
                element_id=element.element_id,
                strategy="text",
                value=text,
                locator_type="text",
                priority=8,
                reason="Visible element text",
                semantic_role=element.role,
                accessible_name=element.accessible_name,
                evidence_source="visible-text",
                semantic_evidence=semantic_evidence,
            )
        )

    # --------------------------------------------------
    # CSS
    # --------------------------------------------------

    def _add_css_candidate(
        self,
        element: ElementInfo,
        candidates: List[LocatorCandidate],
    ):

        if element.id:

            return

        if element.tag and element.class_name:

            classes = [cls.strip() for cls in element.class_name.split() if cls.strip()]

            if classes:

                selector = element.tag + "".join(
                    f".{self._escape_css_class(cls)}" for cls in classes[:3]
                )

                candidates.append(
                    LocatorCandidate(
                        element_id=element.element_id,
                        strategy="css",
                        value=selector,
                        locator_type="css",
                        priority=9,
                        reason="Tag and CSS class combination",
                    )
                )

    # --------------------------------------------------
    # XPATH
    # --------------------------------------------------

    def _add_xpath_candidate(
        self,
        element: ElementInfo,
        candidates: List[LocatorCandidate],
    ):

        if not element.dom_path:
            return

        xpath = self._dom_path_to_xpath(element.dom_path)

        if not xpath:
            return

        candidates.append(
            LocatorCandidate(
                element_id=element.element_id,
                strategy="dom-path",
                value=xpath,
                locator_type="xpath",
                priority=10,
                reason="Generated from DOM path",
            )
        )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    @staticmethod
    def _escape_css_class(
        class_name: str,
    ) -> str:

        return (
            class_name.replace("\\", "\\\\")
            .replace(".", "\\.")
            .replace(":", "\\:")
            .replace("[", "\\[")
            .replace("]", "\\]")
        )

    @staticmethod
    def _dom_path_to_xpath(
        dom_path: str,
    ) -> str:

        if not dom_path:
            return ""

        parts = [part.strip() for part in dom_path.split(">") if part.strip()]

        xpath_parts = []

        for part in parts:

            if ":nth-of-type(" in part:

                tag = part.split(":nth-of-type(")[0]

                index = part.split(":nth-of-type(")[1].rstrip(")")

                xpath_parts.append(f"{tag}[{index}]")

            elif "#" in part:

                tag, element_id = part.split(
                    "#",
                    1,
                )

                xpath_parts.append(f"{tag}[@id='{element_id}']")

            else:

                xpath_parts.append(part)

        return "//" + "/".join(xpath_parts)

    @staticmethod
    def _remove_duplicates(
        candidates: List[LocatorCandidate],
    ) -> List[LocatorCandidate]:

        seen = set()

        unique_candidates = []

        for candidate in candidates:

            key = (
                candidate.locator_type,
                candidate.strategy,
                candidate.value,
            )

            if key in seen:
                continue

            seen.add(key)

            unique_candidates.append(candidate)

        return unique_candidates

    def _build_semantic_evidence(
        self,
        element: ElementInfo,
    ) -> SemanticEvidence:

        return SemanticEvidence(
            role=element.role,
            accessible_name=(element.accessible_name or ""),
            accessible_description=(
                getattr(
                    element,
                    "accessible_description",
                    "",
                )
                or ""
            ),
            name_source=self._get_accessibility_evidence(element),
            aria_label=element.aria_label,
            aria_labelledby=(element.aria_labelledby),
            aria_describedby=(
                getattr(
                    element,
                    "aria_describedby",
                    None,
                )
            ),
            label_text=(element.label_text or ""),
            placeholder=element.placeholder,
            visible_text=(element.inner_text or element.text or ""),
        )
