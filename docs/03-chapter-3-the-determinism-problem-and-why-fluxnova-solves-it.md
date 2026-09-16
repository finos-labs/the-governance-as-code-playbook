<!--
SPDX-License-Identifier: CC-BY-4.0
Copyright 2026 Fintech Open Source Foundation
-->

# Chapter 3 — The Determinism Problem, and Why Fluxnova Solves It

Here's the tension at the heart of every agentic AI compliance conversation: LLMs are non-deterministic by nature. Ask the same question twice and you can get two different answers, two different tool-call sequences, two different paths through a task. That's a feature for creativity and adaptability — and a serious liability for an FSI organization, where a regulator, an auditor, or a court needs to know that a specific process was followed the same way every time, that specific approval gates were never skipped, and that the sequence of decisions leading to an outcome can be reconstructed after the fact.

An agent that "decides for itself" whether to check a sanctions list, escalate to a human, or proceed autonomously isn't just unpredictable — from a governance standpoint, it's unauditable. If the reasoning path isn't fixed, the evidence trail isn't fixed either, and an FSI organization cannot certify or attest to a process it can't reliably reproduce.

Fluxnova's role in the pipeline is to draw a hard line between the parts of a workflow that must be deterministic and the parts where an LLM's judgment genuinely adds value — and to keep the deterministic parts deterministic even when AI is involved throughout. Built on BPMN and DMN, with a focus on audit-ready execution, Fluxnova gives financial institutions the same operational guarantees traditional distributed systems have always required, with probabilistic decision-making layered on top only where it's supposed to be. Concretely:

- **The process backbone is fixed, modeled, and enforced.** A workflow — say, a loan-servicing exception or a KYC remediation case — is expressed as a BPMN model: a defined sequence of steps, gateways, and approval points that the orchestration engine executes exactly as specified, every time. The LLM doesn't get to skip a mandatory human-in-the-loop checkpoint or reorder a sequence of controls because it decided that was more efficient — the process model is the authority, not the model's own judgment about what to do next.

- **DMN pins down the decision logic that must be consistent.** Wherever a decision needs to be rule-based and reproducible — eligibility thresholds, escalation criteria, risk scoring bands — Decision Model and Notation captures that logic explicitly and separately from the LLM, so the same inputs always produce the same decision, and that decision logic can be reviewed, versioned, and audited independently of any model's behavior.

- **The LLM operates inside guardrails, not instead of them.** Non-deterministic reasoning gets scoped to where it belongs — summarizing a document, drafting a response, interpreting ambiguous free-text input — while the orchestration layer around it stays fixed.

- **Every execution is traced.** Because the engine executes and traces workflows as a matter of course, business and compliance teams get full visibility into exactly where a given case is, what path it took to get there, and whether service-level and control commitments were met — turning "trust us, the agent behaved" into a reconstructable execution record.

## 3.1 Why This Makes the Agentic Solution More Compliant, Not Just More Reliable

- **Reproducibility becomes provable, not asserted.** When a regulator asks how a specific customer outcome was reached, the answer isn't "the model decided" — it's the exact BPMN path and DMN decision the case followed.

- **Control points can't be silently bypassed.** Mandatory checks — sanctions screening, four-eyes approval, escalation thresholds — live in the process model itself, not in a prompt instructing the model to "remember" to do them. A prompt is a request; a BPMN gateway is an enforcement point.

- **Non-determinism gets contained, not eliminated.** FSI organizations don't need to strip agentic AI of its adaptive value to make it compliant — they need to make sure the unpredictable part of the system can't touch the part that has to be predictable.

- **Evidence generation is automatic.** Because execution is traced by default, the audit trail an examiner or an AIUC-1-style adversarial tester would ask for already exists as a byproduct of running the process, rather than needing to be reconstructed or, worse, self-reported.

This is also why Fluxnova sits naturally inside AIGF's broader risk catalog rather than beside it: AIGF defines which risks demand a deterministic control point — an autonomy boundary, an oversight gate, a data-handling rule — and Fluxnova is the mechanism that actually enforces that boundary at runtime, every single execution, regardless of what the underlying model decides to do.
