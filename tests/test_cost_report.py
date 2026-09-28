from decimal import Decimal

from platform_guard.cost_report import summarize_costs


def test_cost_report_groups_services_and_flags_budget(tmp_path):
    usage_file = tmp_path / "usage.csv"
    usage_file.write_text(
        "date,service,cost_usd\n2026-09-01,inference,10.25\n2026-09-02,inference,4.75\n2026-09-02,storage,2.00\n",
        encoding="utf-8",
    )

    report = summarize_costs(usage_file, Decimal("16.00"))

    assert report["row_count"] == 3
    assert report["total_usd"] == "17.00"
    assert report["by_service_usd"] == {"inference": "15.00", "storage": "2.00"}
    assert report["over_budget"] is True


def test_cost_report_requires_expected_columns(tmp_path):
    usage_file = tmp_path / "bad.csv"
    usage_file.write_text("service,total\napi,12\n", encoding="utf-8")

    try:
        summarize_costs(usage_file)
    except ValueError as error:
        assert "date, service, and cost_usd" in str(error)
    else:
        raise AssertionError("invalid CSV columns should be rejected")