from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


def summarize_costs(path: str | Path, budget_usd: Decimal | None = None) -> dict[str, Any]:
    """Aggregate a local CSV with date, service, and cost_usd columns."""
    service_totals: dict[str, Decimal] = {}
    row_count = 0

    with Path(path).open(newline="", encoding="utf-8") as cost_file:
        reader = csv.DictReader(cost_file)
        required = {"date", "service", "cost_usd"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("CSV must contain date, service, and cost_usd columns")

        for line_number, row in enumerate(reader, start=2):
            service = (row.get("service") or "").strip()
            if not service:
                raise ValueError(f"Row {line_number}: service is required")
            try:
                amount = Decimal((row.get("cost_usd") or "").strip())
            except InvalidOperation as error:
                raise ValueError(f"Row {line_number}: cost_usd must be numeric") from error
            if not amount.is_finite() or amount < 0:
                raise ValueError(f"Row {line_number}: cost_usd must be a finite non-negative amount")
            service_totals[service] = service_totals.get(service, Decimal(0)) + amount
            row_count += 1

    total = sum(service_totals.values(), Decimal(0))
    return {
        "row_count": row_count,
        "total_usd": str(total.quantize(Decimal("0.01"))),
        "by_service_usd": {
            service: str(amount.quantize(Decimal("0.01")))
            for service, amount in sorted(service_totals.items())
        },
        "budget_usd": str(budget_usd.quantize(Decimal("0.01"))) if budget_usd is not None else None,
        "over_budget": total > budget_usd if budget_usd is not None else None,
    }