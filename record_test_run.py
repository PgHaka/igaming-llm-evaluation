
import csv
from pathlib import Path

BASE_DIR = Path.home() / "igaming_llm_eval"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = RESULTS_DIR / "test_runs.csv"

FIELDS = [
    "run_id",
    "test_id",
    "prompt_version",
    "test_method",
    "model_response",
    "evaluation_result",
    "severity",
    "failure_category",
    "evaluator",
    "evaluation_notes",
]

print("\nRECORD NEW TEST RUN\n")

run = {}

run["run_id"] = input("Run ID: ").strip().upper()
run["test_id"] = input("Test ID: ").strip().upper()
run["prompt_version"] = input("Prompt version (A/B): ").strip().upper()
run["test_method"] = input("Test method: ").strip()

print("\nPaste the model response.")
print("When finished, type END on a new line.\n")

response_lines = []

while True:
    line = input()

    if line.strip() == "END":
        break

    response_lines.append(line)

run["model_response"] = "\n".join(response_lines)

run["evaluation_result"] = input(
    "\nEvaluation result (PASS/FAIL/NEEDS REVIEW): "
).strip().upper()

run["severity"] = input(
    "Severity (NONE/LOW/MEDIUM/HIGH): "
).strip().upper()

run["failure_category"] = input(
    "Failure category: "
).strip()

run["evaluator"] = input(
    "Evaluator: "
).strip()

run["evaluation_notes"] = input(
    "Evaluation notes: "
).strip()

# Prevent accidentally overwriting or duplicating a run ID.
existing_ids = set()

if OUTPUT_FILE.exists():
    with OUTPUT_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        existing_ids = {
            row["run_id"]
            for row in csv.DictReader(f)
        }

if not run["run_id"] or run["run_id"] in existing_ids:
    raise ValueError("Run ID is empty or already exists.")

write_header = not OUTPUT_FILE.exists()

with OUTPUT_FILE.open("a", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)

    if write_header:
        writer.writeheader()

    writer.writerow(run)

print("\nTest run saved successfully.")
print(f"File: {OUTPUT_FILE}")
print(f"Run ID: {run['run_id']}")

