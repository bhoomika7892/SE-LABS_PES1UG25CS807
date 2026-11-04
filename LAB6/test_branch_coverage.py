import pytest

from water_utility_billing import calculate_water_bill, check_meter_tampering


def test_validation_branches_for_accounts_and_base_fee():
    with pytest.raises(ValueError):
        calculate_water_bill(None, 10.0)
    with pytest.raises(ValueError):
        calculate_water_bill([], -1.0)
    assert calculate_water_bill([], 0.0)["status"] == "NO_ACTIVITY"


def test_account_iteration_active_and_inactive_paths():
    accounts = [
        {"is_active": False, "usage_blocks": [100]},
        {"is_active": True, "usage_blocks": []},
    ]
    assert calculate_water_bill(accounts, 5.0) == {
        "total_billed": 5.0, "status": "NORMAL"
    }


def test_usage_loop_empty_and_nonempty_paths():
    assert calculate_water_bill(
        [{"is_active": True, "usage_blocks": []}], 5.0
    )["total_billed"] == 5.0
    assert calculate_water_bill(
        [{"is_active": True, "usage_blocks": [10]}], 5.0
    )["total_billed"] == 20.0


def test_nonpositive_and_positive_usage_paths():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [0, -1, 20]}], 5.0
    )
    assert result == {"total_billed": 35.0, "status": "NORMAL"}


def test_over_100_commercial_and_residential_paths():
    commercial = calculate_water_bill(
        [{"is_active": True, "is_commercial": True, "usage_blocks": [110, 10]}],
        0.0,
    )
    residential = calculate_water_bill(
        [{"is_active": True, "is_commercial": False, "usage_blocks": [110, 10]}],
        0.0,
    )
    # Commercial continues to the next block; residential breaks after the first.
    assert commercial["total_billed"] == 400.0
    assert residential["total_billed"] == 495.0


def test_middle_and_low_usage_tier_paths():
    result = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [51, 50]}], 0.0
    )
    assert result["total_billed"] == 202.5


def test_leak_waiver_present_absent_and_threshold_paths():
    with_waiver_over = calculate_water_bill(
        [{"is_active": True, "has_leak_waiver": True, "usage_blocks": [150]}],
        0.0,
    )
    with_waiver_under = calculate_water_bill(
        [{"is_active": True, "has_leak_waiver": True, "usage_blocks": [50]}],
        0.0,
    )
    without_waiver = calculate_water_bill(
        [{"is_active": True, "has_leak_waiver": False, "usage_blocks": [150]}],
        0.0,
    )
    assert with_waiver_over["total_billed"] == 625.0
    assert with_waiver_under["total_billed"] == 75.0
    assert without_waiver["total_billed"] == 675.0


def test_status_excessive_flags_and_no_activity_and_normal_paths():
    excessive = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [0, 0, 0, 0, 0, 0]}], 1.0
    )
    no_activity = calculate_water_bill([], 1.0)
    normal = calculate_water_bill(
        [{"is_active": True, "usage_blocks": [1]}], 1.0
    )
    assert excessive["status"] == "EXCESSIVE_FLAGS"
    assert no_activity["status"] == "NO_ACTIVITY"
    assert normal["status"] == "NORMAL"


def test_meter_no_data_and_empty_meter_paths():
    assert check_meter_tampering([]) == "NO_DATA"
    assert check_meter_tampering([[]]) == "CLEAR"


def test_meter_negative_nonnegative_reset_and_consecutive_negative_paths():
    assert check_meter_tampering([[ -1, 0, -1, 1]]) == "CLEAR"
    assert check_meter_tampering([[-1, -1]]) == "TAMPER_SUSPECTED"


def test_meter_outer_loop_continues_to_next_meter():
    assert check_meter_tampering([[-1], [1, -1]]) == "CLEAR"
