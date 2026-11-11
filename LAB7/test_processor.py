"""Hypothesis fuzz tests for the Lab 7 input-validation functions."""

from hypothesis import given, settings, strategies as st
import pytest

from processor import (
    sanitize_meter_id,
    parse_consumption_readings,
    format_billing_summary,
)

# The lab starter explicitly asks for text values and null inputs.
FUZZ_INPUTS = st.one_of(st.text(), st.none())


@settings(max_examples=250, deadline=None)
@given(FUZZ_INPUTS)
def test_sanitize_meter_id_no_crash(s):
    cleaned = s.strip() if isinstance(s, str) else None
    if cleaned is not None:
        for ch in ('!', '@', '#', '$', '%'):
            cleaned = cleaned.replace(ch, '')

    try:
        result = sanitize_meter_id(s)
    except (TypeError, ValueError):
        # None and IDs that become empty after sanitization must be rejected.
        assert s is None or cleaned == ""
    else:
        assert isinstance(result, str)
        assert cleaned
        assert result == cleaned.upper()
        assert result == result.upper()
        assert not any(ch in result for ch in '!@#$%')


@settings(max_examples=250, deadline=None)
@given(FUZZ_INPUTS)
def test_parse_consumption_readings_safe(s):
    try:
        result = parse_consumption_readings(s)
    except (TypeError, ValueError):
        # A malformed value is a validation failure, not an unexpected crash.
        assert s is None or isinstance(s, str)
    else:
        assert isinstance(result, list)
        assert all(type(value) is int for value in result)
        assert isinstance(s, str)
        assert len(result) == len(s.split(','))


@settings(max_examples=250, deadline=None)
@given(FUZZ_INPUTS)
def test_format_billing_summary_safe(s):
    try:
        result = format_billing_summary(s)
    except (TypeError, ValueError):
        # Invalid structure/content should be rejected by validation.
        assert s is None or isinstance(s, str)
    else:
        assert isinstance(result, str)
        assert result.startswith("Customer ")
        assert " billed " in result
        assert " USD in " in result
        assert isinstance(s, str)
        fields = s.split(":")
        assert len(fields) == 3
        customer_name, usage_text, zone = (field.strip() for field in fields)
        assert customer_name and usage_text and zone
        int(usage_text)  # accepted records must contain an integer usage value


def test_valid_inputs_keep_expected_behavior():
    assert sanitize_meter_id("  !ab@12#  ") == "AB12"
    assert parse_consumption_readings("10, 25,30") == [10, 25, 30]
    assert format_billing_summary("Asha:25:North") == (
        "Customer Asha billed 50 USD in North"
    )


def test_malformed_delimiters_and_nulls_are_rejected():
    for value in (None, "", "   "):
        with pytest.raises((TypeError, ValueError)):
            parse_consumption_readings(value)

    for value in ("1,,2", ",1", "1,", "1,two,3"):
        with pytest.raises(ValueError):
            parse_consumption_readings(value)

    bad_records = (
        None, "", "Asha:10", "Asha:10:North:Extra", ":10:North",
        "Asha::North", "Asha:abc:North", "Asha:10:",
    )
    for value in bad_records:
        with pytest.raises((TypeError, ValueError)):
            format_billing_summary(value)

    for value in (None, "", "   ", "!@#$%"):
        with pytest.raises((TypeError, ValueError)):
            sanitize_meter_id(value)
