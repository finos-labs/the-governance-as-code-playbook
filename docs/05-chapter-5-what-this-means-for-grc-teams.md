<!--
SPDX-License-Identifier: CC-BY-4.0
Copyright 2026 Fintech Open Source Foundation
-->

# Chapter 5 — What This Means for GRC Teams

For risk, compliance, and model governance functions, the shift is just as significant, though it looks different from their side of the table.

## 5.1 What Changes Day to Day for GRC

- **Consistency at scale.** The Use Cases Taxonomy means every AI system in the institution gets classified and governed the same way, regardless of which team built it.

- **Evidence, not attestations.** Because controls run automatically in the pipeline and observability data is captured continuously, GRC teams get generated evidence of compliance rather than relying on engineers to self-report that they followed the process.

- **Faster, better-informed reviews.** When a system reaches a formal risk review, the reference architecture, the AIGF risk mapping, and the CI/CD validation history already exist.

- **Direct line to regulatory frameworks.** Because AIGF's catalog is explicitly mapped to regulations like the EU AI Act, GRC teams aren't translating internal controls into regulatory language after the fact.

- **A seat at the table industry-wide.** AIGF is being shaped by the same institutions that have to answer to the same regulators — Morgan Stanley, NatWest, DTCC, RBC, and others are founding backers of the FINOS AI Fund driving this work.

## 5.2 From Estimation to Production: GRC at Every Phase

The pitfalls in the Introduction included governance bolted on at the end and compliance treated as a one-time gate. Both come from the same root cause: in a traditional model, GRC's involvement is concentrated into a single late-stage review, because that's the only point where there's something concrete enough to review. Governance-as-code spreads that involvement across the entire lifecycle instead, in a form appropriate to each phase — which changes not just when GRC shows up, but how much effort each appearance takes. Walking the same lifecycle a KYC-style use case actually moves through:

- **Estimation and scoping.** Traditionally, compliance review time is a guess — a project is sized without really knowing how much scrutiny it will need, because that depends on details nobody has worked out yet. With the taxonomy in place, classification (Step 1) can happen the moment a use case is proposed, before a line of code is written. A use case that classifies as high-autonomy, high-data-sensitivity gets flagged for a heavier review budget at the estimation stage itself; a low-autonomy internal tool gets sized accordingly. GRC's role here is defining and maintaining the taxonomy's categories, not reviewing individual projects one at a time.

- **Design.** This is where the risk shortlist and mitigation mapping (Step 2) and the reference architecture selection (Step 3) happen. GRC's involvement is direct but bounded: reviewing a specific, structured artifact — the kind produced in Chapter 9 — rather than an open-ended conversation about a system that doesn't exist yet. Because the taxonomy and risk catalog already exist, this review is comparing a proposal against a known list, not inventing the list from scratch for this project.

- **Development.** Once CALM specifications and Fluxnova process definitions are being written (Steps 4 and 5), GRC's role shifts from reviewing artifacts by hand to defining the automated checks that will review every subsequent change — the CI/CD policy checks from Section 4.1 and Chapter 2. GRC does not read every pull request; GRC ensures the control requirements those pull requests get checked against are correct and current.

- **Testing and pre-production.** With the process modeled in Fluxnova (Chapter 11), the DMN decision tables can be unit-tested directly against the outcomes compliance actually signed off on — exactly as Section 11.5 describes. This is also the point at which a decision on AIUC-1 certification (Step 9) typically gets made for higher-risk use cases, since the artifacts an external audit would need are now largely in place.

- **Deployment.** CI/CD policy checks passing becomes a release gate (Step 6) rather than a manual sign-off email. A system cannot reach production with a failing control check any more than it could ship with a failing test suite — which means the deployment-time GRC conversation is about exceptions, not about running the checklist from the top for every release.

- **Production and monitoring.** This is the biggest structural change from the traditional model. Instead of a periodic audit reconstructing what happened from logs after the fact, GRC has a live view through the observability layer (Step 7) — dashboards showing case volumes by outcome, escalation rates, drift signals from evals. A compliance question about the KYC agent's behavior last quarter is answered by querying existing data, not by requesting a special audit.

- **Continuous improvement.** When production data surfaces something the original risk assessment didn't anticipate — an unexpected escalation pattern, a drift in extraction confidence — that finding feeds back into the risk catalog (Step 8), the same feedback loop shown in Chapter 1's diagram. GRC's role here is deciding whether the finding changes the mitigation for this use case, or whether it's significant enough to propose back into AIGF itself, extending the benefit to every other institution using the framework, exactly as Chapter 9 describes for the original contribution.

The throughline is the same one from the Introduction's ROI argument: GRC's total effort across a use case's life doesn't disappear, but its shape changes from one expensive, high-stakes review concentrated at the end to a series of smaller, well-defined touchpoints spread across a process that was designed, from the estimation stage onward, to produce exactly the artifacts each touchpoint needs.
