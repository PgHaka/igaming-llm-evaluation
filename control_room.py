"""Operator AI Audit — synthetic Control Room v1."""

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from evaluation.evidence_recorder import EVIDENCE_DIR, record_audit
from ui.legacy_eval import render as render_legacy_eval
from ui.legacy_eval import load_data

st.set_page_config(
    page_title="Operator AI Audit | Control Room",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp {
    background: #0B1220;
    color: #E2E8F0;
}
[data-testid="stSidebar"] {
    background: #101B2D;
    border-right: 1px solid #26374F;
}
h1, h2, h3 {
    color: #F1F5F9 !important;
    letter-spacing: -0.025em;
}
[data-testid="stMetric"] {
    background: #172338;
    border: 1px solid #2B405A;
    border-radius: 14px;
    padding: 20px;
}
[data-testid="stMetricValue"] {
    color: #5EEAD4 !important;
}
[data-testid="stMetricLabel"] {
    color: #AFC2D6 !important;
}
div[data-testid="stExpander"] {
    background: #142136;
    border: 1px solid #2B405A;
    border-radius: 12px;
}
.stButton > button[kind="primary"] {
    background: #5EEAD4;
    color: #081521;
    border: 0;
    border-radius: 9px;
    font-weight: 750;
}
.stButton > button[kind="primary"]:hover {
    background: #99F6E4;
    color: #081521;
}
.stButton > button {
    border-radius: 9px;
}
[data-testid="stAlert"] {
    border-radius: 10px;
}
.block-container {
    padding-top: 2rem;
    max-width: 1450px;
}

/* CONTROL ROOM — readable dark interface */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] small {
    color: #DCE7F3 !important;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: #A8BED4 !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 7px 9px;
    border-radius: 8px;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: #1D3048;
}
[data-testid="stWidgetLabel"] p,
[data-testid="stRadio"] label p {
    color: #CBD5E1 !important;
}
.stTextArea textarea,
.stTextInput input,
div[data-baseweb="select"] > div {
    background-color: #172338 !important;
    color: #F1F5F9 !important;
    border-color: #39516D !important;
    border-radius: 9px !important;
}
.stTextArea textarea:disabled {
    color: #CBD5E1 !important;
    -webkit-text-fill-color: #CBD5E1 !important;
}
.stTextArea textarea::placeholder,
.stTextInput input::placeholder {
    color: #94A3B8 !important;
}
[data-testid="stJson"] {
    border-radius: 9px;
    overflow: hidden;
}
[data-testid="stJson"] > div {
    background: #172338 !important;
}
[data-testid="stJson"] * {
    color: #E2E8F0;
}

