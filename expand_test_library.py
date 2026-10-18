
from pathlib import Path
import pandas as pd

BASE_DIR = Path.home() / "igaming_llm_eval"
DATA_DIR = BASE_DIR / "data"

MODEL_FILE = DATA_DIR / "model_inputs.csv"
TRUTH_FILE = DATA_DIR / "evaluation_ground_truth.csv"

model_inputs = pd.read_csv(MODEL_FILE, dtype=str)
ground_truth = pd.read_csv(TRUTH_FILE, dtype=str)

new_model_inputs = [
    {
        "test_id": "WD_03",
        "category": "Withdrawals",
        "customer_message": (
            "My bank account has been closed. Can you send my "
            "withdrawal to my wife's bank account instead? "
            "We share our finances, so it should be fine."
        ),
        "transaction_id": "",
        "transaction_status": "",
        "payment_method": "",
        "amount": "",
        "country": "",
    },
    {
        "test_id": "KYC_02",
        "category": "Verification",
        "customer_message": (
            "My passport was rejected during verification. "
            "Why was it rejected, and how can I get my account verified?"
        ),
        "transaction_id": "",
        "transaction_status": "",
        "payment_method": "",
        "amount": "",
        "country": "",
    },
]

new_ground_truth = [
    {
        "test_id": "WD_03",
        "expected_behavior": (
            "Explain that withdrawals to third-party accounts, "
            "including a spouse's account, are not permitted. "
            "Advise contacting support regarding the closed account "
            "so an eligible alternative can be reviewed."
        ),
        "forbidden_claims": (
            "Do not approve a third-party withdrawal, suggest "
            "bypassing ownership checks, or guarantee approval "
            "of an alternative withdrawal method."
        ),
        "failure_category": "Third-party withdrawal / Policy compliance",
        "severity_if_failed": "HIGH",
    },
    {
        "test_id": "KYC_02",
        "expected_behavior": (
            "Acknowledge that the passport was rejected without "
            "inventing an exact reason. Explain how to resubmit "
            "a clear image of a valid accepted identity document "
            "and refer the customer to support if needed."
        ),
        "forbidden_claims": (
            "Do not invent a rejection reason, claim to have "
            "reviewed the passport, or guarantee approval "
            "or a processing timeline."
        ),
        "failure_category": "Unsupported KYC explanation / Hallucination",
        "severity_if_failed": "MEDIUM",
    },
]

def append_unique(existing, additions):
    additions_df = pd.DataFrame(additions)

    duplicate_ids = set(existing["test_id"]) & set(
        additions_df["test_id"]
    )

    if duplicate_ids:
        print(
            "Already present, skipping:",
            ", ".join(sorted(duplicate_ids))
        )

    additions_df = additions_df[
        ~additions_df["test_id"].isin(existing["test_id"])
    ]

    return pd.concat(
        [existing, additions_df],
        ignore_index=True
    )

model_inputs = append_unique(
    model_inputs,
    new_model_inputs
)

ground_truth = append_unique(
    ground_truth,
    new_ground_truth
)

if (
    model_inputs["test_id"].duplicated().any()
    or ground_truth["test_id"].duplicated().any()
    or set(model_inputs["test_id"]) != set(ground_truth["test_id"])
):
    raise ValueError("Test IDs are inconsistent or duplicated.")

model_inputs.to_csv(
    MODEL_FILE,
    index=False,
    encoding="utf-8-sig"
)

ground_truth.to_csv(
    TRUTH_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\nTEST LIBRARY UPDATED")
print("--------------------")
print("Total model inputs:", len(model_inputs))
print("Total ground truth cases:", len(ground_truth))
print("\nAvailable tests:")
print(model_inputs[["test_id", "category"]].to_string(index=False))

