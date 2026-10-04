from typing import Any, Dict, List

from playwright.async_api import Page

from app.models.browser import BoundingBox, ElementInfo


class DOMExtractor:

    INTERACTIVE_SELECTORS = """
        button,
        a,
        input,
        textarea,
        select,
        option,
        h1,
        h2,
        h3,
        h4,
        h5,
        h6,
        form,
        [role],
        [tabindex],
        [contenteditable="true"]
    """

    async def extract_elements(
        self,
        page: Page,
    ) -> List[ElementInfo]:

        locator = page.locator(self.INTERACTIVE_SELECTORS)

        count = await locator.count()

        print(f"DOM candidates found: {count}")

        elements: List[ElementInfo] = []

        for index in range(count):

            element = locator.nth(index)

            try:

                data: Dict[str, Any] = await element.evaluate("""
                        (element) => {

                            function cleanText(value) {

                                if (!value) {
                                    return "";
                                }

                                return value
                                    .replace(/\\s+/g, " ")
                                    .trim();
                            }


                            function getDirectText(element) {

                                const parts = [];

                                for (
                                    const node
                                    of element.childNodes
                                ) {

                                    if (
                                        node.nodeType ===
                                        Node.TEXT_NODE
                                    ) {

                                        const value =
                                            cleanText(
                                                node.textContent
                                            );

                                        if (value) {
                                            parts.push(value);
                                        }
                                    }
                                }

                                return cleanText(
                                    parts.join(" ")
                                );
                            }


                            function getLabelledByText(element) {

                                const ids =
                                    element.getAttribute(
                                        "aria-labelledby"
                                    );

                                if (!ids) {
                                    return "";
                                }

                                const labels = [];

                                for (
                                    const id
                                    of ids.split(/\\s+/)
                                ) {

                                    const referenced =
                                        document.getElementById(
                                            id
                                        );

                                    if (!referenced) {
                                        continue;
                                    }

                                    const value =
                                        cleanText(
                                            referenced.innerText ||
                                            referenced.textContent ||
                                            ""
                                        );

                                    if (value) {
                                        labels.push(value);
                                    }
                                }

                                return cleanText(
                                    labels.join(" ")
                                );
                            }
                            function getDescribedByText(element) {

                                const ids =
                                    element.getAttribute(
                                        "aria-describedby"
                                    );

                                if (!ids) {
                                    return "";
                                }

                                const descriptions = [];

                                for (
                                    const id
                                    of ids.split(/\s+/)
                                ) {

                                    const referenced =
                                        document.getElementById(
                                            id
                                        );

                                    if (!referenced) {
                                        continue;
                                    }

                                    const value =
                                        cleanText(
                                            referenced.innerText ||
                                            referenced.textContent ||
                                            ""
                                        );

                                    if (value) {
                                        descriptions.push(value);
                                    }
                                }

                                return cleanText(
                                    descriptions.join(" ")
                                );
                            }

                            function getAssociatedLabelText(element) {

                                const tag = element.tagName.toLowerCase();

                                if (
                                    tag !== "input" &&
                                    tag !== "textarea" &&
                                    tag !== "select"
                                ) {
                                    return "";
                                }

                                // Explicit label:
                                // <label for="email">Email Address</label>
                                // <input id="email">

                                const id = element.getAttribute("id");

                                if (id) {

                                    const label = document.querySelector(
                                        `label[for="${CSS.escape(id)}"]`
                                    );

                                    if (label) {

                                        const labelText = cleanText(
                                            label.innerText ||
                                            label.textContent ||
                                            ""
                                        );

                                        if (labelText) {
                                            return labelText;
                                        }
                                    }
                                }

                                // Wrapped label:
                                // <label>
                                //     Password
                                //     <input>
                                // </label>

                                const parentLabel = element.closest("label");

                                if (parentLabel) {

                                    const labelText = cleanText(
                                        parentLabel.innerText ||
                                        parentLabel.textContent ||
                                        ""
                                    );

                                    if (labelText) {
                                        return labelText;
                                    }
                                }

                                return "";
                            }
                            function getNativeAccessibleName(
                                element
                            ) {

                                const ariaLabel =
                                    cleanText(
                                        element.getAttribute(
                                            "aria-label"
                                        )
                                    );

                                if (ariaLabel) {
                                    return ariaLabel;
                                }


                                const labelledBy =
                                    getLabelledByText(
                                        element
                                    );

                                if (labelledBy) {
                                    return labelledBy;
                                }


                                const tag =
                                    element.tagName
                                        .toLowerCase();


                                /*
                                 * Inputs and form controls.
                                 *
                                 * Try associated <label>
                                 * before falling back to
                                 * placeholder/name.
                                 */

                                if (
                                    tag === "input" ||
                                    tag === "textarea" ||
                                    tag === "select"
                                ) {

                                    const id =
                                        element.getAttribute(
                                            "id"
                                        );

                                    if (id) {

                                        const label =
                                            document.querySelector(
                                                `label[for="${CSS.escape(id)}"]`
                                            );

                                        if (label) {

                                            const labelText =
                                                cleanText(
                                                    label.innerText ||
                                                    label.textContent ||
                                                    ""
                                                );

                                            if (labelText) {
                                                return labelText;
                                            }
                                        }
                                    }


                                    const parentLabel =
                                        element.closest(
                                            "label"
                                        );

                                    if (parentLabel) {

                                        const labelText =
                                            cleanText(
                                                parentLabel.innerText ||
                                                parentLabel.textContent ||
                                                ""
                                            );

                                        if (labelText) {
                                            return labelText;
                                        }
                                    }
                                }


                                /*
                                 * Buttons and links normally
                                 * use their own text.
                                 */

                                if (
                                    tag === "button" ||
                                    tag === "a"
                                ) {

                                    const directText =
                                        getDirectText(
                                            element
                                        );

                                    if (directText) {
                                        return directText;
                                    }

                                    const innerText =
                                        cleanText(
                                            element.innerText
                                        );

                                    if (innerText) {
                                        return innerText;
                                    }
                                }


                                /*
                                 * Headings use their visible text.
                                 */

                                if (
                                    /^h[1-6]$/.test(tag)
                                ) {

                                    return cleanText(
                                        element.innerText ||
                                        element.textContent ||
                                        ""
                                    );
                                }


                                /*
                                 * Generic elements with an
                                 * explicit ARIA role should
                                 * prefer short direct text.
                                 *
                                 * Do NOT use the complete
                                 * descendant text here.
                                 */

                                if (
                                    element.hasAttribute(
                                        "role"
                                    )
                                ) {

                                    const directText =
                                        getDirectText(
                                            element
                                        );

                                    if (directText) {
                                        return directText;
                                    }

                                    const title =
                                        cleanText(
                                            element.getAttribute(
                                                "title"
                                            )
                                        );

                                    if (title) {
                                        return title;
                                    }
                                }


                                return "";
                            }


                            /*
                             * Resolve the semantic/accessibility
                             * role of the element.
                             *
                             * Explicit ARIA role takes priority.
                             * If no explicit role exists, fall back
                             * to the native HTML semantics.
                             */

                            function getSemanticRole(element) {

                                const explicitRole =
                                    element.getAttribute("role");

                                if (explicitRole) {
                                    return explicitRole.trim();
                                }

                                const tag =
                                    element.tagName.toLowerCase();

                                switch (tag) {

                                    case "button":
                                        return "button";

                                    case "a":
                                        return element.hasAttribute(
                                            "href"
                                        )
                                            ? "link"
                                            : null;

                                    case "input": {

                                        const type =
                                            (
                                                element.getAttribute(
                                                    "type"
                                                ) ||
                                                "text"
                                            ).toLowerCase();

                                        switch (type) {

                                            case "button":
                                            case "submit":
                                            case "reset":
                                            case "image":
                                                return "button";

                                            case "checkbox":
                                                return "checkbox";

                                            case "radio":
                                                return "radio";

                                            case "search":
                                                return "searchbox";

                                            case "range":
                                                return "slider";

                                            default:
                                                return "textbox";
                                        }
                                    }

                                    case "textarea":
                                        return "textbox";

                                    case "select":
                                        return element.multiple
                                            ? "listbox"
                                            : "combobox";

                                    case "option":
                                        return "option";

                                    case "h1":
                                    case "h2":
                                    case "h3":
                                    case "h4":
                                    case "h5":
                                    case "h6":
                                        return "heading";

                                    case "img":
                                        return "img";

                                    case "nav":
                                        return "navigation";

                                    case "main":
                                        return "main";

                                    case "header":
                                        return "banner";

                                    case "footer":
                                        return "contentinfo";

                                    case "aside":
                                        return "complementary";

                                    default:
                                        return null;
                                }
                            }


                            function buildDomPath(
                                element
                            ) {

                                const path = [];

                                let current = element;

                                while (
                                    current &&
                                    current.nodeType === 1 &&
                                    path.length < 8
                                ) {

                                    const tag =
                                        current.tagName
                                            .toLowerCase();

                                    if (current.id) {

                                        path.push(
                                            `${tag}#${current.id}`
                                        );

                                        break;
                                    }

                                    const parent =
                                        current.parentElement;

                                    if (!parent) {

                                        path.push(tag);

                                        break;
                                    }

                                    const siblings =
                                        Array.from(
                                            parent.children
                                        ).filter(
                                            child =>
                                                child.tagName ===
                                                current.tagName
                                        );

                                    if (
                                        siblings.length > 1
                                    ) {

                                        const position =
                                            siblings.indexOf(
                                                current
                                            ) + 1;

                                        path.push(
                                            `${tag}:nth-of-type(${position})`
                                        );

                                    } else {

                                        path.push(tag);
                                    }

                                    current = parent;
                                }

                                return path
                                    .reverse()
                                    .join(" > ");
                            }


                            const tag =
                                element.tagName
                                    .toLowerCase();


                            const text =
                                (
                                    element.textContent ||
                                    ""
                                )
                                .trim();


                            let innerText = text;

                            try {

                                innerText =
                                    (
                                        element.innerText ||
                                        ""
                                    )
                                    .trim();

                            } catch (e) {

                                innerText = text;
                            }


                            const accessibleName =
                                getNativeAccessibleName(
                                    element
                                );


                            let value = null;

                            if (
                                tag === "input" ||
                                tag === "textarea" ||
                                tag === "select" ||
                                tag === "option"
                            ) {

                                value = element.value;
                            }


                            const attributes = {};

                            for (
                                const attribute
                                of element.attributes
                            ) {

                                attributes[
                                    attribute.name
                                ] = attribute.value;
                            }


                            return {

                                tag: tag,

                                id:
                                    element.getAttribute(
                                        "id"
                                    ),

                                class_name:
                                    element.getAttribute(
                                        "class"
                                    ),

                                name:
                                    element.getAttribute(
                                        "name"
                                    ),

                                /*
                                 * Use semantic role instead of
                                 * only reading explicit ARIA role.
                                 */
                                role:
                                    getSemanticRole(element),

                                aria_label:
                                    element.getAttribute(
                                        "aria-label"
                                    ),

                                aria_labelledby:
                                    element.getAttribute(
                                        "aria-labelledby"
                                    ),

                                aria_describedby:
                                    element.getAttribute(
                                        "aria-describedby"
                                    ),

                                accessible_name:
                                    accessibleName ||
                                    null,

                                accessible_description:
                                    getDescribedByText(
                                        element
                                    ) || null,
                                label_text:
                                    getAssociatedLabelText(
                                        element
                                    ) || null,
                                placeholder:
                                    element.getAttribute(
                                        "placeholder"
                                    ),

                                title:
                                    element.getAttribute(
                                        "title"
                                    ),

                                text:
                                    text.substring(
                                        0,
                                        1000
                                    ),

                                inner_text:
                                    innerText.substring(
                                        0,
                                        1000
                                    ),

                                value: value,

                                href:
                                    element.getAttribute(
                                        "href"
                                    ),

                                type:
                                    element.getAttribute(
                                        "type"
                                    ),

                                alt:
                                    element.getAttribute(
                                        "alt"
                                    ),

                                data_testid:
                                    element.getAttribute(
                                        "data-testid"
                                    ),

                                data_test:
                                    element.getAttribute(
                                        "data-test"
                                    ),

                                data_cy:
                                    element.getAttribute(
                                        "data-cy"
                                    ),

                                parent_tag:
                                    element.parentElement
                                        ? element
                                            .parentElement
                                            .tagName
                                            .toLowerCase()
                                        : null,

                                parent_text:
                                    element.parentElement
                                        ? (
                                            element
                                                .parentElement
                                                .innerText ||
                                            ""
                                        )
                                            .trim()
                                            .substring(
                                                0,
                                                500
                                            )
                                        : null,

                                nearby_text:
                                    element.parentElement
                                        ? (
                                            element
                                                .parentElement
                                                .innerText ||
                                            ""
                                        )
                                            .trim()
                                            .substring(
                                                0,
                                                500
                                            )
                                        : null,

                                dom_path:
                                    buildDomPath(
                                        element
                                    ),

                                attributes:
                                    attributes
                            };
                        }
                        """)

                if not data:
                    continue

                data["accessible_name"] = data.get("accessible_name") or ""
                data["accessible_description"] = (
                    data.get("accessible_description") or ""
                )
                data["label_text"] = data.get("label_text") or ""

                data["element_id"] = f"candidate_{index + 1}"

                data["visible"] = await element.is_visible()

                data["enabled"] = await element.is_enabled()

                bounding_box = await element.bounding_box()

                if bounding_box:

                    data["bounding_box"] = BoundingBox(
                        x=bounding_box["x"],
                        y=bounding_box["y"],
                        width=bounding_box["width"],
                        height=bounding_box["height"],
                    )

                else:

                    data["bounding_box"] = None

                elements.append(ElementInfo(**data))

            except Exception as error:

                print(f"Could not extract " f"candidate_{index + 1}: " f"{error}")

        print(f"Successfully extracted elements: " f"{len(elements)}")

        return elements
