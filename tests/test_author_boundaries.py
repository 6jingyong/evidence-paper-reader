import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
SCRIPTS = SKILL / "scripts"
REFS = SKILL / "references"
RUN_ROOT = ROOT / "validation-runs" / "real-papers"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


render = load_module("author_boundary_render", SCRIPTS / "render_audit.py")
gate = load_module("author_boundary_gate", SCRIPTS / "audit_gate.py")
markdown = load_module("author_boundary_markdown", SCRIPTS / "validate_audit.py")
ALLOWED = markdown.evidence_labels((REFS / "evidence-types.md").read_text(encoding="utf-8"))


def valid_v4():
    data = copy.deepcopy(render.TEMPLATE)
    data["paper_type"] = "controlled empirical study"
    data["reader_conclusion"] = "The bounded claims are separated from broader inferential reach."
    for index, claim in enumerate(data["claims"], start=1):
        claim["content"] = f"Bounded claim {index}."
        claim["support"]["evidence_type"] = ["direct experiment"]
        claim["support"]["source_location"] = f"Results {index}"
        claim["support"]["support_level"] = "sufficient"
        claim["support"]["reason"] = "The listed result supports this bounded claim."
        claim["support"]["author_boundary"] = {
            "status": "not-applicable",
            "summary": "none",
            "source_location": "none",
        }
    data["usable"] = {
        "results": "The bounded results are usable.",
        "methods_or_design": "The disclosed design is inspectable.",
        "materials_or_documentation": "The result locations are documented.",
    }
    data["downweight"] = {
        "worth_noticing": "The broader interpretation is separable from the result.",
        "cautious_or_ignore": "Do not extend beyond the stated setting.",
    }
    data["value_breakdown"] = {
        "result": "high",
        "method": "medium",
        "theory_or_insight": "medium",
        "research_design": "medium",
        "material_or_documentation": "high",
    }
    data["uncertainty_and_follow_up"] = "External transfer remains open."
    return data


class AuthorBoundaryTests(unittest.TestCase):
    def test_schema_v4_template_contains_author_boundary_metadata(self):
        self.assertEqual(render.LEDGER_SCHEMA_VERSION, 4)
        for claim in render.TEMPLATE["claims"]:
            boundary = claim["support"]["author_boundary"]
            self.assertIn(
                boundary["status"],
                {"explicit", "partial", "absent", "unclear", "not-applicable"},
            )

    def test_non_sufficient_claim_cannot_skip_author_boundary_assessment(self):
        data = valid_v4()
        data["claims"][2]["support"]["support_level"] = "partial"
        data["reasoning_edges"][2]["reasoning_status"] = "qualified"
        data["reasoning_edges"][2]["added_reach"] = "Extends beyond the direct result."
        errors = render.validate_ledger(data)
        self.assertTrue(
            any("requires an author-boundary assessment" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("cannot use not-applicable author boundary" in error for error in gate.validate_author_boundary_closure(data)),
            gate.validate_author_boundary_closure(data),
        )

    def test_explicit_or_partial_acknowledgment_requires_concrete_location(self):
        data = valid_v4()
        data["claims"][2]["support"]["support_level"] = "partial"
        data["reasoning_edges"][2]["reasoning_status"] = "qualified"
        data["reasoning_edges"][2]["added_reach"] = "Extends beyond the direct result."
        data["claims"][2]["support"]["author_boundary"] = {
            "status": "explicit",
            "summary": "The authors state that external validation is still needed.",
            "source_location": "none",
        }
        errors = render.validate_ledger(data)
        self.assertTrue(
            any("requires a concrete source_location" in error for error in errors),
            errors,
        )
        self.assertTrue(gate.validate_author_boundary_closure(data))

    def test_absent_or_unclear_status_requires_explanation(self):
        data = valid_v4()
        data["claims"][2]["support"]["support_level"] = "partial"
        data["reasoning_edges"][2]["reasoning_status"] = "qualified"
        data["reasoning_edges"][2]["added_reach"] = "Extends beyond the direct result."
        data["claims"][2]["support"]["author_boundary"] = {
            "status": "unclear",
            "summary": "none",
            "source_location": "none",
        }
        errors = render.validate_ledger(data)
        self.assertTrue(
            any("requires a short explanatory summary" in error for error in errors),
            errors,
        )

    def test_rendered_v4_places_author_acknowledgment_next_to_support_judgment(self):
        data = valid_v4()
        data["claims"][2]["support"]["support_level"] = "partial"
        data["reasoning_edges"][2]["reasoning_status"] = "qualified"
        data["reasoning_edges"][2]["added_reach"] = "Extends the local result to a broader population."
        data["claims"][2]["support"]["author_boundary"] = {
            "status": "explicit",
            "summary": "The authors themselves state that broader external validation is needed.",
            "source_location": "Discussion; Limitations",
        }

        self.assertEqual(render.validate_ledger(data), [])
        text = render.render(data)
        self.assertIn("- support level: partial", text)
        self.assertIn("- author boundary: explicit", text)
        self.assertIn(
            "- author acknowledgment: The authors themselves state that broader external validation is needed.",
            text,
        )
        self.assertIn("- author-boundary source: Discussion; Limitations", text)
        self.assertEqual(markdown.validate(text, ALLOWED), [])

    def test_g129_independently_rejects_source_free_explicit_acknowledgment(self):
        data = valid_v4()
        data["claims"][0]["support"]["author_boundary"] = {
            "status": "explicit",
            "summary": "The authors explicitly acknowledge a limitation.",
            "source_location": "none",
        }
        errors = gate.validate_author_boundary_closure(data)
        self.assertTrue(
            any("requires a concrete source location" in error for error in errors),
            errors,
        )

    def test_reference_cases_capture_partial_and_explicit_author_acknowledgment(self):
        cases = {
            "photochemical-sei-fast-charge-2021": (
                "partial",
                "Discussion/Conclusion; manufacturing applicability and future directions",
            ),
            "microclimatic-warming-paramo-2021": (
                "explicit",
                "Discussion/Conclusion; future shrub-dominance interpretation and further-research statement",
            ),
            "deep-lob-forecasting-2024": (
                "explicit",
                "Results 7.2; Table 8; Conclusion and future work",
            ),
        }
        round_root = RUN_ROOT / "2026-09-26-round-04"
        for case_id, (status, location) in cases.items():
            with self.subTest(case_id=case_id):
                ledger = json.loads(
                    (round_root / case_id / "ledger.json").read_text(encoding="utf-8")
                )
                self.assertEqual(ledger["ledger_schema_version"], 4)
                boundary = ledger["claims"][2]["support"]["author_boundary"]
                self.assertEqual(boundary["status"], status)
                self.assertEqual(boundary["source_location"], location)
                self.assertEqual(render.validate_ledger(ledger), [])
                self.assertEqual(gate.validate_author_boundary_closure(ledger), [])


if __name__ == "__main__":
    unittest.main()
