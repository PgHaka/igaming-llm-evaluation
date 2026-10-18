from pathlib import Path
from datetime import datetime
import pandas as pd

BASE = Path(__file__).resolve().parent

RESULTS_FILE = BASE / "results" / "test_runs.csv"
MODEL_INPUTS_FILE = BASE / "data" / "model_inputs.csv"
REPORT_DIR = BASE / "reports"

REPORT_DIR.mkdir(exist_ok=True)

runs = pd.read_csv(
    RESULTS_FILE,
    dtype=str,
    keep_default_na=False
)

cases = pd.read_csv(
    MODEL_INPUTS_FILE,
    dtype=str,
    keep_default_na=False
)

if runs.empty:
    raise SystemExit("No recorded test runs found.")

required = [
    "run_id",
    "test_id",
    "prompt_version",
    "evaluation_result",
    "severity",
    "failure_category"
]

missing = [c for c in required if c not in runs.columns]

if missing:
    raise ValueError(f"Missing result columns: {missing}")

# Add test category from the test library.
runs = runs.merge(
    cases[["test_id", "category"]],
    on="test_id",
    how="left",
    validate="many_to_one"
)

runs["category"] = runs["category"].fillna("Unknown")

# Normalize evaluation labels.
runs["evaluation_result"] = (
    runs["evaluation_result"].str.strip().str.upper()
)

runs["severity"] = runs["severity"].str.strip().str.upper()

total = len(runs)
passed = (runs["evaluation_result"] == "PASS").sum()
failed = (runs["evaluation_result"] == "FAIL").sum()
review = (runs["evaluation_result"] == "NEEDS REVIEW").sum()

pass_rate = passed / total * 100

# Summary by category.
category_summary = pd.crosstab(
    runs["category"],
    runs["evaluation_result"]
)

category_summary["TOTAL"] = category_summary.sum(axis=1)

# Summary by prompt version.
prompt_summary = pd.crosstab(
    runs["prompt_version"],
    runs["evaluation_result"]
)

prompt_summary["TOTAL"] = prompt_summary.sum(axis=1)

# Severity distribution.
severity_summary = (
    runs["severity"]
    .value_counts()
    .rename_axis("severity")
    .reset_index(name="count")
)

# Save analysis files.
runs.to_csv(
    REPORT_DIR / "evaluation_detail.csv",
    index=False,
    encoding="utf-8-sig"
)

category_summary.to_csv(
    REPORT_DIR / "category_summary.csv",
    encoding="utf-8-sig"
)

prompt_summary.to_csv(
    REPORT_DIR / "prompt_summary.csv",
    encoding="utf-8-sig"
)

severity_summary.to_csv(
    REPORT_DIR / "severity_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

# Build a readable Markdown report.
lines = [
    "# iGaming LLM Evaluation Report",
    "",
    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    "",
    "## Project scope",
    "",
    "Python-assisted evaluation using synthetic iGaming transaction data.",
    "Prompts are generated programmatically, model responses are obtained",
    "manually, and results are assessed through human review.",
    "",
    "## Overall results",
    "",
    f"- Recorded test runs: {total}",
    f"- PASS: {passed}",
    f"- FAIL: {failed}",
    f"- NEEDS REVIEW: {review}",
    f"- Observed pass rate: {pass_rate:.1f}%",
    "",
    "The observed pass rate describes only the recorded test runs.",
    "It is not a statistically validated estimate of model reliability.",
    "",
    "## Results by category",
    "",
    "```\n" + category_summary.to_string() + "\n```",
    "",
    "## Results by prompt version",
    "",
    "```\n" + prompt_summary.to_string() + "\n```",
    "",
    "## Severity distribution",
    "",
    "```\n" + severity_summary.to_string(index=False) + "\n```",
    "",
    "## Individual test runs",
    "",
    "```",
    runs[
        [
            "run_id",
            "category",
            "prompt_version",
            "evaluation_result",
            "severity",
            "failure_category"
        ]
    ].to_string(index=False) + "\n```",
    "",
    "## Methodology and limitations",
    "",
    "- Synthetic demonstration dataset; no real player data.",
    "- Case-specific evaluation criteria are separated from model inputs.",
    "- LLM execution is manual, not automated through an API.",
    "- Evaluation decisions are human-reviewed.",
    "- Small test samples do not establish production reliability.",
    "- Secondary Gemini observations are documented separately",
    "  only when materially significant differences are identified.",
    "",
]

report_path = REPORT_DIR / "evaluation_report.md"

report_path.write_text(
    "\n".join(lines),
    encoding="utf-8"
)

print("\n========================================")
print("IGAMING LLM EVALUATION REPORT")
print("========================================")
print(f"Recorded runs: {total}")
print(f"PASS: {passed}")
print(f"FAIL: {failed}")
print(f"NEEDS REVIEW: {review}")
print(f"Observed pass rate: {pass_rate:.1f}%")

print("\nRESULTS BY CATEGORY")
print(category_summary.to_string())

print("\nREPORT GENERATED SUCCESSFULLY")
print(f"Markdown report: {report_path}")
print(f"CSV summaries: {REPORT_DIR}")
