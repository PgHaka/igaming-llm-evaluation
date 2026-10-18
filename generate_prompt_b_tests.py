from pathlib import Path

base = Path(__file__).resolve().parent
prompt_dir = base / "prompts"

prompt_b = (base / "prompt_b.txt").read_text(encoding="utf-8").strip()

test_ids = [
    "DEP_02",
    "KYC_02",
    "WD_03",
    "ADV_01",
    "ADV_02",
    "ADV_03",
]

for test_id in test_ids:
    source = prompt_dir / f"{test_id}_blind_prompt.txt"

    if not source.exists():
        print(f"SKIPPED: {test_id} — source prompt missing")
        continue

    original = source.read_text(encoding="utf-8")

    marker = "CUSTOMER MESSAGE:"

    if marker not in original:
        print(f"SKIPPED: {test_id} — customer message marker missing")
        continue

    scenario = original[original.index(marker):]

    output = prompt_dir / f"{test_id}_prompt_b.txt"
    output.write_text(
        prompt_b + "\n\n" + scenario,
        encoding="utf-8"
    )

    print(f"CREATED: {output.name}")

print("\nPrompt B test generation complete.")
