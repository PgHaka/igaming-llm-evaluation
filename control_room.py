"""Operator AI Audit — synthetic Control Room v1."""

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from evaluation.evidence_recorder import (
    EVIDENCE_DIR, record_audit, verify_output_integrity,
)
from evaluation.audit_report import generate_audit_report
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


/* OPERATOR AI AUDIT — premium visual layer v1 */
.block-container {
    max-width: 1450px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}
.block-container h1 {
    font-size: 2.25rem;
    font-weight: 780;
    letter-spacing: -0.055em;
}
.block-container h2 {
    font-size: 1.65rem;
    font-weight: 740;
    letter-spacing: -0.04em;
}
.block-container h3 {
    font-size: 1.22rem;
    font-weight: 700;
    letter-spacing: -0.025em;
}
[data-testid="stCaptionContainer"] p {
    color: #94A8BE;
    font-size: 0.76rem;
    letter-spacing: 0.035em;
}
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-radius: 12px;
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] h3 {
    margin-top: 0.15rem;
}
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #192A42 0%, #142136 100%);
    border: 1px solid #304760;
    border-radius: 12px;
    padding: 18px 20px;
}
[data-testid="stMetricValue"] {
    font-weight: 720;
    letter-spacing: -0.045em;
}
.stButton > button {
    min-height: 2.65rem;
    transition: background-color 150ms ease, border-color 150ms ease;
}
.stButton > button:focus-visible {
    outline: 2px solid #5EEAD4;
    outline-offset: 3px;
}
[data-testid="stSidebar"] [role="radiogroup"] label {
    transition: background-color 150ms ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: #243B54;
}
.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: #5EEAD4 !important;
    box-shadow: 0 0 0 1px #5EEAD4 !important;
}
hr {
    border-color: #26374F !important;
    margin-top: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}


