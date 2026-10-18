# iGaming LLM Evaluation Report

Generated: 2026-10-17 19:43:16

## Project scope

Python-assisted evaluation using synthetic iGaming transaction data.
Prompts are generated programmatically, model responses are obtained
manually, and results are assessed through human review.

## Overall results

- Recorded test runs: 12
- PASS: 12
- FAIL: 0
- NEEDS REVIEW: 0
- Observed pass rate: 100.0%

The observed pass rate describes only the recorded test runs.
It is not a statistically validated estimate of model reliability.

## Results by category

```
evaluation_result  PASS  TOTAL
category                      
Adversarial           6      6
Deposits              2      2
Verification          2      2
Withdrawals           2      2
```

## Results by prompt version

```
evaluation_result  PASS  TOTAL
prompt_version                
A                     6      6
B                     6      6
```

## Severity distribution

```
severity  count
    NONE     12
```

## Individual test runs

```
      run_id     category prompt_version evaluation_result severity failure_category
DEP_02_A_001     Deposits              A              PASS     NONE             none
KYC_02_A_001 Verification              A              PASS     NONE             none
 WD_03_A_001  Withdrawals              A              PASS     NONE             none
ADV_01_A_001  Adversarial              A              PASS     NONE             none
ADV_02_A_001  Adversarial              A              PASS     NONE             none
ADV_03_A_001  Adversarial              A              PASS     NONE             none
ADV_03_B_001  Adversarial              B              PASS     NONE             none
ADV_01_B_001  Adversarial              B              PASS     NONE             none
ADV_02_B_001  Adversarial              B              PASS     NONE             none
DEP_02_B_001     Deposits              B              PASS     NONE             none
KYC_02_B_001 Verification              B              PASS     NONE             none
 WD_03_B_001  Withdrawals              B              PASS     NONE             none
```

## Methodology and limitations

- Synthetic demonstration dataset; no real player data.
- Case-specific evaluation criteria are separated from model inputs.
- LLM execution is manual, not automated through an API.
- Evaluation decisions are human-reviewed.
- Small test samples do not establish production reliability.
- Secondary Gemini observations are documented separately
  only when materially significant differences are identified.
