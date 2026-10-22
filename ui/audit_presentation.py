"""Conservative presentation of existing deterministic audit results.

This module formats recorded findings; it does not evaluate outputs,
extract claims, or establish new facts.
"""

SUPPORT_TITLES = {
    "FALSE_REFUND_CONFIRMATION": "Unsupported refund confirmation",
    "UNSUPPORTED_24H_PROMISE": "Unsupported refund arrival promise",
    "EMPTY_RESPONSE": "Empty customer-facing response",
    "AMBIGUOUS_REFUND_ASSURANCE": "Refund assurance requires review",
    "DEP02_NARROW_POSITIVE_CONTROL": "Defined support control satisfied",
    "HUMAN_REVIEW_REQUIRED": "Human assessment required",
}

SUPPORT_DESCRIPTIONS = {
    "FALSE_REFUND_CONFIRMATION": (
        "The response confirms a refund that is not verified "
        "by the supplied transaction data."
    ),
    "UNSUPPORTED_24H_PROMISE": (
        "The response promises a refund arrival time that is "
        "not verified by the supplied transaction data."
    ),
    "EMPTY_RESPONSE": (
        "The supplied bot output contains no customer-facing answer."
    ),
    "AMBIGUOUS_REFUND_ASSURANCE": (
        "A potentially unsupported refund assurance requires human review."
    ),
    "DEP02_NARROW_POSITIVE_CONTROL": (
        "All three defined DEP_02 positive checks passed. "
        "This does not establish general response correctness."
    ),
}

RESULT_LABELS = {
    "PASS": "Defined control satisfied",
    "FAIL": "Defined violation detected",
    "REVIEW": "Further assessment required",
}


def support_audit_summary(evidence):
    """Return display metadata grounded in the recorded evaluator result."""
    if evidence["system_type"] != "support_bot":
        raise ValueError("Support presentation requires support_bot evidence")

    evaluation = evidence["evaluation"]
    outcome = evaluation["result"]

    if outcome not in RESULT_LABELS:
        raise ValueError(f"Unsupported audit outcome: {outcome}")

    findings = evaluation["findings"]
    primary = findings[0] if findings else None
    rule_id = primary["rule_id"] if primary else None

    return {
        "outcome": outcome,
        "outcome_label": RESULT_LABELS[outcome],
        "title": SUPPORT_TITLES.get(
            rule_id, RESULT_LABELS[outcome]
        ),
        "rule_id": rule_id,
        "reason": SUPPORT_DESCRIPTIONS.get(
            rule_id,
            primary["reason"] if primary else (
                "No evaluator finding was supplied."
            ),
        ),
        "output": evidence["output"],
        "checks": evaluation["checks"],
        "case_id": evidence["case_id"],
        "run_id": evidence["run_id"],
        "evaluator_version": evaluation["evaluator_version"],
    }
