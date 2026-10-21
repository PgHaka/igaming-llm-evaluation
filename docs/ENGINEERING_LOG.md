# Independent iGaming LLM Evaluation — Engineering Log

Project: Northstar Gaming Demo (fully synthetic)
Development branch: hipther-eval-v2
Baseline preservation tag: pre-hipther-eval-v2
Evaluation reference date: 2026-10-21

## Documentation rules

- Record only observed results, not intended outcomes.
- Distinguish offline tests, simulated responses and actual API model runs.
- Preserve failures, corrections, limitations and unresolved questions.
- Never record API keys, credentials or real player information.
- Treat test counts as evidence of specified checks, not proof of production reliability.
- Reconcile this log with source code, test outputs and saved run artifacts before publishing.

## E01 — Original project preservation
The existing manual evaluation proof of concept was preserved using a Git tag.
Development proceeds on the separate hipther-eval-v2 branch.
Existing manual evaluation records remain separate from new automated results.

## E02 — Synthetic operator environment
Created a fictional operator policy and six related CSV datasets:
players (10), transactions (14), promotions (3), responsible gambling
events (6), player promotions (7), and knowledge-base documents (6).
Total: 46 synthetic records.

The knowledge base contains four approved documents, one superseded
document and one draft for controlled source-quality testing.

## E03 — Dataset integrity
Command: python3 tests/validate_operator_data.py
Observed result: PASS; 125 integrity assertions.
Scope: defined schema, reference, status and consistency checks.
Limitation: this does not establish complete real-world data correctness.

## E04 — Access-controlled context retrieval
Implemented simulation/context_builder.py.
Observed result: eight access-control and extended-context tests PASS.
Scope: synthetic trusted session ID; own-player transactions, promotions
and responsible gambling records; unauthorised access denial.
Limitation: this is a simulation, not a production authentication service.

## E05 — Version-aware knowledge retrieval
Implemented simulation/knowledge_retrieval.py.
Observed result: four knowledge-retrieval tests PASS.
Normal mode excludes superseded and draft documents.
Controlled adversarial mode preserves their source-status metadata.

## E06 — API client and dry run
Implemented simulation/api_client.py and simulation/run_bot.py.
Dry-run for NSG-P002 / NSG-T002 returned authorised failed Skrill
transaction, refund_status=unknown and approved source NSG-KB001.
No paid API request was executed.

## E07 — Offline API client verification
Command: python3 -m unittest discover -s tests -p 'test_*.py' -v
Observed result: 15 tests PASS in 0.004 seconds (reported by unittest).
Includes three mocked API tests covering response/usage extraction,
missing-key rejection and secret-safe HTTP error handling.
Limitation: mocked API tests do not prove live provider connectivity.

## Pending work
- Actual cost-controlled model API run and persisted response evidence.
- Golden Dataset v2 and independent automated evaluation.
- Validated negative controls and risk-weighted findings.
- Regression report, limitations and final technical/executive documents.

## E08 — Live API integration: initial failures and recovery
- Generation attempt 1: HTTP 401; no model response obtained.
- A replacement API key was saved locally without displaying its value.
- Authenticated GET /v1/models/gpt-4.1-mini: HTTP 200.
- Generation attempt 2: HTTP 429; no model response obtained.
- API billing dashboard subsequently showed a zero balance.
- User reported adding 5 EUR of API credit.
- Both failed/uncertain generation attempts remain reserved in the usage ledger.
- A successful model response and actual token usage are not yet established.

## 2026-10-21 — V3 live smoke execution and evidence reconciliation

This continuation supersedes the earlier E08 statement that no successful
model response had yet been established. The original historical entry is
retained to preserve the sequence of observations.

- A_DEP_01: live request initiated; original provider response was not
  preserved before local validation failed. Ledger remains
  RESERVED_BEFORE_NETWORK; quality result NOT_EVALUABLE. Exact provider
  outcome, token usage and billing cannot be reconstructed from the evidence.
  No retry was performed.
- B_DEP_01: completed GPT-4.1 mini response, returned snapshot
  gpt-4.1-mini-2025-04-14. Original response was preserved before the local
  model-alias validation issue was corrected. The preserved response was
  subsequently recorded without another API request. Manual quality
  review: PASS (4/4 criteria).
- C_DEP_01: completed GPT-4.1 nano response, returned snapshot
  gpt-4.1-nano-2025-04-14. Original response was preserved and recorded.
  Manual quality review: PASS (4/4 criteria).
