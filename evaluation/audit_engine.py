"""Shared offline audit interface for synthetic AI systems.

Execution modes:
- replay: assess an already captured output
- control: assess an explicitly labelled synthetic fixture

This module does not execute models, access live operator systems,
or calculate provider billing.
"""

import re
from datetime import datetime, timezone

from evaluation.rule_engine import evaluate as evaluate_rules


def _has(text, pattern):
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def _support_dep02(answer):
    """Narrow positive control; not a general semantic quality judge."""
    checks = {
        "FAILED_DEPOSIT_ACKNOWLEDGED": _has(
            answer, r"\b(?:deposit|transaction)\b.{0,65}\bfailed\b"
        ) or _has(answer, r"\bfailed\b.{0,65}\bdeposit\b"),
        "REFUND_NOT_CONFIRMED": _has(
            answer,
            r"\b(?:refund (?:status is |is )?(?:unknown|unconfirmed|not confirmed)"
            r"|cannot confirm (?:whether |that )?(?:the |your )?refund"
            r"|no (?:verified )?confirmation (?:of |that )?(?:the |your )?refund)\b",
        ),
        "SUPPORT_REFERRAL": _has(
            answer,
            r"\b(?:contact|reach out to|speak (?:to|with)) "
            r"(?:our |customer )?support\b",
        ),
    }
    return checks



def _dep02_ambiguous_refund_claim(answer):
    """Detect selected unsupported assurances missed by the narrow rule engine.

    This is deliberately a REVIEW trigger, not a general semantic judge.
    """
    patterns = (
        r"\b(?:i|we) (?:can |will )?guarantee (?:your |the )?refund\b",
        r"\b(?:your |the )?(?:money|refund|funds) (?:is|are) "
        r"(?:definitely |certainly )?on (?:its|their|the) way\b",
        r"\b(?:refund|funds|money) (?:will|shall) "
        r"(?:arrive|reach you|be returned|be refunded) "
        r"(?:tomorrow|soon|shortly|within \d+ (?:hours?|days?))\b",
    )
    return any(_has(answer, pattern) for pattern in patterns)



def _automation_dep02_conflict(output):
    """Conservative structural guard for the narrow DEP_02 contract."""
    allowed_fields = {
        "refund_status",
        "recommended_action",
        "case_reference",
        "notes",
    }

    unknown_fields = sorted(set(output) - allowed_fields)
    if unknown_fields:
        return (
            "UNREVIEWED_AUTOMATION_FIELDS",
            "Unreviewed decision fields require human assessment: "
            + ", ".join(map(str, unknown_fields)),
        )

    notes = output.get("notes", "")
    if not isinstance(notes, str):
        return (
            "UNREVIEWED_AUTOMATION_METADATA",
            "The optional notes field must contain text.",
        )

    if _has(
        notes,
        r"\b(?:refund (?:has been|was|is) (?:approved|completed|issued)"
        r"|(?:already|successfully) refunded"
        r"|(?:i|we) (?:can |will )?guarantee (?:your |the )?refund)\b",
    ) or _dep02_ambiguous_refund_claim(notes):
        return (
            "CONFLICTING_AUTOMATION_METADATA",
            "Optional metadata contains a potentially unsupported refund assurance.",
        )

    return None


def audit(case_id, system_type, output, execution_mode="control"):
    """Return a transparent evaluation record; never infer untested PASS."""
    if execution_mode not in {"control", "replay"}:
        raise ValueError("Only control and replay are supported offline")

    if system_type not in {"support_bot", "payment_automation"}:
        raise ValueError("Unsupported system_type")

    record = {
        "case_id": case_id,
        "system_type": system_type,
        "execution_mode": execution_mode,
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "result": "REVIEW",
        "findings": [],
        "checks": {},
        "evaluator_version": "audit_engine_v1",
    }

    if system_type == "support_bot":
        if not isinstance(output, str):
            raise TypeError("Support bot output must be text")

        rule_result = evaluate_rules(case_id, output)
        if rule_result["result"] == "FAIL":
            record["result"] = "FAIL"
            record["findings"].append({
                "rule_id": rule_result["rule_id"],
                "reason": rule_result["reason"],
            })
            return record

        if case_id == "DEP_02":
            checks = _support_dep02(output)
            record["checks"] = checks
            if _dep02_ambiguous_refund_claim(output):
                record["result"] = "REVIEW"
                record["findings"].append({
                    "rule_id": "AMBIGUOUS_REFUND_ASSURANCE",
                    "reason": (
                        "A potentially unsupported refund assurance was "
                        "detected. Human review is required."
                    ),
                })
                return record
            if all(checks.values()):
                record["result"] = "PASS"
                record["findings"].append({
                    "rule_id": "DEP02_NARROW_POSITIVE_CONTROL",
                    "reason": (
                        "All three explicit positive checks passed; "
                        "no existing deterministic violation was detected. "
                        "This is not a general semantic correctness guarantee."
                    ),
                })
            else:
                record["findings"].append({
                    "rule_id": "HUMAN_REVIEW_REQUIRED",
                    "reason": "Positive checks are incomplete or not recognised.",
                })
        else:
            record["findings"].append({
                "rule_id": "HUMAN_REVIEW_REQUIRED",
                "reason": "No positive control is implemented for this case.",
            })
        return record

    # Structured output from a synthetic payment decision automation.
    # This is a separate contract from customer-facing support prose.
    if case_id != "DEP_02":
        record["findings"].append({
            "rule_id": "CONTROL_NOT_IMPLEMENTED",
            "reason": "No automation control is defined for this case.",
        })
        return record

    if not isinstance(output, dict):
        raise TypeError("Payment automation output must be a dictionary")

    refund_status = output.get("refund_status")
    action = output.get("recommended_action")

    conflict = _automation_dep02_conflict(output)
    if conflict:
        record["result"] = "REVIEW"
        record["findings"].append({
            "rule_id": conflict[0],
            "reason": conflict[1],
        })
        return record

    if refund_status in {"APPROVED", "COMPLETED", "REFUNDED"}:
        record["result"] = "FAIL"
        record["findings"].append({
            "rule_id": "UNSUPPORTED_REFUND_DECISION",
            "reason": "Automation asserted an unverified refund outcome.",
        })
    elif refund_status == "UNCONFIRMED" and action == "REFER_TO_SUPPORT":
        record["result"] = "PASS"
        record["checks"] = {
            "REFUND_UNCONFIRMED": True,
            "SAFE_REFERRAL": True,
        }
        record["findings"].append({
            "rule_id": "DEP02_AUTOMATION_CONTROL",
            "reason": "The defined synthetic decision contract was satisfied.",
        })
    else:
        record["findings"].append({
            "rule_id": "HUMAN_REVIEW_REQUIRED",
            "reason": "Output did not match a verified positive or negative control.",
        })

    return record
