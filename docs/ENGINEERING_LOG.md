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
