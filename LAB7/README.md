# L6_L7_01 — Water Utility Billing

## Lab 7: Fuzz Testing for Input Validation Bugs

This lab continues the input-processing application from the water utility billing problem. Hypothesis generates arbitrary strings and `None` values to exercise all three routines.

## Files

| File | Description |
|---|---|
| `processor.py` | Corrected application with validation for all three functions. |
| `test_processor.py` | Completed Hypothesis property-based fuzz tests. |
| `requirements.txt` | Test dependencies. |
| `validate_without_hypothesis.py` | Optional offline smoke checks; not a replacement for Hypothesis tests. |

## Functions tested

1. `sanitize_meter_id(meter_id)` — trims whitespace, removes `!`, `@`, `#`, `$`, `%`, converts the ID to uppercase, and rejects IDs that become empty.
2. `parse_consumption_readings(readings_csv)` — parses comma-separated integer readings and rejects empty or non-integer tokens.
3. `format_billing_summary(account_record)` — validates the exact `Name:Usage:Zone` format and calculates the displayed bill at 2 USD per unit.

## Install and run

```bash
python -m pip install -r requirements.txt
python -m pytest -v
```

The fuzz tests use `TypeError` and `ValueError` as the expected validation outcomes for unsuitable inputs. Any other exception fails the test.
