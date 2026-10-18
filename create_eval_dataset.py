
import pandas as pd
from pathlib import Path

# Project directories
BASE_DIR = Path.home() / "igaming_llm_eval"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Model inputs: information visible to the tested LLM
model_inputs = [
    {
        "test_id": "DEP_01",
        "category": "Deposits",
        "customer_message": "I made a deposit via Trustly, but the money is not showing in my balance.",
        "transaction_id": "TXN-100003",
        "transaction_status": "completed",
        "payment_method": "Trustly",
        "amount": 108.30,
        "country": "EE",
    },
    {
        "test_id": "DEP_02",
        "category": "Deposits",
        "customer_message": "My bank account was charged, but my deposit failed. What happens to my money?",
        "transaction_id": "TXN-100040",
        "transaction_status": "failed",
        "payment_method": "Skrill",
        "amount": 22.36,
        "country": "DE",
    },
    {
        "test_id": "DEP_03",
        "category": "Deposits",
        "customer_message": "I made a deposit using Trustly, but the money has not appeared in my account. What is happening?",
        "transaction_id": "TXN-100004",
        "transaction_status": "pending",
        "payment_method": "Trustly",
        "amount": 16.16,
        "country": "FI",
    },
]

# Ground truth: evaluation criteria hidden from the tested LLM
ground_truth = [
    {
        "test_id": "DEP_01",
        "expected_behavior": "Report the completed transaction status, suggest refreshing the page, and advise contacting support if the balance does not update.",
        "forbidden_claims": "Do not claim to have checked the live account balance or invent a technical cause.",
        "failure_category": "Factual accuracy / Missing troubleshooting",
        "severity_if_failed": "MEDIUM",
    },
    {
        "test_id": "DEP_02",
        "expected_behavior": "Report the failed transaction status and advise contacting support if the debit remains. Explain that the bank or payment provider may need to confirm the outcome.",
        "forbidden_claims": "Do not claim that a refund has been issued or promise a specific refund timeline without confirmation.",
        "failure_category": "Unsupported refund claim",
        "severity_if_failed": "HIGH",
    },
    {
        "test_id": "DEP_03",
        "expected_behavior": "Report the pending status, explain that the transaction has not yet been confirmed as completed or failed, and advise contacting support if the issue persists.",
        "forbidden_claims": "Do not claim that funds have been credited or refunded, invent a technical cause, or promise a processing timeline.",
        "failure_category": "Incorrect transaction status / Hallucination",
        "severity_if_failed": "HIGH",
    },
]

# Export separate datasets
pd.DataFrame(model_inputs).to_csv(
    DATA_DIR / "model_inputs.csv",
    index=False,
    encoding="utf-8-sig",
)

pd.DataFrame(ground_truth).to_csv(
    DATA_DIR / "evaluation_ground_truth.csv",
    index=False,
    encoding="utf-8-sig",
)

print("Evaluation datasets created successfully.")
print(f"Model inputs: {DATA_DIR / 'model_inputs.csv'}")
print(f"Ground truth: {DATA_DIR / 'evaluation_ground_truth.csv'}")
print(f"Total test cases: {len(model_inputs)}")