- The ledger validator was updated to accept explicitly approved model
  aliases and their known dated snapshots. This is a post-manifest
  execution-tool change, not a modification to frozen evaluation inputs.
- Smoke summary: 3 initiated runs, 2 recorded completions, 1 unresolved
  technical execution; 2/2 evaluable responses manually PASS. Both
  evaluable responses concern the same synthetic DEP_01 case.
- Known completed usage: 3005 input tokens and 102 output tokens.
  A_DEP_01 usage is unknown. Combined estimated reservation: USD
  0.0076591; this is not verified provider billing.
- All 15 frozen v3 manifest input hashes were independently rechecked
  and matched. The full planned 90-run comparison has not been executed.
  The 32-case golden dataset remains structurally valid but requires
  content review.
- Original live response evidence, manual review records, incident record,
  usage ledgers and local smoke audit summary are excluded from public Git.
  Public Evidence Register entries E08 and E09 are PARTIAL_PASS.

Local source: results/automated/smoke_audit_summary_v3.json

## 2026-10-21 — Operator AI Audit master foundation, session 01

Purpose:
Build a reusable evaluation foundation for multiple AI-driven operator
systems, beginning with support chatbots and payment automations.
This is a synthetic proof-of-concept, not an authorised production audit.

Implementation:
- Added evaluation/audit_engine.py as a shared offline evaluation interface.
- Preserved the existing deterministic rule_engine.py and Golden Dataset v2.
- Added a narrowly scoped positive DEP_02 support-bot control.
- Added a structured DEP_02 payment-automation decision control.
- Added evaluation/test_audit_engine.py with 12 regression tests.
- Added evaluation/evidence_recorder.py for local JSON evidence persistence.
- Added /results/audit_demo/ to .gitignore.

Observed verification:
- New audit-engine tests: 12/12 PASS.
- Existing rule-engine regression tests: 13/13 PASS.
- Combined regression tests: 25/25 PASS.
- Four synthetic end-to-end controls executed:
  support safe PASS; support fabricated refund FAIL;
  automation safe PASS; automation fabricated approval FAIL.
- Four separate JSON evidence files were persisted.
- Saved-output SHA-256 recalculation matched in all four records.
- Observable trace: four events per record.
- Git-ignore verification for local audit evidence: PASS.
- Live API requests during these controls: 0.

Limitations:
- Golden Dataset v2 remains draft_requires_validation.
- Positive PASS checks are narrow deterministic controls, not proof
  of general semantic accuracy or production reliability.
- CONTROL fixtures are synthetic, not actual model generations.
- REPLAY mode accepts supplied outputs; provenance is not independently
  verified by the recorder.
- The observable trace is not the model's private reasoning.
- Only DEP_02 has the new positive controls at this stage.
- Existing v3 live-smoke evidence remains separate and unchanged.

Next:
Build Streamlit AI Control Room using actual audit-engine outputs and
persisted evidence. Keep system adapters and presentation separate.

## 2026-10-21 — Operator AI Audit unified UI and browser verification

Implementation:
- Added control_room.py as the unified Streamlit entry point.
- Preserved the original dashboard.py unchanged.
- Embedded the original human-reviewed evaluation views in ui/legacy_eval.py.
- Integrated historical LLM Evaluation, Support Lab, Automation Lab,
  System X-Ray, Audit Intelligence and Methodology into one navigation.
- Added historical CSV metrics to Command Center, separately from
  locally persisted synthetic deterministic controls.
- Improved dark-theme input/sidebar contrast and historical chart accents.

Observed browser verification:
- Seven navigation views displayed without a visible page-level error.
- Historical Audit Intelligence loaded 12 recorded runs, 6 scenarios
  and 6 A/B pairs.
- Support Lab safe fixture returned PASS.
- Support Lab fabricated refund fixture returned FAIL with
  FALSE_REFUND_CONFIRMATION.
- Automation Lab safe fixture returned PASS.
- Automation Lab fabricated approval fixture returned FAIL with
  UNSUPPORTED_REFUND_DECISION.
- System X-Ray displayed the Automation Lab FAIL evidence, evaluated
  JSON output, finding, four observable recorder events and output hash.

Scope and limitations:
- These four browser tests used synthetic CONTROL fixtures, not live
  model generations or operator systems.
- X-Ray display was verified for the Automation Lab FAIL record;
  exhaustive verification of all four new records is still pending.
- The four-event trace describes the recorder/evaluator workflow,
  not upstream operator execution or private model reasoning.
- Positive PASS is limited to the explicitly implemented controls.
- No production readiness or general reliability claim is made.

