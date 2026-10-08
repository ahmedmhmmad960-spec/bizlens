from core.diagnoses.margin_decline import detect_margin_decline


def test_margin_decline_returns_evidence_backed_diagnosis() -> None:
    result = detect_margin_decline(
        {
            "previous": {"gross_margin": 31.4},
            "current": {"gross_margin": 20.1},
        }
    )

    assert result is not None
    assert result["diagnosis"] == "Margin Decline"
    assert result["change_points"] == -11.3
    assert result["severity"] == "high"
    assert result["evidence"]["margin_change_points"] == -11.3


def test_small_margin_change_is_not_a_diagnosis() -> None:
    result = detect_margin_decline(
        {
            "previous": {"gross_margin": 31.4},
            "current": {"gross_margin": 29.0},
        }
    )

    assert result is None


def test_missing_margin_does_not_create_a_diagnosis() -> None:
    result = detect_margin_decline(
        {
            "previous": {"gross_margin": None},
            "current": {"gross_margin": 20.0},
        }
    )

    assert result is None
