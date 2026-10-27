#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-4.0
"""
Deterministic Governance-as-Code Build Gate for the KYC Agentic Subprocess
(Chapters 9, 10, 11, 12, and 14 of The Governance-as-Code Playbook).

Executes five deterministic validation gates across the KYC reference artefacts:
  1. Step 2 Policy Derivation & Override Audit (kyc-use-case.yaml + derivation-rules.yaml -> risk-shortlist.json)
  2. CALM Structural & Reachable-Surface Boundary Check (kyc-agentic-subprocess.calm.json)
  3. Risk-to-Control Traceability & File Resolution (risk-shortlist.json -> CALM controls)
  4. Portable DMN Decision Table Exhaustive Invariant Check (kyc-risk-confidence-dmn.json)
  5. First-Class Evidence & Shared/External Control Lifecycle Gate (control-state.json)

Usage:
  python3 examples/kyc/ci/validate_governance.py
  python3 examples/kyc/ci/validate_governance.py --self-test
"""

from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple


def _parse_scalar(val: str) -> Any:
    val = val.strip()
    if val in ("true", "True"):
        return True
    if val in ("false", "False"):
        return False
    if val in ("null", "None", "~"):
        return None
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    try:
        if "." in val:
            return float(val)
        return int(val)
    except ValueError:
        return val


def load_yaml_or_json(path: Path) -> Dict[str, Any]:
    """Load YAML or JSON using PyYAML if installed, or a deterministic stdlib YAML subset parser."""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except ImportError:
        pass

    # Deterministic stdlib parser for the block-YAML subset used in examples/kyc/
    lines: List[Tuple[int, str]] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        lines.append((indent, stripped))

    def parse_block(idx: int, min_indent: int) -> Tuple[Any, int]:
        if idx >= len(lines):
            return {}, idx
        first_indent, first_content = lines[idx]
        if first_indent < min_indent:
            return {}, idx

        if first_content.startswith("- "):
            arr: List[Any] = []
            while idx < len(lines):
                indent, content = lines[idx]
                if indent < first_indent or not content.startswith("- "):
                    break
                if indent > first_indent:
                    break
                item_body = content[2:].strip()
                if ":" in item_body and not (item_body.startswith('"') or item_body.startswith("'")):
                    k, v = item_body.split(":", 1)
                    obj: Dict[str, Any] = {k.strip(): _parse_scalar(v)}
                    idx += 1
                    while idx < len(lines) and lines[idx][0] > first_indent:
                        sub_indent, sub_content = lines[idx]
                        if sub_content.startswith("- "):
                            break
                        sk, sv = sub_content.split(":", 1)
                        sk = sk.strip()
                        sv = sv.strip()
                        if sv == "":
                            nested_val, idx = parse_block(idx + 1, sub_indent + 1)
                            obj[sk] = nested_val
                        else:
                            obj[sk] = _parse_scalar(sv)
                            idx += 1
                    arr.append(obj)
                else:
                    arr.append(_parse_scalar(item_body))
                    idx += 1
            return arr, idx

        mapping: Dict[str, Any] = {}
        while idx < len(lines):
            indent, content = lines[idx]
            if indent < first_indent:
                break
            if indent > first_indent:
                break
            if content.startswith("- "):
                break
            key, val = content.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val == "":
                nested, idx = parse_block(idx + 1, indent + 1)
                mapping[key] = nested
            else:
                mapping[key] = _parse_scalar(val)
                idx += 1
        return mapping, idx

    parsed, _ = parse_block(0, 0)
    return parsed


def parse_iso8601(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts).astimezone(timezone.utc)


