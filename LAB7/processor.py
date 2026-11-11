"""Input-processing routines for the water utility billing application.

This is the Lab 7 corrected version of the supplied starter processor.py.
"""


def sanitize_meter_id(meter_id):
    """Remove supported prefix characters and return an uppercase meter ID."""
    if not isinstance(meter_id, str):
        raise TypeError("meter_id must be a string")

    meter_id = meter_id.strip()
    for ch in ('!', '@', '#', '$', '%'):
        meter_id = meter_id.replace(ch, '')
    return meter_id.upper()


def parse_consumption_readings(readings_csv):
    """Parse a comma-separated string of integer consumption readings."""
    if not isinstance(readings_csv, str):
        raise TypeError("readings_csv must be a string")
    if not readings_csv.strip():
        raise ValueError("readings_csv must contain at least one reading")

    readings = []
    for index, token in enumerate(readings_csv.split(','), start=1):
        token = token.strip()
        if not token:
            raise ValueError(f"reading {index} is empty")
        try:
            readings.append(int(token))
        except ValueError as exc:
            raise ValueError(f"reading {index} must be an integer") from exc
    return readings


def format_billing_summary(account_record):
    """Format a Name:Usage:Zone record using the original 2 USD/unit rate."""
    if not isinstance(account_record, str):
        raise TypeError("account_record must be a string")

    parts = account_record.split(':')
    if len(parts) != 3:
        raise ValueError("account_record must have exactly 3 fields: Name:Usage:Zone")

    customer_name, usage_text, zone = (part.strip() for part in parts)
    if not customer_name:
        raise ValueError("customer name must not be empty")
    if not usage_text:
        raise ValueError("usage must not be empty")
    if not zone:
        raise ValueError("zone must not be empty")

    try:
        units = int(usage_text)
    except ValueError as exc:
        raise ValueError("usage must be an integer") from exc

    return f"Customer {customer_name} billed {units * 2} USD in {zone}"


def main():
    print("==== Running sanitize_meter_id ====")
    raw_id = input("Enter a meter ID with prefixes (!,@,#,$,%): ")
    clean_id = sanitize_meter_id(raw_id)
    print("Sanitized Meter ID:", clean_id)

    print("\n==== Running parse_consumption_readings ====")
    csv_input = input("Enter consumption readings (e.g. 10,25,30): ")
    readings_list = parse_consumption_readings(csv_input)
    print("Parsed Readings:", readings_list)

    print("\n==== Running format_billing_summary ====")
    summary_input = input("Enter account record (Name:Usage:Zone): ")
    summary = format_billing_summary(summary_input)
    print("Billing Summary:", summary)


if __name__ == "__main__":
    main()
