from app.models.failure import FailureEvidence


class FailureAnalyzer:

    def analyze(
        self,
        error_message: str,
        action: str,
        target: str | None = None,
    ) -> FailureEvidence:

        message = error_message.lower()

        failure_type = self._classify(message)

        return FailureEvidence(
            error_message=error_message,
            failure_type=failure_type,
            action=action,
            target=target,
        )

    def _classify(self, message: str) -> str:

        # Explicit timeout errors should be classified first.
        if "timeout" in message:
            return "TIMEOUT_FAILURE"

        # Navigation/network failures.
        if "net::" in message:
            return "NAVIGATION_FAILURE"

        if "navigation" in message:
            return "NAVIGATION_FAILURE"

        # Explicit locator failures.
        if "strict mode violation" in message:
            return "LOCATOR_FAILURE"

        if "no matching" in message:
            return "LOCATOR_FAILURE"

        if "locator" in message:
            return "LOCATOR_FAILURE"

        if "element not found" in message:
            return "LOCATOR_FAILURE"

        # Assertion failures.
        if "assertion" in message:
            return "ASSERTION_FAILURE"

        if "assert failed" in message:
            return "ASSERTION_FAILURE"

        # Do NOT use:
        #     "expected" in message
        #
        # because words such as "unexpected" also contain "expected".

        return "UNKNOWN_FAILURE"
