import pytest

from water_utility_billing import calculate_water_bill, check_meter_tampering


def test_single_active_residential():
    accounts = [{
        "is_active": True,
        "is_commercial": False,
        "has_leak_waiver": False,
        "usage_blocks": [30],
    }]
    result = calculate_water_bill(accounts, 10.0)
    assert result == {"total_billed": 55.0, "status": "NORMAL"}


def test_empty_accounts_returns_no_activity():
    assert calculate_water_bill([], 10.0) == {
        "total_billed": 0.0, "status": "NO_ACTIVITY"
    }


def test_inactive_account_is_skipped():
    accounts = [{"is_active": False, "usage_blocks": [30]}]
    assert calculate_water_bill(accounts, 10.0) == {
        "total_billed": 0.0, "status": "NO_ACTIVITY"
    }


def test_commercial_usage_over_100_uses_commercial_rate():
    accounts = [{
        "is_active": True,
        "is_commercial": True,
        "usage_blocks": [120],
    }]
    # 10 base fee + (120 * 3.5)
    assert calculate_water_bill(accounts, 10.0)["total_billed"] == 430.0


def test_residential_usage_over_100_uses_residential_rate():
    accounts = [{
        "is_active": True,
        "is_commercial": False,
        "usage_blocks": [120],
    }]
    # 10 base fee + (120 * 4.5)
    assert calculate_water_bill(accounts, 10.0)["total_billed"] == 550.0


def test_usage_between_51_and_100_uses_middle_rate():
    accounts = [{"is_active": True, "usage_blocks": [60]}]
    assert calculate_water_bill(accounts, 10.0)["total_billed"] == 160.0


def test_usage_up_to_50_uses_low_rate():
    accounts = [{"is_active": True, "usage_blocks": [50]}]
    assert calculate_water_bill(accounts, 10.0)["total_billed"] == 85.0


def test_non_positive_usage_is_flagged_and_skipped():
    accounts = [{"is_active": True, "usage_blocks": [0, -5, 10]}]
    result = calculate_water_bill(accounts, 10.0)
    assert result == {"total_billed": 25.0, "status": "NORMAL"}


def test_leak_waiver_deducts_50_when_bill_exceeds_200():
    accounts = [{
        "is_active": True,
        "has_leak_waiver": True,
        "usage_blocks": [100],
    }]
    # Residential usage above 100 is charged at 4.5 per unit; waiver deducts 50.
    accounts[0]["usage_blocks"] = [150]
    assert calculate_water_bill(accounts, 10.0)["total_billed"] == 635.0


def test_leak_waiver_does_not_deduct_when_bill_is_200_or_less():
    accounts = [{
        "is_active": True,
        "has_leak_waiver": True,
        "usage_blocks": [50],
    }]
    assert calculate_water_bill(accounts, 10.0)["total_billed"] == 85.0


def test_more_than_five_flags_sets_excessive_flags():
    accounts = [{
        "is_active": True,
        "usage_blocks": [0, 0, 0, 0, 0, 0],
    }]
    assert calculate_water_bill(accounts, 10.0)["status"] == "EXCESSIVE_FLAGS"


def test_invalid_accounts_argument_raises_value_error():
    with pytest.raises(ValueError):
        calculate_water_bill("not a list", 10.0)


def test_negative_base_fee_raises_value_error():
    with pytest.raises(ValueError):
        calculate_water_bill([], -1.0)


def test_empty_meter_readings_return_no_data():
    assert check_meter_tampering([]) == "NO_DATA"


def test_meter_readings_without_two_consecutive_negative_deltas_are_clear():
    assert check_meter_tampering([[1, -1, 2, -1], [0, 3]]) == "CLEAR"


def test_two_consecutive_negative_deltas_detect_tampering():
    assert check_meter_tampering([[1, -1, -2, 3]]) == "TAMPER_SUSPECTED"
