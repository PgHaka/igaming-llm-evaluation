# iGaming LLM Evaluation Framework

### Independent Proof of Concept | AI Quality Assurance

A Python-based evaluation framework designed to explore how AI customer support assistants handle iGaming-specific operational scenarios, payment-related questions, verification requirements and adversarial customer requests.

The project combines practical iGaming operational knowledge with structured LLM evaluation methods.

**Project status:** Working proof of concept. Further development ongoing.

---

## 1. Project Objective

The long-term objective is to develop a reusable evaluation framework that helps iGaming operators systematically assess AI customer support assistants against their own operational policies, verified transaction information and risk criteria.

The framework is intended to support evidence-based confidence in AI behaviour through repeatable testing, structured evaluation and transparent reporting.

This is an independent portfolio project, not a production deployment.

## 2. Current Implementation

The current proof of concept includes:

- Synthetic iGaming customer support scenarios.
- Separate model inputs and evaluation ground truth.
- Repeatable prompt generation using Python.
- Two prompt configurations (A and B).
- Manual model execution and verbatim response recording.
- Human-reviewed evaluation outcomes.
- Structured CSV result logging.
- Automated evaluation reporting.
- An interactive Streamlit dashboard.
- Scenario-level inspection of expected and actual behaviour.

### Initial Evaluation Results

| Metric | Recorded result |
|---|---:|
| Unique evaluated scenarios | 6 |
| Recorded evaluation runs | 12 |
| Matched A/B test pairs | 6 |
| PASS | 12 |
| FAIL | 0 |
| NEEDS REVIEW | 0 |
| Observed pass rate | 100% |

Both prompt configurations passed the selected scenarios.

No measurable improvement between Prompt A and Prompt B was observed in this limited test set.

The results describe only the recorded, manually reviewed evaluations. They do not establish general model reliability or production readiness.

## 3. Evaluation Coverage

The initial test set covers selected scenarios involving:

- Failed deposits and unsupported refund confirmations.
- Identity verification requirements.
- Third-party withdrawal restrictions.
- Confidentiality of player and payment information.
- Unsupported customer claims.
- Prompt injection and authority-spoofing attempts.

Evaluation criteria include expected behaviour, forbidden claims, failure categories and severity classifications.

## 4. Evaluation Workflow

1. Prepare synthetic customer scenarios and verified demo information.
2. Define expected behaviour and forbidden claims separately from model inputs.
3. Generate repeatable prompts for the selected scenario.
4. Submit the prompts to the model manually.
5. Record the model response verbatim.
6. Review the response against predefined evaluation criteria.
7. Store the evaluation result in CSV format.
8. Generate automated summaries and inspect results in the dashboard.

The current implementation uses human evaluation. It does not automatically execute model API calls or perform automated LLM-as-a-judge scoring.

## 5. Project Structure

```text
igaming_llm_eval/
|
|-- dashboard.py
|-- generate_blind_test.py
|-- generate_prompt_b_tests.py
|-- record_test_run.py
|-- generate_eval_report.py
|-- prompt_b.txt
|-- data/
|   |-- model_inputs.csv
|   |-- evaluation_ground_truth.csv
|-- results/
|   |-- test_runs.csv
|-- reports/
|   |-- evaluation_report.md
|   |-- evaluation_detail.csv
|   |-- category_summary.csv
|   |-- prompt_summary.csv
|   |-- severity_summary.csv
|-- prompts/
|-- README.md
```

Additional scripts used during dataset preparation are retained in the project directory.

## 6. Running the Dashboard

From the project directory:

```bash
source .venv/bin/activate
streamlit run dashboard.py
```

Open the local address displayed in the terminal, normally:

http://localhost:8501

The dashboard reads the existing CSV files and displays:

- Recorded evaluation metrics.
- Prompt A/B comparison.
- Scenario coverage.
- Individual test cases.
- Expected behaviour and forbidden claims.
- Recorded model responses.
- Human evaluation notes.
- Project methodology and limitations.

To regenerate the evaluation reports:

```bash
python generate_eval_report.py
```

## 7. Development Roadmap

The next development stages are:

### Expanded Golden Dataset
Build a larger and more representative set of scenarios, including operator-specific policies, edge cases and risk classifications.

### Automated Evaluation
Introduce repeatable model execution, programmatic checks and appropriate automated evaluation methods.

### Regression Testing
Compare system behaviour across model, prompt and policy changes.

### Operational Readiness
Explore integration requirements, access controls, logging, monitoring and deployment considerations.

These items are planned development work, not features claimed to be implemented in the current proof of concept.

## 8. Limitations

- All scenarios use synthetic or fictional demo information.
- No live operator accounts or real customer payment data are used.
- The evaluation dataset is small and deliberately selected.
- Model responses were collected manually.
- Evaluation outcomes were reviewed by a human.
- The observed pass rate is not a production safety guarantee.
- No production integration or live monitoring has been implemented.

---

**Independent iGaming Data & AI Portfolio Project**

*Combining operational domain knowledge, Python automation and AI quality assurance.*
