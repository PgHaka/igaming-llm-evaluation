from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="iGaming AI | Evaluation Lab",
    page_icon="🧪",
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
    background: #111C2E;
}
[data-testid="stMetric"] {
    background: #17253A;
    border: 1px solid #263A55;
    border-radius: 12px;
    padding: 18px;
}
[data-testid="stMetricLabel"] {
    color: #A8BED4;
}
h1, h2, h3 {
    color: #F1F5F9 !important;
}
div[data-testid="stExpander"] {
    border: 1px solid #263A55;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
[data-testid="stMetricValue"] {
    color: #F8FAFC !important;
}
[data-testid="stMetricLabel"] {
    color: #CBD5E1 !important;
}
[data-testid="stSidebar"] * {
    color: #E2E8F0;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
    color: #94A3B8 !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label {
    color: #E2E8F0 !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    runs = pd.read_csv(ROOT / "results/test_runs.csv", encoding="utf-8-sig")
    inputs = pd.read_csv(ROOT / "data/model_inputs.csv", encoding="utf-8-sig")
    truth = pd.read_csv(ROOT / "data/evaluation_ground_truth.csv", encoding="utf-8-sig")

    for df in (runs, inputs, truth):
        df.columns = df.columns.str.strip()
        df["test_id"] = df["test_id"].astype(str).str.strip()

    runs["prompt_version"] = runs["prompt_version"].astype(str).str.strip().str.upper()
    runs["evaluation_result"] = runs["evaluation_result"].astype(str).str.strip().str.upper()

    detail = runs.merge(
        inputs, on="test_id", how="left", validate="many_to_one"
    ).merge(
        truth, on="test_id", how="left", validate="many_to_one",
        suffixes=("", "_ground_truth")
    )

    return runs, inputs, truth, detail


def show_value(value):
    if pd.isna(value) or str(value).strip() == "":
        return "Not specified"
    return str(value)


def show_response(row):
    if row is None:
        st.info("No recorded response for this prompt version.")
        return

    result = show_value(row["evaluation_result"])
    if result == "PASS":
        st.success("PASS")
    elif result == "FAIL":
        st.error("FAIL")
    else:
        st.warning(result)

    st.caption(
        f"Run: {show_value(row['run_id'])} · "
        f"Method: {show_value(row['test_method'])}"
    )
    st.markdown("**Model response**")
    st.text_area(
        "Recorded model response",
        value=show_value(row["model_response"]),
        height=290,
        disabled=True,
        key=f"response_{row['run_id']}",
        label_visibility="collapsed",
    )
    st.markdown("**Human evaluation**")
    st.write(show_value(row["evaluation_notes"]))
    st.caption(
        f"Severity: {show_value(row['severity'])} · "
        f"Failure category: {show_value(row['failure_category'])} · "
        f"Evaluator: {show_value(row['evaluator'])}"
    )


try:
    runs, inputs, truth, detail = load_data()
except (FileNotFoundError, ValueError, KeyError) as exc:
    st.error(f"Could not load the evaluation dataset: {exc}")
    st.stop()

st.sidebar.markdown("## ◈ iGaming AI")
st.sidebar.caption("INDEPENDENT EVALUATION LAB")
page = st.sidebar.radio(
    "Navigation",
    ["Overview", "Test Explorer", "Methodology"],
)
st.sidebar.divider()
st.sidebar.caption("Independent proof of concept")
st.sidebar.caption("Synthetic scenarios · Human-reviewed results")

total = len(runs)
passed = int((runs["evaluation_result"] == "PASS").sum())
failed = int((runs["evaluation_result"] == "FAIL").sum())
review = int((runs["evaluation_result"] == "NEEDS REVIEW").sum())
unique_tests = runs["test_id"].nunique()
observed_rate = 100 * passed / total if total else 0

versions_by_test = runs.groupby("test_id")["prompt_version"].agg(set)
paired_ids = [
    test_id for test_id, versions in versions_by_test.items()
    if {"A", "B"}.issubset(versions)
]

if page == "Overview":
    st.caption("INDEPENDENT PROOF OF CONCEPT / AI QUALITY ASSURANCE")
    st.title("LLM Evaluation Framework")
    st.write(
        "A reproducible, human-reviewed evaluation workflow for "
        "iGaming customer support scenarios."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Recorded runs", total)
    c2.metric("Unique scenarios", unique_tests)
    c3.metric("A/B pairs", len(paired_ids))
    c4.metric("Pass rate", f"{observed_rate:.0f}%")

    st.caption(
        "Pass rate describes only the recorded, manually reviewed runs. "
        "It is not a production safety or general model reliability estimate."
    )

    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("Prompt comparison")
        comparison = pd.crosstab(
            runs["prompt_version"], runs["evaluation_result"]
        ).reindex(index=["A", "B"], fill_value=0)
        st.bar_chart(comparison, stack=True)
        st.dataframe(comparison, use_container_width=True)

    with right:
        st.subheader("Scenario coverage")
        coverage = (
            detail.groupby("category", dropna=False)
            .size()
            .rename("Recorded runs")
            .sort_values(ascending=False)
        )
        st.bar_chart(coverage)
        st.dataframe(coverage, use_container_width=True)

    st.divider()
    st.subheader("Recorded outcomes")
    a, b, c = st.columns(3)
    a.metric("PASS", passed)
    b.metric("FAIL", failed)
    c.metric("NEEDS REVIEW", review)

    st.subheader("Run register")
    register_columns = [
        "run_id", "test_id", "category", "prompt_version",
        "evaluation_result", "severity", "failure_category"
    ]
    st.dataframe(
        detail[register_columns],
        hide_index=True,
        use_container_width=True,
    )

elif page == "Test Explorer":
    st.caption("EVIDENCE / SCENARIO REVIEW")
    st.title("Test Explorer")
    st.write(
        "Inspect the customer scenario, expected behaviour and actual "
        "recorded responses for both prompt versions."
    )

    categories = sorted(inputs["category"].dropna().astype(str).unique())
    category = st.selectbox("Scenario category", ["All"] + categories)

    available = inputs.copy()
    if category != "All":
        available = available[available["category"] == category]

    selected_id = st.selectbox(
        "Select test case",
        sorted(available["test_id"].unique()),
    )

    input_row = inputs.loc[inputs["test_id"] == selected_id].iloc[0]
    truth_rows = truth.loc[truth["test_id"] == selected_id]
    selected_runs = runs.loc[runs["test_id"] == selected_id]

    st.subheader(f"Scenario: {selected_id}")
    st.caption(f"Category: {show_value(input_row['category'])}")

    st.markdown("#### Customer message")
    st.info(show_value(input_row["customer_message"]))

    with st.expander("Verified scenario information", expanded=True):
        fields = [
            ("Transaction ID", "transaction_id"),
            ("Status", "transaction_status"),
            ("Payment method", "payment_method"),
            ("Amount", "amount"),
            ("Country", "country"),
        ]
        for label, field in fields:
            st.write(f"**{label}:** {show_value(input_row[field])}")

    with st.expander("Evaluation criteria", expanded=True):
        if truth_rows.empty:
            st.warning("No matching ground-truth record found.")
        else:
            expected = truth_rows.iloc[0]
            st.markdown("**Expected behaviour**")
            st.write(show_value(expected["expected_behavior"]))
            st.markdown("**Forbidden claims**")
            st.write(show_value(expected["forbidden_claims"]))
            st.caption(
                f"Failure category: {show_value(expected['failure_category'])} · "
                f"Severity if failed: {show_value(expected['severity_if_failed'])}"
            )

    st.divider()
    st.subheader("Prompt A vs Prompt B")

    left, right = st.columns(2)
    for column, version in [(left, "A"), (right, "B")]:
        with column:
            st.markdown(f"### Prompt {version}")
            matches = selected_runs.loc[
                selected_runs["prompt_version"] == version
            ]
            if matches.empty:
                show_response(None)
            else:
                if len(matches) > 1:
                    run_id = st.selectbox(
                        "Recorded run",
                        matches["run_id"].tolist(),
                        key=f"select_{version}",
                    )
                    row = matches.loc[
                        matches["run_id"] == run_id
                    ].iloc[0]
                else:
                    row = matches.iloc[0]
                show_response(row)

elif page == "Methodology":
    st.caption("PROJECT DOCUMENTATION")
    st.title("Evaluation Methodology")

    st.markdown("""
### Purpose

Explore how an AI customer support assistant responds to selected
iGaming payment, verification, withdrawal and adversarial scenarios.

### Workflow

1. Prepare synthetic customer scenarios and verified demo information.
2. Define expected behaviour and forbidden claims separately.
3. Generate repeatable prompts for Prompt A and Prompt B.
4. Submit prompts manually to the model.
5. Record model responses verbatim.
6. Review responses against the defined evaluation criteria.
7. Save the results to CSV and generate reproducible summaries.

### Evaluation approach

- Human-reviewed PASS / FAIL / NEEDS REVIEW outcomes.
- Prompt A and B use matched scenarios.
- Customer statements are not treated as verified transaction evidence.
- Adversarial scenarios include unsupported claims, privacy requests
  and attempts to override the assistant's instructions.

### Limitations

- This is an independent proof of concept using synthetic scenarios.
- The current evaluation set is small and deliberately selected.
- Results are manually reviewed, not produced by an automated judge.
- The observed pass rate cannot establish production readiness.
- No live operator account or customer payment information was used.
- Matching A/B outcomes do not demonstrate an improvement from Prompt B.

### Current interpretation

Both prompt versions passed the recorded scenarios. No measurable
difference was observed in this limited test set. A larger, more
diverse golden dataset and repeated runs would be required before
drawing broader conclusions.
""")

    st.divider()
    st.subheader("Source files")
    st.code(
        "data/model_inputs.csv\n"
        "data/evaluation_ground_truth.csv\n"
        "results/test_runs.csv\n"
        "reports/evaluation_report.md",
        language="text",
    )

st.divider()
st.caption(
    "iGaming AI Evaluation Lab · Independent portfolio project · "
    "Synthetic data · Not a production deployment"
)
