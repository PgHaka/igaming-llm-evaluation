"""Offline pre-request budget gate. Prices must be explicitly verified.

Synthetic prices in tests are not provider pricing.
"""

from decimal import Decimal, InvalidOperation

from evaluation.batch_ledger_v3 import initialise


def amount(value):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("Invalid monetary value") from None
    if not result.is_finite() or result < 0:
        raise ValueError("Monetary value must be finite and nonnegative")
    return result


def check_budget(
    *,
    model,
    pricing,
    pricing_verified,
    estimated_input_tokens,
    max_output_tokens,
    max_calls,
    max_estimated_usd,
    ledger=None,
):
    if not pricing_verified:
        raise PermissionError("Provider pricing has not been verified.")

    if model not in pricing:
        raise ValueError("Missing verified model pricing.")

    if not isinstance(max_calls, int) or not 1 <= max_calls <= 90:
        raise ValueError("Invalid batch call limit.")

    if not isinstance(estimated_input_tokens, int) or estimated_input_tokens < 1:
        raise ValueError("Invalid input-token estimate.")

    if not isinstance(max_output_tokens, int) or not 1 <= max_output_tokens <= 250:
        raise ValueError("Invalid output-token cap.")

    budget = amount(max_estimated_usd)
    if budget <= 0:
        raise ValueError("Budget must be positive.")

    ledger = initialise() if ledger is None else ledger
    entries = ledger["entries"]

    if len(entries) >= max_calls:
        raise PermissionError("Reserved-call limit reached.")

    rates = pricing[model]
    input_rate = amount(rates["input_per_million_usd"])
    output_rate = amount(rates["output_per_million_usd"])

    # Unknown outcomes consume their full reserved estimate.
    # Completed calls use the larger of recorded usage and reservation estimate.
    previous_estimate = sum(
        (amount(entry["reserved_estimated_usd"]) for entry in entries),
        Decimal("0"),
    )

    next_estimate = (
        Decimal(estimated_input_tokens) * input_rate
        + Decimal(max_output_tokens) * output_rate
    ) / Decimal(1_000_000)

    if previous_estimate + next_estimate > budget:
        raise PermissionError("Estimated spending limit would be exceeded.")

    return {
        "reserved_calls_after_next": len(entries) + 1,
        "next_estimated_usd": str(next_estimate),
        "cumulative_estimated_usd": str(previous_estimate + next_estimate),
        "configured_estimated_limit_usd": str(budget),
        "billing_guarantee": False,
    }


if __name__ == "__main__":
    # Deliberately synthetic test rates, NOT OpenAI prices.
    fake_prices = {
        "test-model": {
            "input_per_million_usd": "1",
            "output_per_million_usd": "2",
        }
    }
    empty = {"entries": []}

    try:
        check_budget(
            model="test-model", pricing=fake_prices,
            pricing_verified=False, estimated_input_tokens=1000,
            max_output_tokens=250, max_calls=3,
            max_estimated_usd="0.01", ledger=empty,
        )
    except PermissionError:
        print("UNVERIFIED PRICING BLOCKED: PASS")
    else:
        raise AssertionError("Unverified pricing accepted")

    result = check_budget(
        model="test-model", pricing=fake_prices,
        pricing_verified=True, estimated_input_tokens=1000,
        max_output_tokens=250, max_calls=3,
        max_estimated_usd="0.01", ledger=empty,
    )
    assert result["next_estimated_usd"] == "0.0015"
    print("SYNTHETIC COST CALCULATION: PASS")

    try:
        check_budget(
            model="test-model", pricing=fake_prices,
            pricing_verified=True, estimated_input_tokens=1000,
            max_output_tokens=250, max_calls=3,
            max_estimated_usd="0.001", ledger=empty,
        )
    except PermissionError:
        print("ESTIMATED BUDGET EXCESS BLOCKED: PASS")
    else:
        raise AssertionError("Budget excess accepted")

    try:
        check_budget(
            model="test-model", pricing=fake_prices,
            pricing_verified=True, estimated_input_tokens=1000,
            max_output_tokens=250, max_calls=1,
            max_estimated_usd="1",
            ledger={"entries": [{"reserved_estimated_usd": "0.0015"}]},
        )
    except PermissionError:
        print("CALL LIMIT BLOCKED: PASS")
    else:
        raise AssertionError("Call limit bypassed")

    assert initialise()["entries"] == []
    print("REAL V3 LEDGER: EMPTY")
    print("API REQUESTS EXECUTED: 0")
