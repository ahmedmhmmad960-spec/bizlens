def calculate_change(previous, current):
    if previous is None or current is None:
        return None

    change = current - previous

    if previous != 0:
        change_percent = (change / abs(previous)) * 100
    else:
        change_percent = None

    return {
        "previous": round(previous, 2),
        "current": round(current, 2),
        "change": round(change, 2),
        "change_percent": (
            round(change_percent, 2)
            if change_percent is not None
            else None
        ),
    }


def build_what_changed(period_comparison: dict) -> list[dict]:
    previous = period_comparison.get("previous", {})
    current = period_comparison.get("current", {})

    metrics = [
        ("Revenue", "revenue"),
        ("Orders", "orders"),
        ("Cost", "cost"),
        ("Discount", "discount"),
        ("Gross Profit", "gross_profit"),
        ("Gross Margin", "gross_margin"),
    ]

    changes = []

    for label, key in metrics:
        result = calculate_change(
            previous.get(key),
            current.get(key),
        )

        if result is None:
            continue

        if result["change"] > 0:
            direction = "up"
        elif result["change"] < 0:
            direction = "down"
        else:
            direction = "unchanged"

        changes.append({
            "metric": label,
            "key": key,
            **result,
            "direction": direction,
        })

    return changes
