"""Offline smoke checks; not a replacement for the Hypothesis suite."""
from processor import (
    sanitize_meter_id,
    parse_consumption_readings,
    format_billing_summary,
)


def must_raise(expected, function, value):
    try:
        function(value)
    except expected:
        return
    raise AssertionError(f"Expected {expected} for input {value!r}")


assert sanitize_meter_id(" !ab@12# ") == "AB12"
assert parse_consumption_readings("10, 25,30") == [10, 25, 30]
assert format_billing_summary("Asha:25:North") == (
    "Customer Asha billed 50 USD in North"
)

must_raise(TypeError, sanitize_meter_id, None)
must_raise(TypeError, parse_consumption_readings, None)
must_raise(ValueError, parse_consumption_readings, "1,,2")
must_raise(ValueError, parse_consumption_readings, "one,2")
must_raise(TypeError, format_billing_summary, None)
must_raise(ValueError, format_billing_summary, "Asha:10")
must_raise(ValueError, format_billing_summary, "Asha:x:North")

print("Offline smoke checks passed: 10 checks")
