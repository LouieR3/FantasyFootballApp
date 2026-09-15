"""Utility to format win-loss-tie records cleanly.

Converts "W-L-T" records so ties only show if T > 0:
- "7-3-0" → "7-3"
- "7-3-1" → "7-3-1"
"""

def format_record(record):
    """
    Format a record string, omitting the tie count if it's 0.

    Args:
        record: Record as string "W-L" or "W-L-T", or int/float

    Returns:
        Formatted record string (e.g., "7-3" or "7-3-1")
    """
    if record is None or (isinstance(record, float) and record != record):  # NaN check
        return "–"

    record_str = str(record).strip()
    if not record_str:
        return "–"

    parts = record_str.split('-')

    if len(parts) < 2:
        return record_str

    wins = parts[0]
    losses = parts[1]
    ties = parts[2] if len(parts) > 2 else "0"

    # Convert to int to check if tie is 0
    try:
        ties_int = int(float(ties))
    except (ValueError, TypeError):
        # If we can't parse ties, return original
        return record_str

    if ties_int == 0:
        return f"{wins}-{losses}"
    else:
        return f"{wins}-{losses}-{ties}"


if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("7-3-0", "7-3"),
        ("7-3-1", "7-3-1"),
        ("1-0-0", "1-0"),
        ("1-0-1", "1-0-1"),
        ("0-0-0", "0-0"),
        ("10-4-0", "10-4"),
        (None, "–"),
        ("", "–"),
    ]

    for input_val, expected in test_cases:
        result = format_record(input_val)
        status = "✓" if result == expected else "✗"
        print(f"{status} format_record({input_val!r}) = {result!r} (expected {expected!r})")
