from app.recovery.failure_analyzer import FailureAnalyzer


def test_locator_failure_is_classified():

    analyzer = FailureAnalyzer()

    result = analyzer.analyze(
        error_message="Locator resolved to no matching elements",
        action="click",
        target="Product",
    )

    assert result.failure_type == "LOCATOR_FAILURE"
    assert result.action == "click"
    assert result.target == "Product"


def test_strict_mode_failure_is_classified():

    analyzer = FailureAnalyzer()

    result = analyzer.analyze(
        error_message="strict mode violation: locator resolved to 3 elements",
        action="click",
        target="Product",
    )

    assert result.failure_type == "LOCATOR_FAILURE"


def test_navigation_failure_is_classified():

    analyzer = FailureAnalyzer()

    result = analyzer.analyze(
        error_message="page.goto: net::ERR_NETWORK_CHANGED",
        action="navigate",
        target="https://www.ikea.com/in/en/",
    )

    assert result.failure_type == "NAVIGATION_FAILURE"


def test_assertion_failure_is_classified():

    analyzer = FailureAnalyzer()

    result = analyzer.analyze(
        error_message="Assertion failed: expected heading to be visible",
        action="assert",
        target="Search Results",
    )

    assert result.failure_type == "ASSERTION_FAILURE"


def test_timeout_failure_is_classified():

    analyzer = FailureAnalyzer()

    result = analyzer.analyze(
        error_message="Timeout 15000ms exceeded",
        action="click",
        target="Product",
    )

    assert result.failure_type == "TIMEOUT_FAILURE"


def test_unknown_failure_is_classified():

    analyzer = FailureAnalyzer()

    result = analyzer.analyze(
        error_message="Unexpected browser failure",
        action="click",
        target="Product",
    )

    assert result.failure_type == "UNKNOWN_FAILURE"
