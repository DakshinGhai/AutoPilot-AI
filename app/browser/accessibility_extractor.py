from typing import Dict

from playwright.async_api import Page


class AccessibilityExtractor:

    async def extract(
        self,
        page: Page,
    ) -> Dict:

        return await page.evaluate("""
            () => {

                function cleanText(value) {

                    if (!value) {
                        return "";
                    }

                    return value
                        .replace(/\\\\s+/g, " ")
                        .trim();
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
                        of ids.split(/\\\\s+/)
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


                function getAccessibleName(
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
                        element.tagName.toLowerCase();


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

                        return cleanText(
                            element.innerText ||
                            ""
                        );
                    }


                    if (
                        /^h[1-6]$/.test(tag)
                    ) {

                        return cleanText(
                            element.innerText ||
                            element.textContent ||
                            ""
                        );
                    }


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

                        return cleanText(
                            element.getAttribute(
                                "title"
                            )
                        );
                    }


                    return "";
                }


                const elements = [];


                const nodes =
                    document.querySelectorAll(
                        '[role], [aria-label], [aria-labelledby], [aria-describedby]'
                    );


                nodes.forEach(
                    (element, index) => {

                        elements.push({

                            index: index,

                            tag:
                                element.tagName
                                    .toLowerCase(),

                            role:
                                element.getAttribute(
                                    "role"
                                ),

                            ariaLabel:
                                element.getAttribute(
                                    "aria-label"
                                ),

                            ariaLabelledBy:
                                element.getAttribute(
                                    "aria-labelledby"
                                ),

                            ariaDescribedBy:
                                element.getAttribute(
                                    "aria-describedby"
                                ),

                            ariaExpanded:
                                element.getAttribute(
                                    "aria-expanded"
                                ),

                            ariaChecked:
                                element.getAttribute(
                                    "aria-checked"
                                ),

                            ariaSelected:
                                element.getAttribute(
                                    "aria-selected"
                                ),

                            ariaHasPopup:
                                element.getAttribute(
                                    "aria-haspopup"
                                ),

                            accessibleName:
                                getAccessibleName(
                                    element
                                ),

                            accessibleText:
                                getAccessibleName(
                                    element
                                )
                        });
                    }
                );


                return elements;
            }
            """)
