# Chapter 9 — Codifying a Use Case

Step 1 deserves more attention than a single paragraph, for a specific reason: it's not just the first step, it's the *template* for how every subsequent use case gets handled. Get the pattern right once, and every team after you is filling in a known shape rather than inventing a process from scratch. This chapter walks through that pattern in full, using a KYC use case as the worked example, all the way through to opening a pull request against the AIGF repository itself.

## 9.1 Why This Step Is the Template

Everything downstream in the pipeline — the reference architecture in Step 3 (Chapter 10), the CALM specification in Step 4 (also Chapter 10), the Fluxnova process boundaries in Step 5 (Chapter 11), even the decision on AIUC-1 in Step 9 — takes its inputs from what gets produced in Step 1. If the use case is classified loosely or the risk assessment is shallow, every later stage inherits that weakness. So the goal of Step 1 isn't just to produce a classification — it's to produce a small set of concrete, reusable artifacts that the rest of the pipeline can consume mechanically, and that the next team building a similar use case can copy as a starting point.

Four artifacts come out of a well-run Step 1:

1.  A **use case narrative** — what the system does, who it serves, and what decisions or actions it's permitted to take.

<!-- -->

1.  A **taxonomy classification** — where the use case sits against AIGF's Use Cases Taxonomy: type, architecture pattern, autonomy level, tool authority, human-oversight pattern, and data-handling requirements.

2.  A **risk shortlist** — the specific entries from AIGF's risk catalog that actually apply, produced through the eight-step heuristic assessment.

3.  A **mitigation mapping** — the catalog mitigations selected against each shortlisted risk, with enough detail that an engineer can act on them directly.

## 9.2 Worked Example: An Agentic KYC Document Review Assistant

Take a concrete case: an FSI organization wants to build an agent that reviews KYC onboarding documents (passports, proof-of-address, corporate registry extracts), extracts and validates the required fields, cross-checks them against sanctions and PEP lists, flags discrepancies, and either auto-clears low-risk cases or escalates ambiguous ones to a human analyst.

### Narrative

In a sentence: an agent that triages KYC documentation for new retail and corporate customers, with autonomy to clear straightforward cases and a hard requirement to escalate anything ambiguous, high-risk, or sanctions-adjacent to a human analyst.

### Taxonomy classification

- *Type* — a document-processing and decisioning agent, not a conversational assistant.

- *Architecture pattern* — single agent with tool access (OCR/extraction tool, sanctions-list lookup, case management system), not a multi-agent system.

- *Autonomy level* — bounded autonomy: the agent can approve low-risk cases outright but cannot reject or escalate-close a case without a human decision, and cannot override a sanctions hit under any circumstance.

- *Tool authority* — read access to document stores and sanctions/PEP databases, write access limited to a case management queue (it can move a case, not close a compliance file).

- *Human-oversight pattern* — human-in-the-loop for all escalations, human-on-the-loop (spot-check sampling) for auto-cleared cases.

- *Data-handling requirements* — processes PII and government ID data, so falls into the taxonomy's higher data-sensitivity band, with corresponding requirements for data minimization and retention limits.

This classification alone already tells you this is not a low-stakes internal tool — it's a customer-onboarding system touching regulated data with a real compliance function, which shapes everything from here on.

### Heuristic assessment

- *Training and grounding data* — the agent isn't fine-tuned on customer data; it's a general-purpose model grounded via retrieval against the FSI organization's KYC policy documents and live sanctions feeds. That narrows one category of risk (training-data leakage) while keeping others open (retrieval-source poisoning, stale sanctions data).

- *Input data* — each query includes an uploaded document plus structured case metadata; both may contain full PII (name, DOB, national ID number, address).

- *Output and exposure risk* — the agent's outputs are structured decisions and extracted fields written into the case management system, not free text shown to the customer.

- *Context and risk tolerance* — this is a client-facing, regulatory-relevant use case with essentially zero tolerance for a false clear on a genuine sanctions match, and low tolerance for inconsistent treatment of similar cases.

### Risk shortlist

