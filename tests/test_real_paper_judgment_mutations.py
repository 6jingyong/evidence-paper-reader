import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
RUN_ROOT = ROOT / "validation-runs" / "real-papers"
VALIDATOR = RUN_ROOT / "validate_judgments.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validator = load_module("real_paper_judgment_validator", VALIDATOR)


def load_case(round_id: str, case_id: str):
    round_root = RUN_ROOT / round_id
    manifest = json.loads(
        (round_root / "manifest.json").read_text(encoding="utf-8")
    )
    case = next(item for item in manifest["cases"] if item["id"] == case_id)
    ledger = json.loads(
        (round_root / case_id / "ledger.json").read_text(encoding="utf-8")
    )
    return case["regression_contract"], ledger


class RealPaperJudgmentMutationTests(unittest.TestCase):
    def test_allowed_partial_insufficient_drift_is_accepted(self):
        contract, ledger = load_case(
            "2026-09-26-round-01",
            "attention-is-all-you-need-2017",
        )
        self.assertEqual(validator.judgment_errors(contract, ledger), [])

        mutant = copy.deepcopy(ledger)
        mutant["claims"][2]["support"]["support_level"] = "insufficient"
        self.assertEqual(
            validator.judgment_errors(contract, mutant),
            [],
            "declared partial/insufficient judgment tolerance should be real",
        )

    def test_tolerance_cannot_cross_into_sufficient(self):
        contract, ledger = load_case(
            "2026-09-26-round-01",
            "attention-is-all-you-need-2017",
        )
        mutant = copy.deepcopy(ledger)
        mutant["claims"][2]["support"]["support_level"] = "sufficient"
        errors = validator.judgment_errors(contract, mutant)
        self.assertTrue(
            any("claim 3" in error and "outside allowed range" in error for error in errors),
            errors,
        )

    def test_hard_sufficient_claim_cannot_be_softened(self):
        contract, ledger = load_case(
            "2026-09-26-round-01",
            "sprint-2015",
        )
        mutant = copy.deepcopy(ledger)
        mutant["claims"][0]["support"]["support_level"] = "partial"
        self.assertTrue(validator.judgment_errors(contract, mutant))

    def test_non_auditable_viability_is_hard(self):
        contract, ledger = load_case(
            "2026-09-26-round-02",
            "surgisphere-hcq-2020",
        )
        self.assertEqual(validator.judgment_errors(contract, ledger), [])

        mutant = copy.deepcopy(ledger)
        mutant["evidence_viability"] = "auditable"
        errors = validator.judgment_errors(contract, mutant)
        self.assertTrue(any("viability drift" in error for error in errors), errors)

    def test_source_integrity_flag_cannot_be_removed(self):
        contract, ledger = load_case(
            "2026-09-26-round-02",
            "surgisphere-hcq-2020",
        )
        mutant = copy.deepcopy(ledger)
        mutant["viability_flags"] = ["proprietary-black-box"]
        errors = validator.judgment_errors(contract, mutant)
        self.assertTrue(
            any("missing required viability flag" in error for error in errors),
            errors,
        )

    def test_unapproved_viability_flag_cannot_be_added(self):
        contract, ledger = load_case(
            "2026-09-26-round-02",
            "surgisphere-hcq-2020",
        )
        mutant = copy.deepcopy(ledger)
        mutant["viability_flags"].append("promotional-asymmetry")
        errors = validator.judgment_errors(contract, mutant)
        self.assertTrue(
            any("outside allowed range" in error for error in errors),
            errors,
        )

    def test_claim_count_cannot_drift_inside_tolerance(self):
        contract, ledger = load_case(
            "2026-09-26-round-01",
            "echinacea-2010",
        )
        mutant = copy.deepcopy(ledger)
        mutant["claims"].append(copy.deepcopy(mutant["claims"][-1]))
        errors = validator.judgment_errors(contract, mutant)
        self.assertTrue(any("claim-count drift" in error for error in errors), errors)

    def test_contract_cannot_be_broadened_to_three_support_levels(self):
        contract, _ = load_case(
            "2026-09-26-round-01",
            "attention-is-all-you-need-2017",
        )
        mutant = copy.deepcopy(contract)
        mutant["allowed_range"]["support_levels"][2] = [
            "sufficient",
            "partial",
            "insufficient",
        ]
        errors = validator.contract_errors(mutant)
        self.assertTrue(
            any("too broad" in error for error in errors),
            errors,
        )

    def test_contract_cannot_allow_sufficient_partial_boundary(self):
        contract, _ = load_case(
            "2026-09-26-round-01",
            "attention-is-all-you-need-2017",
        )
        mutant = copy.deepcopy(contract)
        mutant["allowed_range"]["support_levels"][2] = [
            "sufficient",
            "partial",
        ]
        errors = validator.contract_errors(mutant)
        self.assertTrue(
            any("only permitted two-level tolerance" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