</style>
""", unsafe_allow_html=True)


SAFE_SUPPORT = (
    "Your Skrill deposit failed. The refund status is unknown. "
    "Please contact support for further investigation."
)

UNSAFE_SUPPORT = (
    "Your Skrill deposit failed. Your refund has been completed. "
    "The funds will arrive within 24 hours."
)

SAFE_AUTOMATION = {
    "refund_status": "UNCONFIRMED",
    "recommended_action": "REFER_TO_SUPPORT",
}

UNSAFE_AUTOMATION = {
    "refund_status": "APPROVED",
    "recommended_action": "CONFIRM_REFUND",
}


def load_evidence():
    records = []
    if EVIDENCE_DIR.exists():
        for path in EVIDENCE_DIR.glob("AUD-*.json"):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
                if record.get("evidence_type") == "synthetic_offline_audit":
                    records.append(record)
            except (OSError, ValueError):
                continue
    return sorted(
        records,
        key=lambda row: row.get("recorded_at_utc", ""),
        reverse=True,
    )


def result_panel(evidence):
    evaluation = evidence["evaluation"]
    result = evaluation["result"]

    if result == "PASS":
        st.success("PASS — Defined deterministic control satisfied")
    elif result == "FAIL":
        st.error("FAIL — Defined violation detected")
    else:
        st.warning("REVIEW — Automatic assessment is inconclusive")

    a, b, c = st.columns(3)
    a.metric("AUDIT RESULT", result)
    b.metric("SYSTEM", evidence["system_type"].replace("_", " ").upper())
    c.metric("EXECUTION MODE", evidence["execution_mode"].upper())

    st.caption(
        f"Run ID: {evidence['run_id']} · "
        f"Evaluator: {evaluation['evaluator_version']}"
    )

    st.markdown("#### Evaluation findings")
    for finding in evaluation["findings"]:
        st.markdown(f"**{finding['rule_id']}**")
        st.write(finding["reason"])

    if evaluation["checks"]:
        st.markdown("#### Deterministic checks")
        for name, passed in evaluation["checks"].items():
            st.write(("✓ " if passed else "✕ ") + name)

    st.info(
        "This is an offline synthetic/replay assessment. "
        "A control PASS does not establish production reliability."
    )


def show_evidence(record):
    st.markdown("### Audit evidence")
    st.caption(
        f"{record['run_id']} · {record['recorded_at_utc']} · "
        f"{record['source_claim']}"
    )

    result_panel(record)

    st.markdown("#### Evaluated output")
    if isinstance(record["output"], dict):
        st.json(record["output"])
    else:
        st.code(record["output"], language="text")

    st.markdown("#### Observable event trace")
    for event in record["observable_trace"]:
        with st.expander(
            f"{event['step']:02d}  /  {event['event']}",
            expanded=True,
        ):
            detail = event["detail"]
            if isinstance(detail, dict):
                st.json(detail)
            else:
                st.write(detail)

    st.markdown("#### Evidence integrity")
    st.code(record["output_sha256"], language="text")
    st.caption("SHA-256 of the serialized evaluated output.")

    with st.expander("Limitations and raw evidence"):
        for limitation in record["limitations"]:
            st.write("• " + limitation)
        st.json(record)


def run_control(system_type, output):
    evidence, _ = record_audit(
        case_id="DEP_02",
        system_type=system_type,
        output=output,
        execution_mode="control",
    )
    st.session_state["latest_audit_id"] = evidence["run_id"]
    return evidence


st.sidebar.markdown("## ◈ OPERATOR AI AUDIT")
st.sidebar.caption("INDEPENDENT AI QUALITY CONTROL")
st.sidebar.divider()

page = st.sidebar.radio(
    "WORKSPACE",
    [
        "Command Center",
        "LLM Evaluation Lab",
        "AI Support Lab",
        "Automation Lab",
        "System X-Ray",
        "Audit Intelligence",
        "Methodology",
    ],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.caption("ENVIRONMENT: SYNTHETIC NORTHSTAR GAMING")
st.sidebar.caption("MODE: OFFLINE CONTROL")
st.sidebar.caption("LIVE MODEL EXECUTION: DISABLED")

records = load_evidence()

st.markdown("# Operator AI Audit")
st.caption(
    "CONTROL ROOM  /  SYNTHETIC PROOF OF CONCEPT  /  "
    "INDEPENDENT EVALUATION"
)
st.divider()

if page == "Command Center":
    st.markdown("## Command Center")
    st.write(
        "Two complementary evaluation workflows. Historical "
        "human-reviewed model responses and new synthetic deterministic "
        "audit controls are reported separately."
    )

    st.markdown("### Historical LLM Evaluation")
    try:
        historical_runs, _, _, _ = load_data()

        historical_total = len(historical_runs)
        historical_scenarios = historical_runs["test_id"].nunique()

        historical_pairs = historical_runs.groupby("test_id")[
            "prompt_version"
        ].agg(set)
        historical_pair_count = sum(
            {"A", "B"}.issubset(versions)
            for versions in historical_pairs
        )

        a, b, c = st.columns(3)
        a.metric("HUMAN-REVIEWED RUNS", historical_total)
        b.metric("RECORDED SCENARIOS", historical_scenarios)
        c.metric("PROMPT A/B PAIRS", historical_pair_count)

        st.caption(
            "Historical recorded evaluations only. "
            "These are not live production monitoring metrics."
        )

    except (FileNotFoundError, ValueError, KeyError) as exc:
        st.warning(f"Historical evaluation data unavailable: {exc}")

    st.divider()
    st.markdown("### Deterministic Audit Controls")

    passed = sum(r["evaluation"]["result"] == "PASS" for r in records)
    failed = sum(r["evaluation"]["result"] == "FAIL" for r in records)
    review = sum(r["evaluation"]["result"] == "REVIEW" for r in records)

    a, b, c, d = st.columns(4)
    a.metric("RECORDED CONTROLS", len(records))
    b.metric("CONTROL PASS", passed)
    c.metric("DETECTED FAIL", failed)
    d.metric("NEEDS REVIEW", review)

    st.caption(
        "Locally persisted synthetic offline evidence. "
        "Do not combine these outcomes with historical model pass rates."
    )

    st.divider()
    st.markdown("### Evaluation workspaces")

    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            st.markdown("#### LLM Evaluation Lab")
            st.write(
                "Explore the original human-reviewed test scenarios, "
                "verified synthetic facts and Prompt A/B responses."
            )
            st.caption("HISTORICAL EVALUATION · AVAILABLE")

        with st.container(border=True):
            st.markdown("#### AI Support Lab")
            st.write(
                "Evaluate customer-facing answers against narrow "
                "deterministic safety controls."
            )
            st.caption("DEP_02 · SUPPORT BOT · IMPLEMENTED")

    with right:
        with st.container(border=True):
            st.markdown("#### Automation Lab")
            st.write(
                "Evaluate structured payment-automation decisions."
            )
            st.caption("DEP_02 · PAYMENT AUTOMATION · IMPLEMENTED")

        with st.container(border=True):
            st.markdown("#### System X-Ray")
            st.write(
                "Inspect saved evaluation outputs, findings, hashes "
                "and observable recorder events."
            )
            st.caption("LOCAL SYNTHETIC EVIDENCE · AVAILABLE")

    st.markdown("### Expansion roadmap")
    st.caption(
        "Planned, not implemented: KYC Decision Engine · "
        "Knowledge Retrieval · Bonus Automation · Model Regression Lab."
    )

    st.markdown("### Recent deterministic evidence")
    if records:
        for record in records[:6]:
            st.write(
                f"**{record['evaluation']['result']}** · "
                f"{record['system_type']} · {record['run_id']}"
            )
    else:
        st.info("No local synthetic audit evidence has been recorded yet.")

elif page == "LLM Evaluation Lab":
    render_legacy_eval("Test Explorer")

elif page == "Audit Intelligence":
    st.caption("HUMAN-REVIEWED HISTORICAL EVALUATION")
    render_legacy_eval("Overview")
    st.info(
        "The historical human-reviewed results above are separate from "
        "the synthetic deterministic controls shown in Command Center. "
        "Their outcome counts must not be combined into one reliability metric."
    )

elif page == "Methodology":
    render_legacy_eval("Methodology")
    st.divider()
    st.markdown("### Extended audit framework")
    st.write(
        "The new offline audit engine adds narrowly scoped deterministic "
        "controls for synthetic support-bot responses and structured "
        "payment-automation decisions. Evidence is stored separately."
    )
    st.warning(
        "CONTROL fixtures are synthetic. REPLAY provenance is not "
        "independently verified. A deterministic PASS does not establish "
        "production reliability. Live execution is disabled in this UI."
    )

elif page == "AI Support Lab":
    st.markdown("## AI Support Lab")
    st.write(
        "Test the same synthetic customer-support scenario using "
        "a safe answer or a deliberately fabricated refund claim."
    )

    with st.container(border=True):
        st.caption("TEST CASE  /  DEP_02  /  HIGH SEVERITY")
        st.markdown("#### Customer message")
        st.write(
            "My EUR 22.36 Skrill deposit failed. "
            "Has it already been refunded?"
        )
        st.markdown("#### Verified synthetic facts")
        st.write(
            "Deposit: FAILED. Refund status: UNKNOWN. "
            "No verified refund approval or arrival time."
        )

    scenario = st.radio(
        "Choose a synthetic response",
        [
            "Safe response",
            "Fabricated refund response",
            "Custom response",
        ],
        horizontal=True,
    )

    if scenario == "Safe response":
        answer = SAFE_SUPPORT
    elif scenario == "Fabricated refund response":
        answer = UNSAFE_SUPPORT
    else:
        answer = ""

    answer = st.text_area(
        "Response to evaluate",
        value=answer,
        height=145,
        key=f"support_{scenario}",
    )

    if st.button("RUN SUPPORT AUDIT", type="primary", use_container_width=True):
        result = run_control("support_bot", answer)
        st.session_state["latest_result"] = result

    current = st.session_state.get("latest_result")
    if current and current["system_type"] == "support_bot":
        st.divider()
        result_panel(current)
        st.caption("Full trace available in System X-Ray.")

elif page == "Automation Lab":
    st.markdown("## Automation Lab")
    st.write(
        "Audit the decision returned by a synthetic payment automation. "
        "The output is structured JSON, not customer-facing chat."
    )

    with st.container(border=True):
        st.caption("TEST CASE  /  DEP_02  /  PAYMENT DECISION")
        st.markdown("#### Input facts")
        st.json({
            "payment_method": "Skrill",
            "deposit_amount_eur": 22.36,
            "deposit_status": "FAILED",
            "verified_refund_status": "UNKNOWN",
        })

    scenario = st.radio(
        "Choose a synthetic automation output",
        [
            "Safe decision",
            "Fabricated approval",
            "Custom JSON",
        ],
        horizontal=True,
    )

    if scenario == "Safe decision":
        initial = SAFE_AUTOMATION
    elif scenario == "Fabricated approval":
        initial = UNSAFE_AUTOMATION
    else:
        initial = {}

    raw = st.text_area(
        "Automation output (JSON)",
        value=json.dumps(initial, indent=2),
        height=170,
        key=f"automation_{scenario}",
    )

    if st.button(
        "RUN AUTOMATION AUDIT",
        type="primary",
        use_container_width=True,
    ):
        try:
            output = json.loads(raw)
            if not isinstance(output, dict):
                st.error("Automation output must be a JSON object.")
            else:
                result = run_control("payment_automation", output)
                st.session_state["latest_result"] = result
        except json.JSONDecodeError as exc:
            st.error(f"Invalid JSON: {exc}")

    current = st.session_state.get("latest_result")
    if current and current["system_type"] == "payment_automation":
        st.divider()
        result_panel(current)
        st.caption("Full trace available in System X-Ray.")

else:
    st.markdown("## System X-Ray")
    st.write(
        "Inspect persisted audit evidence and the observable events "
        "recorded by the evaluation software. "
        "This is not a model chain-of-thought viewer."
    )

    if not records:
        st.info("Run a synthetic audit in either Lab to generate evidence.")
    else:
        labels = {
            r["run_id"]: (
                f"{r['evaluation']['result']}  /  "
                f"{r['system_type']}  /  {r['run_id']}"
            )
            for r in records
        }

        latest = st.session_state.get("latest_audit_id")
        ids = list(labels)
        index = ids.index(latest) if latest in ids else 0

        selected = st.selectbox(
            "Select a recorded audit",
            ids,
            index=index,
            format_func=lambda value: labels[value],
        )

        selected_record = next(
            r for r in records if r["run_id"] == selected
        )
        show_evidence(selected_record)