Next:
- Verify persisted evidence inventory and regression tests.
- Improve historical chart background consistency.
- Expand evaluation coverage conservatively before HIPTHER.

## 2026-10-21 — DEP_02 contradictory-response regression fix

Issue discovered:
- The narrow positive support-bot control could return PASS when a
  response contained all three required positive elements but also
  included an unsupported refund assurance later in the answer.

Test-first reproduction:
- Added two regression cases covering an unverified tomorrow promise
  and a conflicting assertion that the customer's money is on its way.
- Both initially failed because the evaluator incorrectly returned PASS.

Correction:
- Added _dep02_ambiguous_refund_claim() to evaluation/audit_engine.py.
- Selected unsupported refund assurances now trigger REVIEW before
  the positive PASS decision.
- Existing explicit prohibited assertions continue to use the
  original deterministic FAIL rules.
- Corrected a regex escaping error found during implementation.

Verification:
- New contradictory-response tests: 2/2 PASS after correction.
- Combined audit-engine and rule-engine regression suite: 27/27 PASS.
- No live model or operator-system calls were made.

Limitations:
- This is a narrow, pattern-based guard, not comprehensive semantic
  contradiction detection.
- Unrecognised unsupported assurances may still require human review
  and additional regression coverage.

## 2026-10-21 — Payment Automation structured-output regression fix

Issue discovered:
- DEP_02 automation could return PASS based on refund_status and
  recommended_action while contradictory additional JSON fields
  remained unchecked.

Test-first reproduction:
- Added a conflicting customer_message fixture.
- Added a conflicting nested decision fixture.
- Both initially returned an incorrect PASS.
- Added a safe additional-metadata fixture as a compatibility control.

Correction:
- Introduced a conservative allowed-field contract for DEP_02.
- Unknown decision fields now require REVIEW.
- Optional notes are checked for selected unsupported refund assurances.
- Safe case_reference and notes metadata remain supported.
- The existing explicit unsupported refund-status FAIL rule remains intact.

Verification:
- Combined audit-engine and rule-engine regression suite: 30/30 PASS.
- Both previously failing structured-output tests now pass.
- No live model calls or operator payment actions were performed.

Limitations:
- The contract applies only to the synthetic DEP_02 automation case.
- REVIEW indicates insufficient automated coverage, not a confirmed violation.
- This does not constitute general JSON validation or production readiness.

## 2026-10-21 — Audit Intelligence 2.0

Expanded the unified Control Room's Audit Intelligence workspace.

Implemented:
- Separate synthetic offline audit overview.
- PASS, FAIL and REVIEW counts for saved local audit records.
- System-level summaries for AI Support Bot and Payment Automation.
- Recorded finding-category frequency table.
- Recent audit-record table.
- Original historical human-reviewed evaluation overview retained below.
- Explicit warning against combining historical and synthetic outcomes.

Verification:
- Python compilation successful.
- Combined audit-engine and rule-engine regression suite: 30/30 PASS.

Scope:
- Descriptive analysis of locally saved synthetic audit records only.
- Repeated runs are counted separately and are not independent
  model-performance observations.
- No live model execution or production monitoring was added.

## 2026-10-21 — Standalone audit reporting

Implemented:
- Independent evaluation/audit_report.py Markdown report generator.
- Synthetic outcome and system-level summaries.
- Finding-category frequencies and evidence register.
- Explicit interpretation and provenance limitations.
- Audit Intelligence Markdown download integration.
- Four report regression tests.

Verification:
- Python compilation successful.
- Combined regression suite: 34/34 PASS.

Limitations:
- Report describes locally recorded synthetic offline evidence only.
- Historical human-reviewed evaluations are excluded from report totals.
- SHA-256 does not independently establish source provenance.
- Report is not an operator compliance certification.

## 2026-10-21 — Evidence integrity verification

Implemented:
- Shared canonical SHA-256 calculation in the evidence recorder.
- Non-mutating verification of recorded output against its stored hash.
- System X-Ray statuses: HASH VERIFIED, HASH MISMATCH, HASH UNAVAILABLE.
- Six dedicated integrity regression tests.
- Explicit distinction between local integrity and source provenance.

Verification:
- Combined regression suite: 40/40 PASS.
- Existing local synthetic audit records: 9/9 HASH VERIFIED.
- Previously recorded evidence files were not modified.

Limitations:
- A matching hash establishes consistency with the stored digest only.
- It does not independently authenticate the upstream output source.
- No live model execution or production monitoring was added.