def validate_bundle(
    use_case: Dict[str, Any],
    derivation_rules: Dict[str, Any],
    risk_shortlist: Dict[str, Any],
    calm_doc: Dict[str, Any],
    dmn_doc: Dict[str, Any],
    evidence_doc: Dict[str, Any],
    calm_dir: Path | None = None,
) -> List[str]:
    """Run all 5 deterministic governance gates and return a list of violation strings (empty if valid)."""
    errors: List[str] = []

    # -------------------------------------------------------------------------
    # Gate 1: Step 2 Deterministic Policy Derivation & Override Audit
    # -------------------------------------------------------------------------
    taxonomy = use_case.get("taxonomy_classification", {})
    override_policy = derivation_rules.get("override_policy", {})
    non_overridable = set(override_policy.get("non_overridable_severities", ["critical"]))

    shortlisted_by_id: Dict[str, Dict[str, Any]] = {
        r["risk_id"]: r for r in risk_shortlist.get("shortlisted_risks", [])
    }

    for rule in derivation_rules.get("rules", []):
        prop = rule["when_property"]
        expected_val = rule["equals"]
        if taxonomy.get(prop) == expected_val:
            risk_id = rule["derive_risk_id"]
            if risk_id not in shortlisted_by_id:
                errors.append(
                    f"[Gate 1: Step 2 Derivation] Use-case property '{prop}={expected_val}' triggered rule "
                    f"'{rule['rule_id']}', but derived risk '{risk_id}' is missing from risk-shortlist.json."
                )
                continue

            entry = shortlisted_by_id[risk_id]
            override = entry.get("override")
            if override is not None:
                if rule["severity"] in non_overridable:
                    errors.append(
                        f"[Gate 1: Step 2 Derivation] Risk '{risk_id}' has severity '{rule['severity']}' "
                        f"which is non-overridable under policy '{derivation_rules.get('policy_bundle_id')}'."
                    )
                if override_policy.get("require_mrm_approval_id") and not override.get("mrm_approval_id"):
                    errors.append(
                        f"[Gate 1: Step 2 Derivation] Override on risk '{risk_id}' is missing required 'mrm_approval_id'."
                    )
                if override_policy.get("require_rationale") and not override.get("rationale"):
                    errors.append(
                        f"[Gate 1: Step 2 Derivation] Override on risk '{risk_id}' is missing required 'rationale'."
                    )
            else:
                if entry.get("required_mitigation_id") != rule["required_mitigation_id"]:
                    errors.append(
                        f"[Gate 1: Step 2 Derivation] Risk '{risk_id}' mitigation mismatch: expected "
                        f"'{rule['required_mitigation_id']}', found '{entry.get('required_mitigation_id')}'."
                    )
                if entry.get("calm_control_id") != rule["required_calm_control_id"]:
                    errors.append(
                        f"[Gate 1: Step 2 Derivation] Risk '{risk_id}' CALM control mismatch: expected "
                        f"'{rule['required_calm_control_id']}', found '{entry.get('calm_control_id')}'."
                    )

    # -------------------------------------------------------------------------
    # Gate 2: CALM Structural Integrity & Reachable-Surface Scope Check
    # -------------------------------------------------------------------------
    nodes_by_id = {n["unique-id"]: n for n in calm_doc.get("nodes", [])}
    for rel in calm_doc.get("relationships", []):
        rel_id = rel.get("unique-id", "<unknown>")
        connects = rel.get("relationship-type", {}).get("connects", {})
        src = connects.get("source", {}).get("node")
        dst = connects.get("destination", {}).get("node")
        if src not in nodes_by_id:
            errors.append(f"[Gate 2: CALM Structure] Relationship '{rel_id}' references unknown source node '{src}'.")
        if dst not in nodes_by_id:
            errors.append(
                f"[Gate 2: CALM Structure] Relationship '{rel_id}' references unknown destination node '{dst}'."
            )
        # Architectural boundary invariant: kyc-agent must route decisions via risk-confidence-gate
        if src == "kyc-agent" and dst in ("case-management-queue", "human-analyst-task"):
            errors.append(
                f"[Gate 2: CALM Boundary] Prohibited direct bypass relationship '{rel_id}' from 'kyc-agent' "
                f"to '{dst}'. All agent routing must traverse 'risk-confidence-gate'."
            )

    agent_node = nodes_by_id.get("kyc-agent", {})
    calm_tools = set(agent_node.get("permitted-tools", []))
    use_case_tools = set(use_case.get("permitted_tools", []))
    prohibited_actions = set(use_case.get("prohibited_actions", []))
    if calm_tools != use_case_tools:
        errors.append(
            f"[Gate 2: CALM Scope] kyc-agent permitted-tools in CALM ({sorted(calm_tools)}) do not match "
            f"kyc-use-case.yaml permitted_tools ({sorted(use_case_tools)})."
        )
    overlap_prohibited = calm_tools.intersection(prohibited_actions)
    if overlap_prohibited:
        errors.append(
            f"[Gate 2: CALM Scope] kyc-agent permitted-tools include prohibited actions: {sorted(overlap_prohibited)}."
        )

    # -------------------------------------------------------------------------
    # Gate 3: Shortlisted Risk -> CALM Control Coverage & Config Resolution
    # -------------------------------------------------------------------------
    calm_controls = calm_doc.get("controls", {})
    for risk in risk_shortlist.get("shortlisted_risks", []):
        if risk.get("override") is not None:
            continue
        risk_id = risk["risk_id"]
        ctrl_id = risk["calm_control_id"]
        if ctrl_id not in calm_controls:
            errors.append(
                f"[Gate 3: Control Coverage] Shortlisted risk '{risk_id}' requires CALM control '{ctrl_id}', "
                f"which is missing from kyc-agentic-subprocess.calm.json."
            )
            continue
        ctrl = calm_controls[ctrl_id]
        if ctrl.get("aigf-risk-ref") != risk_id:
            errors.append(
                f"[Gate 3: Control Coverage] CALM control '{ctrl_id}' has aigf-risk-ref '{ctrl.get('aigf-risk-ref')}', "
                f"expected '{risk_id}'."
            )
        if ctrl.get("aigf-mitigation-ref") != risk["required_mitigation_id"]:
            errors.append(
                f"[Gate 3: Control Coverage] CALM control '{ctrl_id}' has aigf-mitigation-ref "
                f"'{ctrl.get('aigf-mitigation-ref')}', expected '{risk['required_mitigation_id']}'."
            )
        reqs = ctrl.get("requirements", [])
        if not reqs:
            errors.append(f"[Gate 3: Control Coverage] CALM control '{ctrl_id}' has no requirements entries.")
        for req in reqs:
            cfg_url = req.get("control-config-url", "")
            if not cfg_url:
                errors.append(f"[Gate 3: Control Coverage] CALM control '{ctrl_id}' has an empty control-config-url.")
            elif calm_dir is not None and not cfg_url.startswith(("http://", "https://")):
                resolved = (calm_dir / cfg_url).resolve()
                if not resolved.exists():
                    errors.append(
                        f"[Gate 3: Control Coverage] CALM control '{ctrl_id}' config file does not exist: {cfg_url}"
                    )

    # -------------------------------------------------------------------------
    # Gate 4: Portable DMN Decision Table Exhaustive Invariant Check
    # -------------------------------------------------------------------------
    if dmn_doc.get("hit_policy") != "FIRST":
        errors.append(
            f"[Gate 4: DMN Invariants] Expected DMN hit_policy 'FIRST', found '{dmn_doc.get('hit_policy')}'."
        )

    dmn_rules = dmn_doc.get("rules", [])

    def eval_dmn(sanctions: str, confidence: float, tier: str) -> str | None:
        for r in dmn_rules:
            s_match = r["sanctions_match_status"] in ("*", sanctions)
            c_match = float(r["min_confidence"]) <= confidence <= float(r["max_confidence"])
            t_match = r["customer_risk_tier"] in ("*", tier)
            if s_match and c_match and t_match:
                return r["routing_decision"]
        return None

    sanctions_domain = ["confirmed", "possible", "none"]
    confidence_probes = [0.0, 0.50, 0.85, 0.94, 0.949999, 0.95, 0.99, 1.0]
    tier_domain = ["low", "medium", "high"]

    for s in sanctions_domain:
        for c in confidence_probes:
            for t in tier_domain:
                decision = eval_dmn(s, c, t)
                if decision is None:
                    errors.append(
                        f"[Gate 4: DMN Completeness] Unhandled input combination: sanctions={s}, "
                        f"confidence={c}, tier={t}."
                    )
                    continue
                if s in ("confirmed", "possible") and decision == "auto-clear":
                    errors.append(
                        f"[Gate 4: DMN Invariant 'no-sanctions-override'] Sanctions status '{s}' "
                        f"(confidence={c}, tier={t}) resolved to forbidden 'auto-clear'."
                    )
                if (c < 0.95 or t != "low") and decision == "auto-clear":
                    errors.append(
                        f"[Gate 4: DMN Invariant 'mandatory-human-review'] Case with confidence={c}, "
                        f"tier='{t}' resolved to forbidden 'auto-clear'."
                    )

    # -------------------------------------------------------------------------
    # Gate 5: First-Class Evidence & Shared/External Control Lifecycle Gate
    # -------------------------------------------------------------------------
    eval_now = parse_iso8601(evidence_doc["evaluation_timestamp"])
    control_states_by_id = {cs["control_id"]: cs for cs in evidence_doc.get("control_states", [])}

    for ctrl_id in calm_controls:
        if ctrl_id not in control_states_by_id:
            errors.append(
                f"[Gate 5: Evidence Lifecycle] CALM control '{ctrl_id}' has no control_state entry in control-state.json."
            )
            continue

        cs = control_states_by_id[ctrl_id]
        declared_state = cs.get("lifecycle_state")
        max_age_hours = float(cs.get("freshness_policy", {}).get("max_age_hours", 24))
        records = cs.get("evidence_records", [])

        # Determine effective lifecycle state from evidence records
        has_contradicted = declared_state == "contradicted" or any(
            r.get("status") == "contradicted" for r in records
        )
        verified_records = [r for r in records if r.get("status") == "verified"]
        superseded_records = [r for r in records if r.get("status") == "superseded"]

        if has_contradicted:
            effective_state = "contradicted"
        elif not records or (not verified_records and not superseded_records):
            effective_state = "insufficient"
        elif not verified_records and superseded_records:
            effective_state = "superseded"
        else:
            # Check freshness of the newest verified evidence record
            newest_age_hours = min(
                (eval_now - parse_iso8601(r["collected_at"])).total_seconds() / 3600.0
                for r in verified_records
            )
            if newest_age_hours > max_age_hours or newest_age_hours < 0:
                effective_state = "stale"
            else:
                effective_state = "current"

        if declared_state != "current" or effective_state != "current":
            errors.append(
                f"[Gate 5: Evidence Lifecycle] Control '{ctrl_id}' failed evidence gate: "
                f"declared='{declared_state}', effective='{effective_state}' (must be 'current')."
            )

        # Verify covered nodes exist in CALM
        for node_id in cs.get("covered_nodes", []):
            if node_id not in nodes_by_id:
                errors.append(
                    f"[Gate 5: Evidence Scope] Control '{ctrl_id}' references unknown covered_node '{node_id}'."
                )

        # Shared / external provider control boundary check
        if cs.get("enforcement_mode") == "shared-control-and-provider-evidence":
            ext = cs.get("external_dependency", {})
            provider_node = ext.get("provider_node")
            if provider_node not in nodes_by_id:
                errors.append(
                    f"[Gate 5: Shared/Provider Control] Control '{ctrl_id}' external_dependency references "
                    f"undeclared provider_node '{provider_node}'."
                )
            if not ext.get("zero_data_retention_attested"):
                errors.append(
                    f"[Gate 5: Shared/Provider Control] External provider '{provider_node}' on control '{ctrl_id}' "
                    f"lacks 'zero_data_retention_attested=true'."
                )
            if int(ext.get("token_budget_cap_per_case", 0)) <= 0:
                errors.append(
                    f"[Gate 5: Shared/Provider Control] External provider '{provider_node}' on control '{ctrl_id}' "
                    f"must enforce a positive 'token_budget_cap_per_case'."
                )

    return errors