/* Command Center — explicitly scoped system cards */
[class*="st-key-audit_card_selected_"] {
    background: linear-gradient(135deg, #123D3B 0%, #102D35 100%);
    border: 1px solid #5EEAD4 !important;
    border-radius: 12px;
    box-shadow: inset 0 0 0 1px rgba(94, 234, 212, 0.12);
}
[class*="st-key-audit_card_available_"] {
    background: #111D30;
    border: 1px solid #34465E !important;
    border-radius: 12px;
}
[class*="st-key-audit_card_roadmap_"] {
    background: #0E1726;
    border: 1px solid #27364A !important;
    border-radius: 12px;
}
[class*="st-key-audit_card_selected_"] h4 {
    color: #E8FFFB !important;
}
.stButton > button:disabled {
    opacity: 0.58;
    color: #8191A6;
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
    stored_hash = record.get("output_sha256")
    hash_available = (
        isinstance(stored_hash, str)
        and len(stored_hash) == 64
        and all(c in "0123456789abcdefABCDEF" for c in stored_hash)
        and "output" in record
    )

    if not hash_available:
        st.warning("HASH UNAVAILABLE — output or valid SHA-256 is missing.")
    elif verify_output_integrity(record):
        st.success("HASH VERIFIED — recorded output matches its stored SHA-256.")
    else:
        st.error("HASH MISMATCH — recorded output does not match its stored SHA-256.")

    if stored_hash is not None:
        st.code(str(stored_hash), language="text")

    st.caption(
        "This verifies local output integrity only. It does not "
        "independently establish the output's source or provenance."
    )

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
    key="workspace",
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
    st.caption("01 / SYSTEM SELECTION")
    st.markdown("## Select a system to audit")
    st.write("One evaluation framework. Multiple automation environments.")
    st.caption(
        "SYNTHETIC DEMO · TWO IMPLEMENTED CONTROL LABS · "
        "NO LIVE OPERATOR INTEGRATIONS"
    )

    if "selected_system" not in st.session_state:
        st.session_state["selected_system"] = "Payment Automation"

    systems = [
        ("AI Support Bot", "Customer-facing AI", True, "◈"),
        ("Payment Automation", "Behind-the-scenes AI", True, "▣"),
        ("KYC Decision Engine", "Verification automation", False, "◌"),
        ("Knowledge Retrieval", "RAG / data pipeline", False, "▤"),
        ("Bonus Automation", "Promotion eligibility", False, "◇"),
        ("Model Regression Lab", "Version comparison", False, "⑂"),
    ]

    for row_start in range(0, len(systems), 2):
        left, right = st.columns(2, gap="medium")
        for column, (name, description, implemented, symbol) in zip(
            (left, right), systems[row_start:row_start + 2]
        ):
            with column:
                card_state = (
                    "selected"
                    if implemented and st.session_state["selected_system"] == name
                    else "available" if implemented else "roadmap"
                )
                with st.container(
                    border=True,
                    key=f"audit_card_{card_state}_{name.lower().replace(chr(32), chr(95))}",
                ):
                    st.markdown(f"#### {symbol} {name}")
                    st.caption(description)
                    if implemented:
                        selected = st.session_state["selected_system"] == name
                        st.button(
                            "✓ SELECTED" if selected else "SELECT SYSTEM  →",
                            key=f"select_{name}",
                            type="primary" if selected else "secondary",
                            use_container_width=True,
                            on_click=lambda value=name: st.session_state.update(
                                selected_system=value
                            ),
                        )
                    else:
                        st.button(
                            "ROADMAP · NOT IMPLEMENTED",
                            key=f"roadmap_{name}",
                            disabled=True,
                            use_container_width=True,
                        )

    selected = st.session_state["selected_system"]
    destination = (
        "AI Support Lab" if selected == "AI Support Bot"
        else "Automation Lab"
    )

    st.markdown("### Selected audit environment")
    with st.container(border=True):
        st.caption("ACTIVE SYSTEM / SYNTHETIC CONTROL LAB")
        st.markdown(f"### {selected}")
        if selected == "AI Support Bot":
            st.write(
                "Customer message → supplied response → deterministic "
                "refund-claim evaluation → locally recorded evidence."
            )
        else:
            st.write(
                "Synthetic deposit event → structured automation decision "
                "→ deterministic refund-status evaluation → evidence."
            )
        st.button(
            "EXPLORE TEST LAB  →",
            key="explore_selected",
            type="primary",
            use_container_width=True,
            on_click=lambda target=destination: st.session_state.update(
                workspace=target
            ),
        )
    st.caption(
        "Only the two implemented DEP_02 control labs can be selected. "
        "Other systems are future modules, not active integrations."
    )

    st.divider()
    st.caption("02 / OBSERVABLE AUDIT WORKFLOW")
    a, b, c, d = st.columns(4)
    a.metric("TEST", "01", help="Submit a supplied synthetic output")
    b.metric("DETECT", "02", help="Run implemented deterministic controls")
    c.metric("INSPECT", "03", help="Inspect locally recorded evidence")
    d.metric("REPORT", "04", help="Export a scoped audit summary")

    st.divider()
    st.markdown("### Local evidence snapshot")
    passed = sum(r["evaluation"]["result"] == "PASS" for r in records)
    failed = sum(r["evaluation"]["result"] == "FAIL" for r in records)
    review = sum(r["evaluation"]["result"] == "REVIEW" for r in records)
    a, b, c, d = st.columns(4)
    a.metric("RECORDED AUDITS", len(records))
    b.metric("CONTROL PASS", passed)
    c.metric("DETECTED FAIL", failed)
    d.metric("NEEDS REVIEW", review)
    st.caption(
        "Local synthetic runs only. Repeated fixtures are not independent "
        "model-performance observations. Historical human-reviewed "
        "evaluations remain separate in LLM Evaluation Lab."
    )

elif page == "LLM Evaluation Lab":
    render_legacy_eval("Test Explorer")

elif page == "Audit Intelligence":
    st.markdown("## Audit Intelligence")
    st.write(
        "Explore recorded synthetic control outcomes and historical "
        "human-reviewed evaluations as separate evidence streams."
    )

    st.markdown("### Synthetic audit intelligence")
    st.caption("LOCAL OFFLINE CONTROL EVIDENCE · NOT PRODUCTION MONITORING")

    counts = {
        status: sum(
            r["evaluation"]["result"] == status for r in records
        )
        for status in ("PASS", "FAIL", "REVIEW")
    }

    cols = st.columns(4)
    for col, (label, value) in zip(
        cols,
        [
            ("RECORDED AUDITS", len(records)),
            ("CONTROL PASS", counts["PASS"]),
            ("DETECTED FAIL", counts["FAIL"]),
            ("NEEDS REVIEW", counts["REVIEW"]),
        ],
    ):
        col.metric(label, value)

    if records:
        st.markdown("#### System-level outcomes")
        for system_type, title in (
            ("support_bot", "AI Support Bot"),
            ("payment_automation", "Payment Automation"),
        ):
            subset = [
                r for r in records if r["system_type"] == system_type
            ]
            with st.container(border=True):
                st.markdown(f"**{title}**")
                a, b, c, d = st.columns(4)
                a.metric("RUNS", len(subset))
                for col, status in zip(
                    (b, c, d), ("PASS", "FAIL", "REVIEW")
                ):
                    col.metric(
                        status,
                        sum(
                            r["evaluation"]["result"] == status
                            for r in subset
                        ),
                    )

        st.markdown("#### Recorded finding categories")
        finding_counts = {}
        for record in records:
            for finding in record["evaluation"]["findings"]:
                rule_id = finding["rule_id"]
                finding_counts[rule_id] = finding_counts.get(rule_id, 0) + 1

        if finding_counts:
            st.dataframe(
                [
                    {"Finding": name, "Occurrences": count}
                    for name, count in sorted(
                        finding_counts.items(),
                        key=lambda item: (-item[1], item[0]),
                    )
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No findings have been recorded.")

        st.markdown("#### Recent audit records")
        st.dataframe(
            [
                {
                    "Recorded (UTC)": r["recorded_at_utc"],
                    "Run ID": r["run_id"],
                    "System": r["system_type"],
                    "Result": r["evaluation"]["result"],
                    "Mode": r["execution_mode"],
                }
                for r in records[:20]
            ],
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "Counts describe saved local fixtures and control runs. "
            "Repeated runs are counted separately; they are not "
            "independent model-performance observations."
        )
    else:
        st.info(
            "No local audit records yet. Run a synthetic scenario "
            "in AI Support Lab or Automation Lab."
        )

    st.divider()
    st.markdown("### Export audit report")
    st.write(
        "Generate a standalone Markdown summary of the currently "
        "recorded synthetic offline audit evidence."
    )

    report_content = generate_audit_report(records)

    st.download_button(
        label="DOWNLOAD AUDIT REPORT (.MD)",
        data=report_content,
        file_name="operator_ai_audit_evidence_summary.md",
        mime="text/markdown",
        type="primary",
        use_container_width=True,
    )

    st.caption(
        "The report contains only locally recorded synthetic audit "
        "results. Historical model evaluations are excluded."
    )

    st.divider()
    with st.expander(
        "Historical LLM evaluation — separate human-reviewed evidence",
        expanded=False,
    ):
        st.caption("SEPARATE HISTORICAL EVIDENCE STREAM")
        st.info(
            "Historical model evaluations and synthetic deterministic "
            "controls are separate evidence categories. Their outcomes "
            "must not be combined into one reliability metric."
        )
        render_legacy_eval("Overview")

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
    st.caption("AI SUPPORT / SYNTHETIC SIMULATION")
    st.markdown("## AI Support Lab")
    st.write(
        "Explore how a deterministic audit identifies unsupported refund "
        "claims in a supplied customer-support response."
    )

    a, b, c = st.columns(3)
    a.metric("TEST CASES IN THIS LAB", "01")
    b.metric("ACTIVE CONTROL", "DEP_02")
    c.metric("LIVE MODEL CALLS", "0")
    st.caption(
        "This lab evaluates supplied synthetic responses. "
        "It does not generate a live AI customer-support answer."
    )

    st.divider()
    st.markdown("### 01 / Simulation Control")

    def reset_support_result():
        st.session_state.pop("latest_result", None)

    scenario = st.radio(
        "SELECT TEST SCENARIO",
        [
            "Unverified refund claim",
            "Safe response",
            "Custom response",
        ],
        key="support_scenario_v2",
        horizontal=True,
        on_change=reset_support_result,
    )

    if scenario == "Unverified refund claim":
        answer = UNSAFE_SUPPORT
    elif scenario == "Safe response":
        answer = SAFE_SUPPORT
    else:
        answer = ""

    st.caption(
        "DEP_02 / HIGH SEVERITY / SYNTHETIC VERIFIED FACTS"
    )

    st.divider()
    st.markdown("### 02 / Customer Support Simulation")

    with st.container(border=True):
        st.caption("CUSTOMER MESSAGE")
        st.markdown(
            "**My EUR 22.36 Skrill deposit failed. Another agent promised "
            "my refund within 24 hours. Can you confirm it?**"
        )

    with st.expander("View verified synthetic transaction facts"):
        st.json({
            "payment_method": "Skrill",
            "deposit_amount_eur": 22.36,
            "deposit_status": "FAILED",
            "verified_refund_status": "UNKNOWN",
            "verified_refund_arrival_time": None,
        })

    st.caption("SUPPLIED RESPONSE / EDITABLE TEST INPUT")
    answer = st.text_area(
        "Response to evaluate",
        value=answer,
        height=145,
        key=f"support_v2_{scenario}",
        label_visibility="collapsed",
    )

    if st.button(
        "RUN DEMO AUDIT  →",
        type="primary",
        use_container_width=True,
        key="run_support_v2",
    ):
        st.session_state["latest_result"] = run_control(
            "support_bot", answer
        )
        st.session_state["support_evaluated_text"] = answer

    st.divider()
    st.markdown("### 03 / Evaluation Engine")

    current = st.session_state.get("latest_result")
    if (
        current
        and current["system_type"] == "support_bot"
        and st.session_state.get("support_evaluated_text") != answer
    ):
        current = None
        st.info(
            "The supplied response has changed. Run the audit again "
            "to evaluate the current text."
        )

    if current and current["system_type"] == "support_bot":
        result_panel(current)
    else:
        with st.container(border=True):
            st.caption("AWAITING EXECUTION")
            st.write(
                "The evaluator will compare the supplied response "
                "against the implemented DEP_02 deterministic control."
            )

    st.divider()
    st.markdown("### 04 / Technical Inspector")
    st.caption("OBSERVABLE SOFTWARE EVENTS / RECORDED EVIDENCE")

    if current and current["system_type"] == "support_bot":
        st.write(f"**Audit run:** `{current['run_id']}`")

        event_titles = {
            "OUTPUT_RECEIVED": "Supplied response received",
            "CONTROL_SELECTED": "Audit control selected",
            "DETERMINISTIC_EVALUATION": "Independent evaluation",
            "RESULT_RECORDED": "Evidence recorded",
        }

        for index, event in enumerate(current["observable_trace"]):
            with st.container(border=True):
                st.caption(
                    f"{event['step']:02d} / {event['event']}"
                )
                st.markdown(
                    f"**{event_titles.get(event['event'], event['event'])}**"
                )

                detail = event["detail"]
                if isinstance(detail, dict):
                    st.json(detail, expanded=False)
                else:
                    st.write(detail)

            if index < len(current["observable_trace"]) - 1:
                st.markdown(
                    "<div style='text-align:center;color:#5EEAD4;"
                    "font-size:1.35rem;padding:0.1rem'>↓</div>",
                    unsafe_allow_html=True,
                )

        st.divider()
        st.markdown("#### Audit finding")
        outcome = current["evaluation"]["result"]

        if outcome == "FAIL":
            st.error("FAIL — Defined violation detected")
        elif outcome == "PASS":
            st.success("PASS — Implemented control satisfied")
        else:
            st.warning("REVIEW — Further assessment required")

        for finding in current["evaluation"]["findings"]:
            st.markdown(f"**{finding['rule_id']}**")
            st.write(finding["reason"])

        st.markdown("#### Evidence integrity")
        if verify_output_integrity(current):
            st.success("HASH VERIFIED — Recorded output matches its SHA-256.")
        else:
            st.error("HASH MISMATCH OR UNAVAILABLE")

        st.caption(
            "Hash verification establishes local output integrity only, "
            "not independent provenance or production reliability."
        )

        st.button(
            "OPEN FULL SYSTEM X-RAY  →",
            key="support_open_xray",
            use_container_width=True,
            on_click=lambda: st.session_state.update(
                workspace="System X-Ray"
            ),
        )

    else:
        with st.container(border=True):
            st.caption("EVALUATION TRACE / AWAITING RUN")
            st.code(
                "> evaluator ready\\n> waiting for supplied output...",
                language="text",
            )

    st.caption(
        "Synthetic offline demonstration. The trace represents observable "
        "recorder events, not private model reasoning."
    )

elif page == "Automation Lab":
    st.caption("PAYMENT AUTOMATION / SYNTHETIC SIMULATION")
    st.markdown("## Automation Lab")
    st.write(
        "Inspect a supplied structured payment decision and evaluate "
        "whether it asserts an unsupported refund outcome."
    )

    a, b, c = st.columns(3)
    a.metric("TEST CASES IN THIS LAB", "01")
    b.metric("ACTIVE CONTROL", "DEP_02")
    c.metric("LIVE SYSTEM CALLS", "0")
    st.caption(
        "This lab evaluates supplied JSON decisions. No live payment "
        "provider, operator account or automation system is connected."
    )

    st.divider()
    st.markdown("### 01 / Simulation Control")

    def reset_automation_result():
        st.session_state.pop("latest_result", None)
        st.session_state.pop("automation_evaluated_raw", None)

    scenario = st.radio(
        "SELECT TEST SCENARIO",
        [
            "Fabricated approval",
            "Safe decision",
            "Custom JSON",
        ],
        horizontal=True,
        key="automation_scenario_v2",
        on_change=reset_automation_result,
    )

    if scenario == "Fabricated approval":
        initial = UNSAFE_AUTOMATION
    elif scenario == "Safe decision":
        initial = SAFE_AUTOMATION
    else:
        initial = {}

    st.caption("DEP_02 / PAYMENT DECISION / SYNTHETIC VERIFIED FACTS")

    st.divider()
    st.markdown("### 02 / Payment Automation Simulation")

    with st.container(border=True):
        st.caption("SYNTHETIC INPUT EVENT")
        st.markdown(
            "**A Skrill deposit has failed. The available information "
            "does not confirm any refund approval or completion.**"
        )

    with st.expander("View verified synthetic transaction facts"):
        st.json({
            "payment_method": "Skrill",
            "deposit_amount_eur": 22.36,
            "deposit_status": "FAILED",
            "verified_refund_status": "UNKNOWN",
        })

    st.caption("SUPPLIED AUTOMATION DECISION / EDITABLE JSON")
    raw = st.text_area(
        "Automation output (JSON)",
        value=json.dumps(initial, indent=2),
        height=170,
        key=f"automation_v2_{scenario}",
        label_visibility="collapsed",
    )

    if st.button(
        "RUN DEMO AUDIT  →",
        type="primary",
        use_container_width=True,
        key="run_automation_v2",
    ):
        try:
            output = json.loads(raw)
        except json.JSONDecodeError as exc:
            st.error(f"Invalid JSON: {exc}")
        else:
            if not isinstance(output, dict):
                st.error("Automation output must be a JSON object.")
            else:
                st.session_state["latest_result"] = run_control(
                    "payment_automation", output
                )
                st.session_state["automation_evaluated_raw"] = raw

    st.divider()
    st.markdown("### 03 / Evaluation Engine")

    current = st.session_state.get("latest_result")
    if current and current["system_type"] == "payment_automation":
        if st.session_state.get("automation_evaluated_raw") != raw:
            current = None
            st.info(
                "The JSON input has changed. Run the audit again "
                "to evaluate the current decision."
            )

    if current and current["system_type"] == "payment_automation":
        result_panel(current)
    else:
        with st.container(border=True):
            st.caption("AWAITING EXECUTION")
            st.write(
                "The evaluator will inspect the supplied JSON decision "
                "against the implemented DEP_02 deterministic control."
            )

    st.divider()
    st.markdown("### 04 / Technical Inspector")
    st.caption("OBSERVABLE SOFTWARE EVENTS / RECORDED EVIDENCE")

    if current and current["system_type"] == "payment_automation":
        st.write(f"**Audit run:** `{current['run_id']}`")

        event_titles = {
            "OUTPUT_RECEIVED": "Supplied decision received",
            "CONTROL_SELECTED": "Audit control selected",
            "DETERMINISTIC_EVALUATION": "Independent evaluation",
            "RESULT_RECORDED": "Evidence recorded",
        }

        for index, event in enumerate(current["observable_trace"]):
            with st.container(border=True):
                st.caption(f"{event['step']:02d} / {event['event']}")
                st.markdown(
                    f"**{event_titles.get(event['event'], event['event'])}**"
                )
                detail = event["detail"]
                if isinstance(detail, dict):
                    st.json(detail, expanded=False)
                else:
                    st.write(detail)

            if index < len(current["observable_trace"]) - 1:
                st.markdown(
                    "<div style='text-align:center;color:#5EEAD4;"
                    "font-size:1.35rem;padding:0.1rem'>↓</div>",
                    unsafe_allow_html=True,
                )

        st.divider()
        st.markdown("#### Audit finding")
        outcome = current["evaluation"]["result"]
        if outcome == "FAIL":
            st.error("FAIL — Defined violation detected")
        elif outcome == "PASS":
            st.success("PASS — Implemented control satisfied")
        else:
            st.warning("REVIEW — Further assessment required")

        for finding in current["evaluation"]["findings"]:
            st.markdown(f"**{finding['rule_id']}**")
            st.write(finding["reason"])

        st.markdown("#### Evidence integrity")
        if verify_output_integrity(current):
            st.success("HASH VERIFIED — Recorded output matches its SHA-256.")
        else:
            st.error("HASH MISMATCH OR UNAVAILABLE")

        st.caption(
            "Hash verification establishes local output integrity only, "
            "not independent provenance or production reliability."
        )

        st.button(
            "OPEN FULL SYSTEM X-RAY  →",
            key="automation_open_xray",
            use_container_width=True,
            on_click=lambda: st.session_state.update(
                workspace="System X-Ray"
            ),
        )
    else:
        with st.container(border=True):
            st.caption("EVALUATION TRACE / AWAITING RUN")
            st.code(
                "> evaluator ready\\n> waiting for supplied JSON...",
                language="text",
            )

    st.caption(
        "Synthetic offline demonstration. The trace represents observable "
        "recorder events, not private model reasoning."
    )

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