Reviewing the risk catalog against that profile, a KYC use case will typically pull in risks across all three of AIGF's categories — operational, security, and regulatory & compliance. Concretely: data quality and drift (extraction accuracy degrading as document formats change), hallucinated or fabricated field values presented with false confidence, sanctions-list staleness or lookup failure, inconsistent decisioning across similar cases (a fairness and audit concern), and prompt injection via a maliciously crafted document. Not every risk in the catalog applies — that's the point of running the assessment rather than applying the whole catalog by default.

### Mitigation mapping

Each shortlisted risk gets matched to catalog mitigations and made concrete for this use case — for example: mandatory human confirmation before any sanctions-adjacent case is cleared (not just flagged); confidence thresholds below which the agent must escalate rather than guess; periodic sampling and drift monitoring on extraction accuracy against a labeled test set; and input sanitization plus a locked-down instruction boundary around anything read from an uploaded document, so text embedded in a fake "certificate" can't act as a prompt.

## 9.3 Turning the Assessment into a Contribution

At this point the FSI organization has a complete internal risk assessment — useful on its own. Codifying it as a contribution to AIGF means expressing it as a structured artifact using the repository's existing template, rather than a one-off internal memo.

The AIGF repository (finos/ai-governance-framework on GitHub) keeps its published content — the risk catalog, the mitigation catalog, and the use case taxonomy — as structured documents under its docs/ folder, with a dedicated templates-for-ri-md folder providing the markdown templates contributors are expected to follow for new entries, plus scripts and scripts_docs that build and validate the published site from those markdown sources. Practically, contributing the KYC use case means:

- Taking the relevant template from templates-for-ri-md and filling it in with the narrative, taxonomy classification, risk shortlist, and mitigation mapping worked out above.

- Following the project's existing conventions for structure and terminology, documented in CONVENTIONS.md, so the entry reads consistently with everything already published.

- Running the project's local build/validation scripts (per DEVELOPMENT.md) before submitting, so the new entry doesn't break the generated site.

## 9.4 Making the Pull Request

The mechanics follow FINOS's standard open-source contribution model:

4.  **Check for or open an issue first.** FINOS's contribution norms across projects favor discussing a proposed addition in an issue before code lands — for a new use case, this is where you'd sanity-check the classification and risk shortlist with the maintainers and the wider community before investing in the full write-up.

5.  **Fork the repository and create a branch** for the new use case entry.

6.  **Add the markdown file** using the appropriate template, following CONVENTIONS.md.

7.  **Sign every commit with a DCO** (Signed-off-by: Name <email>, or git commit -s) — this is a hard requirement across FINOS projects and commits without it get flagged automatically.

8.  **Open the pull request**, referencing the issue from step 1, and let the automated checks (docs build, formatting) run.

9.  **Engage with review.** AIGF is governed as an open working group — becoming a recognized "Participant" is as simple as attending a meeting or contributing to an issue or PR — and substantive changes typically get discussed at the project's bi-weekly meetings alongside the asynchronous GitHub review.

10. **Iterate and merge.** Once the maintainers (drawn from the project's committer team) are satisfied, the entry merges and becomes part of the published framework — visible to every other institution using AIGF, not just the FSI organization that wrote it.

## 9.5 Why This Is Worth the Effort

Two things happen once the KYC use case is merged. Internally, it becomes the literal template the FSI organization's next similar use case — say, ongoing transaction monitoring, or a credit-decisioning assistant — starts from: the taxonomy dimensions are already understood, the risk categories that matter for regulated customer-data use cases are already known, and the mitigation patterns are already proven. Downstream in the pipeline, this artifact is exactly what Chapter 10 needs to select the right reference architecture and translate it into a CALM specification, and what Chapter 11 needs to know which decision points must be pinned down in Fluxnova as deterministic gates rather than left to the model.

Externally, the entry strengthens the shared catalog every other FINOS member institution draws from — which is the entire point of AIGF being open source rather than a proprietary internal framework: the next FSI organization building a KYC agent doesn't start from zero, because this one didn't either.
