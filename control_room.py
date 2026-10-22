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
from evaluation.demo_loader import load_bundled_examples
from ui.legacy_eval import render as render_legacy_eval
from ui.legacy_eval import load_data
from ui.system_icons import system_icon
from ui.audit_presentation import (
    support_audit_summary,
    automation_audit_summary,
)

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
    """Return only this visitor's non-persistent Control Room audit runs."""
    return sorted(
        st.session_state.get("session_audit_records", []),
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

    st.markdown("#### Audit finding")

    if evidence["system_type"] == "support_bot":
        summary = support_audit_summary(evidence)
    elif evidence["system_type"] == "payment_automation":
        summary = automation_audit_summary(evidence)
    else:
        summary = None

    if summary is not None:
        st.markdown(f"### {summary['title']}")
        st.write(summary["reason"])

    with st.expander("Original evaluator findings", expanded=False):
        for finding in evaluation["findings"]:
            st.markdown(f"**{finding['rule_id']}**")
            st.write(finding["reason"])
        if not evaluation["findings"]:
            st.caption("No evaluator findings were recorded.")

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

    trace = record["observable_trace"]
    with st.expander(
        f"Technical Inspector / {len(trace)} recorded events",
        expanded=False,
    ):
        st.caption(
            "Observable evaluation-software events. "
            "Not private model reasoning."
        )
        for event in trace:
            with st.expander(
                f"{event['step']:02d}  /  {event['event']}",
                expanded=False,
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
        persist=False,
    )
    st.session_state.setdefault("session_audit_records", []).append(evidence)
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
        "Payment Workflow Audit",
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
bundled_examples = load_bundled_examples()

if page != "Command Center":
    st.markdown("# Operator AI Audit")
    st.caption(
        "CONTROL ROOM  /  SYNTHETIC PROOF OF CONCEPT  /  "
        "INDEPENDENT EVALUATION"
    )
    st.divider()

if page == "Command Center":
    st.caption("OPERATOR AI AUDIT / INDEPENDENT QUALITY CONTROL")
    st.markdown("# Is your automation behaving as expected?")
    st.markdown(
        "Test defined operational controls. Detect unsupported AI outputs. "
        "Inspect the evidence behind every recorded result."
    )

    with st.container(border=True):
        st.caption("WHY THIS MATTERS")
        st.markdown("### A convincing AI answer can still be wrong.")
        st.write(
            "A support bot may promise an unverified refund. "
            "A payment automation may recommend a decision that the "
            "available transaction facts do not justify."
        )
        st.caption(
            "OFFLINE SYNTHETIC DEMONSTRATION · "
            "NO LIVE MODEL EXECUTION OR OPERATOR INTEGRATIONS"
        )

    st.divider()

    st.caption("01 / SYSTEM SELECTION")
    st.markdown("## Choose your audit environment")
    st.write(
        "Start with one of the two interactive demonstrations below. "
        "Additional system types are shown as future modules."
    )

    if "selected_system" not in st.session_state:
        st.session_state["selected_system"] = "AI Support Bot"

    available_systems = [
        ("AI Support Bot", "Customer-facing AI", True),
        ("Payment Automation", "Internal workflow quality control", True),
    ]

    roadmap_systems = [
        ("KYC Decision Engine", "Verification automation", False),
        ("Knowledge Retrieval", "RAG / data pipeline", False),
        ("Bonus Automation", "Promotion eligibility", False),
        ("Model Regression Lab", "Version comparison", False),
    ]

    for row_start in range(0, len(available_systems), 2):
        left, right = st.columns(2, gap="medium")
        for column, (name, description, implemented) in zip(
            (left, right), available_systems[row_start:row_start + 2]
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
                    st.markdown(
                        system_icon(name, implemented=implemented),
                        unsafe_allow_html=True,
                    )
                    display_name = (
                        "Payment Workflow Audit"
                        if name == "Payment Automation"
                        else name
                    )
                    st.markdown(f"#### {display_name}")
                    st.caption(description)
                    if name == "AI Support Bot":
                        st.markdown(
                            "**Your AI support bot is always available. "
                            "But is it always accurate?**"
                        )
                    if name == "Payment Automation":
                        st.markdown(
                            "**Automation reduces manual workload. "
                            "But who validates the automation?**"
                        )
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
        else "Payment Workflow Audit"
    )

    st.markdown("### Your first audit")
    with st.container(border=True):
        st.caption("READY TO EXPLORE / INTERACTIVE SYNTHETIC DEMO")

        if selected == "AI Support Bot":
            st.markdown("### Can a chatbot promise an unverified refund?")
            st.write(
                "Follow a realistic-looking customer-support conversation "
                "in which a customer asks whether a failed deposit has "
                "already been refunded."
            )
            st.write(
                "Compare supplied safe and unsafe chatbot responses, "
                "run the audit and see exactly which defined rule was triggered."
            )
            action_label = "EXPLORE AI SUPPORT DEMO  →"
        else:
            st.markdown("### Who validates your automated payment workflow?")
            st.write(
                "Payment-case automation can help teams reduce repetitive "
                "manual work, particularly when exception volumes increase. "
                "But its recommendations still need quality controls."
            )
            st.write(
                "Explore a fictional internal payment workflow. Compare "
                "supplied safe and unsafe handling recommendations, then "
                "audit whether they are supported by the available "
                "synthetic transaction facts."
            )
            action_label = "EXPLORE PAYMENT WORKFLOW AUDIT  →"

        st.button(
            action_label,
            key="explore_selected",
            type="primary",
            use_container_width=True,
            on_click=lambda target=destination: st.session_state.update(
                workspace=target
            ),
        )
        st.caption(
            "Uses supplied synthetic outputs and deterministic controls. "
            "No live chatbot, payment processing or operator connection."
        )
    st.caption(
        "Only the two implemented DEP_02 control labs can be selected. "
        "Other systems are future modules, not active integrations."
    )


    st.markdown("### Future modules")
    st.caption("PRODUCT ROADMAP / NOT IMPLEMENTED")
    for row_start in range(0, len(roadmap_systems), 2):
        left, right = st.columns(2, gap="medium")
        for column, (name, description, implemented) in zip(
            (left, right), roadmap_systems[row_start:row_start + 2]
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
                    st.markdown(
                        system_icon(name, implemented=implemented),
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"#### {name}")
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

    st.divider()
    st.caption("02 / OBSERVABLE AUDIT WORKFLOW")
    st.markdown("### From test input to reviewable evidence")

    workflow = [
        ("01 / TEST", "Submit a supplied synthetic output."),
        ("02 / DETECT", "Evaluate defined operational controls."),
        ("03 / INSPECT", "Inspect recorded audit evidence."),
        ("04 / REPORT", "Export a scoped audit summary."),
    ]

    columns = st.columns(4, gap="medium")
    for column, (stage, description) in zip(columns, workflow):
        with column:
            with st.container(border=True):
                st.markdown(f"#### {stage}")
                st.write(description)

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
    st.caption("AUDIT INTELLIGENCE / EVIDENCE & REPORTING")
    st.markdown("## Audit Intelligence")
    st.markdown(
        "A unified view of deterministic control outcomes, evidence "
        "integrity and downloadable audit reporting."
    )
    st.caption(
        "SYNTHETIC OFFLINE ENVIRONMENT · NO LIVE OPERATOR MONITORING"
    )
    st.divider()

    st.caption("01 / REFERENCE EVIDENCE")
    st.markdown("### Bundled demonstration evidence")
    st.caption(
        "TWO PRE-SUPPLIED DEMONSTRATION FIXTURES · NOT VISITOR-GENERATED "
        "RUNS OR LIVE OPERATOR OBSERVATIONS"
    )
    example_columns = st.columns(2, gap="medium")
    for column, example in zip(example_columns, bundled_examples):
        outcome = example["evaluation"]["result"]
        integrity_ok = verify_output_integrity(example)
        summary = (
            support_audit_summary(example)
            if example["system_type"] == "support_bot"
            else automation_audit_summary(example)
        )
        system_label = {
            "support_bot": "AI SUPPORT BOT",
            "payment_automation": "PAYMENT AUTOMATION",
        }.get(example["system_type"], example["system_type"].upper())

        with column:
            with st.container(border=True):
                st.caption(system_label + " / BUNDLED EXAMPLE")
                if outcome == "FAIL":
                    st.error("FAIL — CONTROL VIOLATION DETECTED")
                elif outcome == "PASS":
                    st.success("PASS — DEFINED CONTROL SATISFIED")
                else:
                    st.warning("REVIEW — MANUAL ASSESSMENT REQUIRED")
                st.markdown(f"#### {summary['title']}")
                st.write(summary["reason"])
                st.caption(
                    f"{example['run_id']} · PRE-SUPPLIED SYNTHETIC CONTROL FIXTURE"
                )
                st.divider()
                st.caption("EVIDENCE INTEGRITY / NOT AN AUDIT OUTCOME")
                if integrity_ok:
                    st.markdown("**SHA-256 · VERIFIED**")
                else:
                    st.error("SHA-256 · MISMATCH")
    st.caption(
        "Open System X-Ray to inspect each example's output, findings "
        "and four observable recorder events."
    )

    st.divider()
    st.caption("02 / YOUR SESSION")
    st.markdown("### Session audit activity")
    st.caption(
        "VISITOR-GENERATED OFFLINE CONTROLS · SESSION-ONLY STORAGE · "
        "NOT PRODUCTION MONITORING"
    )

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
            ("SESSION AUDITS", len(records)),
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
            "Counts describe this session's synthetic control runs. "
            "Repeated runs are counted separately; they are not "
            "independent model-performance observations."
        )
    else:
        with st.container(border=True):
            st.caption("SESSION STATUS / READY")
            st.markdown("#### Your audit workspace is ready")
            st.write(
                "No visitor-generated audit runs in this session yet. "
                "Start with AI Support Lab or Automation Lab to create "
                "your first synthetic control record."
            )
            st.caption(
                "Bundled examples above remain separate from your session activity."
            )

    st.divider()
    st.caption("03 / EVIDENCE EXPORT")
    st.markdown("### Export audit report")

    with st.container(border=True):
        st.caption("AUDIT EVIDENCE / PORTABLE MARKDOWN REPORT")
        st.markdown("#### Generate evidence report")
        st.write(
            "Download a structured record of the bundled synthetic examples "
            "and any audit runs generated during this visitor session. "
            "The report identifies evidence origins, control outcomes, "
            "finding categories, run IDs and output SHA-256 hashes."
        )

        left, right = st.columns(2)
        left.metric("BUNDLED EXAMPLES", len(bundled_examples))
        right.metric("SESSION RUNS", len(records))

        st.caption(
            "SYNTHETIC OFFLINE EVIDENCE SUMMARY · "
            "NOT A PRODUCTION RELIABILITY OR COMPLIANCE CERTIFICATION"
        )

        report_content = generate_audit_report(bundled_examples + records)

        st.download_button(
            label="DOWNLOAD AUDIT REPORT (.MD)",
            data=report_content,
            file_name="operator_ai_audit_evidence_summary.md",
            mime="text/markdown",
            type="primary",
            use_container_width=True,
        )

        st.caption(
            "The report labels each evidence origin separately. Historical "
            "human-reviewed model evaluations are excluded. Session records "
            "are not retained as a permanent server-side audit archive."
        )

    st.divider()
    with st.expander(
        "04 / Historical LLM evaluation — separate human-reviewed evidence",
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
    st.caption("METHODOLOGY / EVALUATION SCOPE & EVIDENCE")
    st.markdown("## How the audit works")
    st.write(
        "Operator AI Audit applies defined deterministic controls to supplied "
        "synthetic support responses and structured automation decisions. "
        "It records the result and supporting local evaluation evidence."
    )
    st.caption(
        "CURRENT FRAMEWORK · SYNTHETIC OFFLINE CONTROL · "
        "NO LIVE MODEL OR OPERATOR EXECUTION"
    )
    st.divider()

    st.caption("01 / CURRENT AUDIT WORKFLOW")
    st.markdown("### From supplied output to inspectable evidence")
    for title, description in (
        (
            "1. Supply a test output",
            "Select a demonstration scenario or supply a response or JSON "
            "decision against the defined DEP_02 synthetic facts.",
        ),
        (
            "2. Apply the implemented control",
            "The deterministic evaluator checks the supplied output against "
            "its narrowly defined rules. This is not a general-purpose AI judge.",
        ),
        (
            "3. Record the outcome",
            "The local recorder captures PASS, FAIL or REVIEW, evaluator "
            "findings, the evaluated output and observable software events.",
        ),
        (
            "4. Inspect and export",
            "System X-Ray exposes the recorded evidence. Audit Intelligence "
            "summarises bundled examples and current-session audit runs "
            "and generates a Markdown evidence report.",
        ),
    ):
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(description)

    st.divider()
    st.caption("02 / OUTCOME INTERPRETATION")
    st.markdown("### What does an audit result establish?")
    left, middle, right = st.columns(3, gap="medium")
    with left:
        with st.container(border=True):
            st.success("PASS")
            st.write(
                "The supplied output satisfied the implemented control. "
                "This does not establish general correctness or reliability."
            )
    with middle:
        with st.container(border=True):
            st.error("FAIL")
            st.write(
                "The implemented control detected a defined violation "
                "in the supplied output."
            )
    with right:
        with st.container(border=True):
            st.warning("REVIEW")
            st.write(
                "The automatic assessment was insufficient or inconclusive. "
                "Human assessment is required."
            )

    st.divider()
    st.caption("03 / EVIDENCE BOUNDARIES")
    st.markdown("### What this demonstration does not establish")
    st.write(
        "Bundled fixtures are pre-supplied examples; visitor-generated audit "
        "records belong to the current session. Historical human-reviewed "
        "model evaluations are a separate evidence set."
    )
    st.write(
        "SHA-256 checks the recorded output against its stored hash; it does "
        "not independently verify provenance. Recorder events describe "
        "observable local evaluation-software activity, not private model "
        "reasoning or upstream execution."
    )
    st.info(
        "No live model calls, operator monitoring or real payment actions "
        "are performed by this interface. A control result is not a "
        "production reliability or compliance certification."
    )
    st.caption(
        "CONTROL fixtures are synthetic. REPLAY provenance is not "
        "independently verified."
    )

    st.divider()
    st.caption("04 / SEPARATE HISTORICAL EVIDENCE")
    st.markdown("### Human-reviewed LLM evaluation")
    st.write(
        "The earlier portfolio study used manually submitted Prompt A/B "
        "variants, recorded model responses and human-reviewed outcomes. "
        "Its methodology and source files remain available below; these "
        "historical results are not current deterministic audit runs."
    )
    with st.expander(
        "Open historical evaluation methodology and source files",
        expanded=False,
    ):
        render_legacy_eval("Methodology")

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

    st.caption(
        "NORTHSTAR GAMING / SIMULATED CUSTOMER SUPPORT CONVERSATION"
    )

    with st.container(border=True):
        st.caption("SYNTHETIC CHAT PREVIEW · NOT A LIVE CHATBOT")

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(
                "**Northstar Gaming Support**"
            )
            st.write(
                "Welcome to Northstar Gaming Support! "
                "How can I assist you today?"
            )

        with st.chat_message("user", avatar="👤"):
            st.markdown("**Customer**")
            st.write(
                "My EUR 22.36 Skrill deposit failed. Another agent "
                "promised my refund within 24 hours. Can you confirm it?"
            )

        st.divider()
        st.caption("SUPPLIED SYNTHETIC BOT RESPONSE / TEST INPUT")

        response_key = f"support_v2_{scenario}"
        if response_key not in st.session_state:
            st.session_state[response_key] = answer

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown("**Supplied Bot Response**")
            preview = st.session_state[response_key]
            if preview.strip():
                st.write(preview)
            else:
                st.caption("No response supplied yet.")

        with st.expander("✎ Edit test response", expanded=False):
            st.caption(
                "Edit the supplied synthetic response to test a different "
                "wording. This does not call a live AI model."
            )
            answer = st.text_area(
                "Response to evaluate",
                key=response_key,
                height=115,
                label_visibility="collapsed",
            )

    with st.expander("View verified synthetic transaction facts"):
        st.json({
            "payment_method": "Skrill",
            "deposit_amount_eur": 22.36,
            "deposit_status": "FAILED",
            "verified_refund_status": "UNKNOWN",
            "verified_refund_arrival_time": None,
        })

    st.caption(
        "The conversation is illustrative. The supplied response is "
        "evaluated offline against the defined DEP_02 control."
    )

    if st.button(
        "AUDIT THIS RESPONSE  →",
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
        summary = support_audit_summary(current)

        with st.container(border=True):
            st.caption("AUDIT OUTCOME / DEP_02")

            if summary["outcome"] == "FAIL":
                st.error("FAIL — " + summary["outcome_label"])
            elif summary["outcome"] == "PASS":
                st.success("PASS — " + summary["outcome_label"])
            else:
                st.warning("REVIEW — " + summary["outcome_label"])

            st.markdown("### " + summary["title"])
            st.write(summary["reason"])

        st.markdown("#### Evidence comparison")
        st.caption(
            "SUPPLIED RESPONSE VS. AVAILABLE SYNTHETIC TRANSACTION FACTS"
        )

        response_column, facts_column = st.columns(2, gap="medium")

        with response_column:
            with st.container(border=True):
                st.caption("SUPPLIED BOT OUTPUT")
                st.write(
                    summary["output"]
                    if summary["output"].strip()
                    else "No customer-facing response supplied."
                )

        with facts_column:
            with st.container(border=True):
                st.caption("VERIFIED SYNTHETIC FACTS")
                st.markdown("**Deposit status:** FAILED")
                st.markdown("**Refund status:** UNKNOWN")
                st.markdown("**Refund arrival time:** NOT VERIFIED")

        with st.expander("Technical reference", expanded=False):
            st.markdown(
                "**Control:** `" + summary["case_id"] + "`"
            )
            st.markdown(
                "**Finding:** `" + str(summary["rule_id"]) + "`"
            )
            st.markdown(
                "**Evaluator:** `" + str(summary["evaluator_version"]) + "`"
            )
            st.caption(
                "The displayed finding and outcome come from the "
                "recorded deterministic evaluation. The comparison "
                "does not independently extract or classify claims."
            )

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

elif page == "Payment Workflow Audit":
    st.caption("INTERNAL PAYMENT WORKFLOW / SYNTHETIC DEMONSTRATION")
    st.markdown("## Payment Workflow Audit")
    st.markdown(
        "### Automation reduces manual workload. "
        "But who validates the automation?"
    )

    with st.container(border=True):
        st.caption("01 / THE CHALLENGE")
        st.write(
            "Payment incidents can overwhelm support and Payments teams. "
            "Automation helps handle the workload — but its recommendations "
            "still need quality control."
        )
        st.caption("02 / THE AUDIT")
        st.write(
            "Test whether a fictional internal payment workflow recommends "
            "an action supported by the available transaction facts."
        )
        st.caption(
            "OFFLINE SYNTHETIC DEMO · NO PAYMENT EXECUTION"
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
    st.markdown("### 02 / Evaluate a Payment Workflow Recommendation")

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

    decision_key = f"automation_v2_{scenario}"
    if decision_key not in st.session_state:
        st.session_state[decision_key] = json.dumps(initial, indent=2)

    with st.expander("✎ Edit supplied JSON decision", expanded=False):
        raw = st.text_area(
            "Automation output (JSON)",
            height=170,
            key=decision_key,
            label_visibility="collapsed",
        )

    recorded_decision = st.session_state.get("latest_result")
    decision_evaluated = (
        recorded_decision is not None
        and recorded_decision.get("system_type") == "payment_automation"
        and st.session_state.get("automation_evaluated_raw") == raw
    )
    st.caption(
        "SUPPLIED AUTOMATION DECISION / "
        + ("EVALUATED" if decision_evaluated else "NOT YET EVALUATED")
    )

    try:
        preview = json.loads(raw)
    except json.JSONDecodeError:
        st.warning("Invalid JSON — edit the supplied decision before auditing.")
    else:
        if not isinstance(preview, dict):
            st.warning("The supplied decision must be a JSON object.")
        else:
            with st.container(border=True):
                left, right = st.columns(2, gap="medium")
                with left:
                    st.caption("REFUND STATUS")
                    st.markdown(
                        "**" + str(preview.get("refund_status", "NOT SUPPLIED")) + "**"
                    )
                with right:
                    st.caption("RECOMMENDED ACTION")
                    st.markdown(
                        "**" + str(preview.get("recommended_action", "NOT SUPPLIED")) + "**"
                    )
                extra_fields = {
                    key: value for key, value in preview.items()
                    if key not in {"refund_status", "recommended_action"}
                }
                if extra_fields:
                    with st.expander("Additional supplied decision fields"):
                        st.json(extra_fields)
            st.caption(
                "Preview of supplied JSON only. No payment action has been "
                "executed."
                + (
                    " The matching recorded audit appears below."
                    if decision_evaluated
                    else " Run the audit to establish a control outcome."
                )
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
        summary = automation_audit_summary(current)

        st.caption("AUDIT OUTCOME / RECORDED DETERMINISTIC EVALUATION")
        if summary["outcome"] == "FAIL":
            st.error("FAIL — " + summary["outcome_label"])
        elif summary["outcome"] == "PASS":
            st.success("PASS — " + summary["outcome_label"])
        else:
            st.warning("REVIEW — " + summary["outcome_label"])

        st.markdown("#### " + summary["title"])
        st.write(summary["reason"])

        with st.container(border=True):
            st.caption("BUSINESS INTERPRETATION / WHY THIS MATTERS")

            if summary["outcome"] == "FAIL":
                st.markdown(
                    "**The workflow recommends an action that the "
                    "available evidence does not justify.**"
                )
                st.write(
                    "In this synthetic case, the supplied automation "
                    "output treats an unverified refund as approved and "
                    "recommends confirming it. The independent audit "
                    "flags this unsupported recommendation, making the "
                    "issue visible before the workflow is relied upon."
                )
                st.caption(
                    "This is a detected test failure, not a blocked "
                    "production payment or an actual refund event."
                )
            elif summary["outcome"] == "PASS":
                st.markdown(
                    "**The supplied recommendation satisfies the "
                    "implemented control for this test case.**"
                )
                st.write(
                    "The workflow does not claim a refund outcome "
                    "that the available synthetic facts cannot confirm. "
                    "This demonstrates a successful local control check, "
                    "not end-to-end automation safety."
                )
            else:
                st.markdown(
                    "**The supplied output needs further assessment.**"
                )
                st.write(
                    "The implemented control has not established a "
                    "definitive PASS or FAIL for this supplied output. "
                    "Do not interpret REVIEW as an approval."
                )

        st.markdown("#### Evidence comparison")
        decision_col, facts_col = st.columns(2, gap="medium")

        with decision_col:
            with st.container(border=True):
                st.caption("RECORDED AUTOMATION OUTPUT")
                st.json(summary["output"], expanded=True)

        with facts_col:
            with st.container(border=True):
                st.caption("VERIFIED SYNTHETIC TRANSACTION FACTS")
                st.markdown("**Deposit status:** FAILED")
                st.markdown("**Refund status:** UNKNOWN")
                st.markdown("**Verified refund arrival time:** Not supplied")
                st.caption(
                    "The supplied transaction data does not establish "
                    "refund approval or completion."
                )

        with st.expander("Technical reference"):
            st.write(f"**Case:** `{summary['case_id']}`")
            st.write(f"**Rule:** `{summary['rule_id']}`")
            st.write(f"**Evaluator:** `{summary['evaluator_version']}`")
            st.write(f"**Run ID:** `{summary['run_id']}`")
            if summary["checks"]:
                st.markdown("**Defined checks**")
                st.json(summary["checks"], expanded=False)

        st.caption(
            "Offline synthetic assessment. A control PASS does not "
            "establish production reliability."
        )
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

elif page == "System X-Ray":
    st.markdown("## System X-Ray")
    st.write(
        "Review bundled synthetic examples and session audit evidence. "
        "Inspect recorded findings, evaluated outputs and observable "
        "evaluation-software events."
    )

    inspectable_records = records + bundled_examples
    if not inspectable_records:
        st.info("No synthetic audit evidence available.")
    else:
        labels = {
            r["run_id"]: (
                f"{r['evaluation']['result']}  /  "
                f"{r['system_type']}  /  {r['run_id']}  /  "
                f"{r.get('evidence_origin', 'recorded_run')}"
            )
            for r in inspectable_records
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
            r for r in inspectable_records if r["run_id"] == selected
        )
        show_evidence(selected_record)
