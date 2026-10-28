<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Runnable KYC Reference Bundle (`examples/kyc/`)

This directory contains the self-contained, executable artefacts for the **Agentic KYC Document Review Assistant** worked example traced across Chapters 9–14 of *The Governance-as-Code Playbook*.

It allows readers and CI pipelines to execute the complete pipeline—from use-case taxonomy properties and deterministic risk derivation through CALM architecture validation, DMN decision-table invariants, and first-class evidence lifecycle evaluation—with zero external dependencies beyond Python 3.

## Artefact Map

| Pipeline Step | Playbook Chapter | Artefact Path | Purpose |
| :--- | :--- | :--- | :--- |
| **Step 1 — Classify Use Case** | Chapter 9 (`9.2`) | [`use-case/kyc-use-case.yaml`](./use-case/kyc-use-case.yaml) | Machine-readable taxonomy classification (`autonomy_level`, `tool_authority`, `human_oversight`, `data_sensitivity`, `regulatory_criticality`, `permitted_tools`, `prohibited_actions`). |
| **Step 2 — Deterministic Policy Derivation** | Chapter 9 (`9.2.1`) | [`policy/derivation-rules.yaml`](./policy/derivation-rules.yaml) | Policy-as-code rules mapping use-case properties to candidate AIGF risks, required mitigations, and CALM controls, with explicit Model Risk Management (`MRM`) override governance. |
| **Step 2 Output — Risk Shortlist** | Chapter 9 (`9.2`) & Chapter 12 | [`risk-shortlist.json`](./risk-shortlist.json) | Derived + MRM-approved shortlist (`RI-KYC-07`, `RI-KYC-12`, `RI-KYC-15`, `RI-KYC-19`) linking each risk to its AIGF mitigation and CALM control ID. |
| **Step 4 — CALM Specification** | Chapter 10 (`10.2`–`10.6`) | [`calm/kyc-agentic-subprocess.calm.json`](./calm/kyc-agentic-subprocess.calm.json) | Complete CALM architecture specification covering business nodes, reference orchestration nodes (`fluxnova-engine`, `fluxnova-dmn-service`), external dependencies (`llm-provider`), relationships, and controls. |
| **Step 5 — Deterministic Gate Table** | Chapter 11 (`11.1.1`, `11.5`) | [`workflow/kyc-risk-confidence-dmn.json`](./workflow/kyc-risk-confidence-dmn.json) | Portable deterministic decision table (`FIRST` hit policy) enforcing `no-sanctions-override` and `mandatory-human-review` (`>= 0.95` confidence floor), mapped to the Fluxnova DMN reference engine. |
| **Step 6 — CI/CD Build Gate** | Chapter 12 (`12.2`–`12.6`) | [`ci/validate_governance.py`](./ci/validate_governance.py) | Deterministic 5-gate validator and adversarial self-test suite (`--self-test`). |
| **Step 8 — First-Class Evidence & Shared-Control State** | Chapter 14 (`14.4.1`) | [`evidence/control-state.json`](./evidence/control-state.json) | First-class control-state and evidence artefact distinguishing `direct-enforcement` from `shared-control-and-provider-evidence`, with explicit freshness TTLs and lifecycle states (`current`, `stale`, `insufficient`, `superseded`, `contradicted`). |

## Running the Build Gate Locally

Validate the complete KYC governance bundle:

```bash
python3 examples/kyc/ci/validate_governance.py
```

Run the built-in adversarial self-test suite (verifying the happy path plus 7 mutation scenarios across unapproved overrides, missing controls, agent bypass edges, weakened DMN thresholds, and stale/contradicted/superseded evidence):

```bash
python3 examples/kyc/ci/validate_governance.py --self-test
```