def run_self_test(
    use_case: Dict[str, Any],
    derivation_rules: Dict[str, Any],
    risk_shortlist: Dict[str, Any],
    calm_doc: Dict[str, Any],
    dmn_doc: Dict[str, Any],
    evidence_doc: Dict[str, Any],
    calm_dir: Path,
) -> int:
    print("=== Running KYC Governance-as-Code Adversarial Self-Test Battery ===")

    # 0. Happy Path
    errs = validate_bundle(
        use_case, derivation_rules, risk_shortlist, calm_doc, dmn_doc, evidence_doc, calm_dir
    )
    if errs:
        print("[FAIL] Happy Path failed unexpectedly:", errs)
        return 1
    print("[PASS] Case 0 (Happy Path): All 5 deterministic gates passed with 0 violations.")

    # 1. Unhappy Path 1: Missing CALM Control for Shortlisted Risk RI-KYC-12
    calm_missing_ctrl = copy.deepcopy(calm_doc)
    del calm_missing_ctrl["controls"]["mandatory-human-review"]
    errs = validate_bundle(
        use_case, derivation_rules, risk_shortlist, calm_missing_ctrl, dmn_doc, evidence_doc, calm_dir
    )
    assert any("Gate 3: Control Coverage" in e and "mandatory-human-review" in e for e in errs), errs
    print("[PASS] Case 1 (Missing CALM Control for RI-KYC-12): Blocked by Gate 3.")

    # 2. Unhappy Path 2: Unpermitted Override on Critical Risk RI-KYC-07
    shortlist_bad_override = copy.deepcopy(risk_shortlist)
    shortlist_bad_override["shortlisted_risks"][0]["override"] = {
        "mrm_approval_id": "MRM-FAKE-001",
        "rationale": "Attempt to waive sanctions override control",
    }
    errs = validate_bundle(
        use_case, derivation_rules, shortlist_bad_override, calm_doc, dmn_doc, evidence_doc, calm_dir
    )
    assert any("Gate 1: Step 2 Derivation" in e and "non-overridable" in e for e in errs), errs
    print("[PASS] Case 2 (Critical Risk Override Attempt on RI-KYC-07): Blocked by Gate 1.")

    # 3. Unhappy Path 3: Direct Agent Bypass Relationship to case-management-queue
    calm_bypass = copy.deepcopy(calm_doc)
    calm_bypass["relationships"].append(
        {
            "unique-id": "agent-direct-queue-bypass",
            "relationship-type": {
                "connects": {
                    "source": {"node": "kyc-agent"},
                    "destination": {"node": "case-management-queue"},
                }
            },
        }
    )
    errs = validate_bundle(
        use_case, derivation_rules, risk_shortlist, calm_bypass, dmn_doc, evidence_doc, calm_dir
    )
    assert any("Gate 2: CALM Boundary" in e and "agent-direct-queue-bypass" in e for e in errs), errs
    print("[PASS] Case 3 (Agent Direct Bypass Edge to Case Queue): Blocked by Gate 2.")

    # 4. Unhappy Path 4: Weakened DMN Confidence Threshold (0.85 instead of 0.95)
    dmn_weak = copy.deepcopy(dmn_doc)
    for r in dmn_weak["rules"]:
        if r["rule_id"] == "DMN-R3":
            r["max_confidence"] = 0.849999
        elif r["rule_id"] == "DMN-R6":
            r["min_confidence"] = 0.85
    errs = validate_bundle(
        use_case, derivation_rules, risk_shortlist, calm_doc, dmn_weak, evidence_doc, calm_dir
    )
    assert any("Gate 4: DMN Invariant 'mandatory-human-review'" in e for e in errs), errs
    print("[PASS] Case 4 (Weakened DMN Confidence Floor 0.85): Blocked by Gate 4.")

    # 5. Unhappy Path 5: Stale Shared-Control Evidence Beyond 24h Freshness Window
    evidence_stale = copy.deepcopy(evidence_doc)
    for cs in evidence_stale["control_states"]:
        if cs["control_id"] == "ccc-workload-isolation":
            cs["evidence_records"][0]["collected_at"] = "2026-10-20T00:00:00Z"
    errs = validate_bundle(
        use_case, derivation_rules, risk_shortlist, calm_doc, dmn_doc, evidence_stale, calm_dir
    )
    assert any("Gate 5: Evidence Lifecycle" in e and "effective='stale'" in e for e in errs), errs
    print("[PASS] Case 5 (Stale Shared-Control Provider Evidence >24h TTL): Blocked by Gate 5.")

    # 6. Unhappy Path 6: Contradicted Runtime Evidence on no-sanctions-override
    evidence_contradicted = copy.deepcopy(evidence_doc)
    evidence_contradicted["control_states"][0]["evidence_records"].append(
        {
            "evidence_id": "EV-RUNTIME-ANOMALY-01",
            "source_type": "otel-runtime-assertion",
            "producer": "production-trace-collector",
            "collected_at": "2026-10-26T17:55:00Z",
            "status": "contradicted",
            "summary": "Detected unrouted sanctions exception in staging trace.",
        }
    )
    errs = validate_bundle(
        use_case, derivation_rules, risk_shortlist, calm_doc, dmn_doc, evidence_contradicted, calm_dir
    )
    assert any("Gate 5: Evidence Lifecycle" in e and "effective='contradicted'" in e for e in errs), errs
    print("[PASS] Case 6 (Contradicted Runtime Evidence Record): Blocked by Gate 5.")

    # 7. Unhappy Path 7: Superseded-Only Evidence Without Current Replacement
    evidence_superseded = copy.deepcopy(evidence_doc)
    for cs in evidence_superseded["control_states"]:
        if cs["control_id"] == "ccc-workload-isolation":
            cs["evidence_records"] = [
                r for r in cs["evidence_records"] if r["status"] == "superseded"
            ]
    errs = validate_bundle(
        use_case, derivation_rules, risk_shortlist, calm_doc, dmn_doc, evidence_superseded, calm_dir
    )
    assert any("Gate 5: Evidence Lifecycle" in e and "effective='superseded'" in e for e in errs), errs
    print("[PASS] Case 7 (Superseded-Only Evidence Record): Blocked by Gate 5.")

    # 8. Unhappy Path 8: Non-Critical Risk Override Missing MRM Approval ID or Rationale
    shortlist_incomplete_override = copy.deepcopy(risk_shortlist)
    shortlist_incomplete_override["shortlisted_risks"][2]["override"] = {
        "mrm_approval_id": "",
        "rationale": "",
    }
    errs = validate_bundle(
        use_case, derivation_rules, shortlist_incomplete_override, calm_doc, dmn_doc, evidence_doc, calm_dir
    )
    assert any("missing required 'mrm_approval_id'" in e for e in errs), errs
    assert any("missing required 'rationale'" in e for e in errs), errs
    print("[PASS] Case 8 (Override Missing MRM Approval ID / Rationale): Blocked by Gate 1.")

    # 9. Happy Path 9: Audited Non-Critical Risk Override With Valid MRM Approval & Rationale
    shortlist_valid_override = copy.deepcopy(risk_shortlist)
    shortlist_valid_override["shortlisted_risks"][2]["override"] = {
        "mrm_approval_id": "MRM-2026-EXC-019",
        "rationale": "compensating OCR air-gap proxy enforced upstream",
    }
    errs = validate_bundle(
        use_case, derivation_rules, shortlist_valid_override, calm_doc, dmn_doc, evidence_doc, calm_dir
    )
    assert not errs, f"Valid non-critical MRM override should pass, got: {errs}"
    print("[PASS] Case 9 (Audited Non-Critical MRM Override With Approval & Rationale): Permitted by Gate 1 & Gate 3.")

    # 10. Unhappy Path 10: Agent Permitted-Tools Escalation (Prohibited Action Added)
    calm_bad_tools = copy.deepcopy(calm_doc)
    for node in calm_bad_tools["nodes"]:
        if node["unique-id"] == "kyc-agent":
            node["permitted-tools"].append("override-sanctions-hit")
    errs = validate_bundle(
        use_case, derivation_rules, risk_shortlist, calm_bad_tools, dmn_doc, evidence_doc, calm_dir
    )
    assert any("Gate 2: CALM Scope" in e and "override-sanctions-hit" in e for e in errs), errs
    print("[PASS] Case 10 (Agent Tool Privilege Escalation 'override-sanctions-hit'): Blocked by Gate 2.")

    # 11. Unhappy Path 11: Broken control-config-url File Reference in CALM
    calm_broken_url = copy.deepcopy(calm_doc)
    calm_broken_url["controls"]["no-sanctions-override"]["requirements"][0]["control-config-url"] = (
        "../workflow/non-existent-dmn.json"
    )
    errs = validate_bundle(
        use_case, derivation_rules, risk_shortlist, calm_broken_url, dmn_doc, evidence_doc, calm_dir
    )
    assert any("Gate 3: Control Coverage" in e and "config file does not exist" in e for e in errs), errs
    print("[PASS] Case 11 (Broken CALM control-config-url Path): Blocked by Gate 3.")

    # 12. Unhappy Path 12: Unverified External Provider Zero-Data-Retention / Token Cap
    evidence_bad_provider = copy.deepcopy(evidence_doc)
    for cs in evidence_bad_provider["control_states"]:
        if cs["control_id"] == "ccc-workload-isolation":
            cs["external_dependency"]["zero_data_retention_attested"] = False
            cs["external_dependency"]["token_budget_cap_per_case"] = 0
    errs = validate_bundle(
        use_case, derivation_rules, risk_shortlist, calm_doc, dmn_doc, evidence_bad_provider, calm_dir
    )
    assert any("lacks 'zero_data_retention_attested=true'" in e for e in errs), errs
    assert any("positive 'token_budget_cap_per_case'" in e for e in errs), errs
    print("[PASS] Case 12 (External Provider Missing Zero-Data-Retention / Token Budget): Blocked by Gate 5.")

    # 13. Unhappy Path 13: Insufficient Evidence (Empty Evidence Records)
    evidence_insufficient = copy.deepcopy(evidence_doc)
    evidence_insufficient["control_states"][1]["evidence_records"] = []
    errs = validate_bundle(
        use_case, derivation_rules, risk_shortlist, calm_doc, dmn_doc, evidence_insufficient, calm_dir
    )
    assert any("Gate 5: Evidence Lifecycle" in e and "effective='insufficient'" in e for e in errs), errs
    print("[PASS] Case 13 (Insufficient / Missing Evidence Records): Blocked by Gate 5.")

    print("=== All 14/14 Governance-as-Code Self-Test Scenarios Passed ===")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate KYC Governance-as-Code artefacts.")
    base_dir = Path(__file__).resolve().parent.parent
    parser.add_argument("--use-case", type=Path, default=base_dir / "use-case" / "kyc-use-case.yaml")
    parser.add_argument("--derivation-rules", type=Path, default=base_dir / "policy" / "derivation-rules.yaml")
    parser.add_argument("--risk-shortlist", type=Path, default=base_dir / "risk-shortlist.json")
    parser.add_argument("--calm", type=Path, default=base_dir / "calm" / "kyc-agentic-subprocess.calm.json")
    parser.add_argument("--dmn", type=Path, default=base_dir / "workflow" / "kyc-risk-confidence-dmn.json")
    parser.add_argument("--evidence", type=Path, default=base_dir / "evidence" / "control-state.json")
    parser.add_argument("--self-test", action="store_true", help="Run happy-path and 7 adversarial mutation tests.")
    args = parser.parse_args()

    use_case = load_yaml_or_json(args.use_case)
    derivation_rules = load_yaml_or_json(args.derivation_rules)
    risk_shortlist = load_yaml_or_json(args.risk_shortlist)
    calm_doc = load_yaml_or_json(args.calm)
    dmn_doc = load_yaml_or_json(args.dmn)
    evidence_doc = load_yaml_or_json(args.evidence)
    calm_dir = args.calm.resolve().parent

    if args.self_test:
        return run_self_test(
            use_case, derivation_rules, risk_shortlist, calm_doc, dmn_doc, evidence_doc, calm_dir
        )

    errors = validate_bundle(
        use_case, derivation_rules, risk_shortlist, calm_doc, dmn_doc, evidence_doc, calm_dir
    )
    if errors:
        print(f"Governance build gate FAILED with {len(errors)} violation(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("Governance build gate PASSED:")
    print(f"  - Use Case:         {use_case['use_case_id']} ({use_case['name']})")
    print(f"  - Derivation Policy:{derivation_rules['policy_bundle_id']} ({len(risk_shortlist['shortlisted_risks'])} risks verified)")
    print(f"  - CALM Spec:        {calm_doc['unique-id']} ({len(calm_doc['nodes'])} nodes, {len(calm_doc['controls'])} controls)")
    print(f"  - DMN Gate Table:   {dmn_doc['decision_table_id']} ({len(dmn_doc['rules'])} rules, 72/72 permutations verified)")
    print(f"  - Evidence State:   {len(evidence_doc['control_states'])}/4 controls 'current' within freshness TTL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
