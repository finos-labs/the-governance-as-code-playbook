# Introduction

A note on terms before we start: this guide uses “FSI” and “FSI organization” to mean any financial services institution — a bank, but equally an insurer, an asset manager, a payments provider, or another regulated financial firm. The pipeline and every example in this guide were built around a banking use case, because that's where AIGF and Fluxnova have the deepest early adoption, but nothing about the argument is bank-specific. Wherever this guide says “an FSI organization,” read it as applying to whichever kind of regulated financial institution you actually work for.

Ask an FSI organization's compliance team how they govern a new AI system today, and you'll usually hear some version of the same story: a policy document, a risk assessment spreadsheet, a review meeting, a sign-off. Ask the engineering team building that system, and you'll hear the mirror image: governance shows up late, as a gate at the end of the pipeline, disconnected from the code and largely manual.

That gap — governance as paperwork versus engineering as pipeline — is exactly what FINOS's Governance-as-Code initiative, backed by the new FINOS AI Fund, is built to close. And the FINOS AI Governance Framework (AIGF) isn't a bystander to that effort. It's the foundation the whole pipeline is built on.

## The Usual Pitfalls

Before getting into how the pipeline works, it's worth naming what tends to go wrong when FSI organizations build agentic AI without something like it in place. None of these are hypothetical — they're the recurring patterns behind delayed launches, failed audits, and agents quietly pulled from production:

- **Governance bolted on at the end.** A team builds an agent, gets it working, and only then brings it to risk and compliance for review — by which point the architecture is set, the autonomy boundaries are implicit in the code rather than designed in, and any serious finding means a costly redesign rather than a small adjustment.

<!-- -->

- **Every team reinvents its own risk assessment.** Without a shared taxonomy, one team's "high risk" is another team's "minor internal tool," and there is no consistent basis for the board or a regulator to compare use cases across the institution — or even to trust that every use case was assessed with the same rigor.

- **Shadow AI and ungoverned proliferation.** Business units and individual teams adopt agentic tools faster than central governance can track them, because the sanctioned path is slow and manual — leaving the institution with agents in production that nobody centrally assessed.

- **Non-determinism quietly accepted, then discovered the hard way.** An agent behaves acceptably in a proof of concept, where a wrong answer costs nothing, and the same non-deterministic behavior ships into a regulated workflow where a skipped control point becomes a reportable incident — because nobody drew a hard line between what the model can decide freely and what must be fixed and enforced.

- **No reconstructable audit trail.** When a regulator or an internal auditor asks how a specific automated decision was reached, the honest answer is often "the model decided," which satisfies nobody — the reasoning path wasn't fixed, so the evidence trail wasn't fixed either, and reconstructing it after the fact is expensive or impossible.

- **Compliance treated as a one-time gate, not a continuous state.** A system passes its launch review and is then left unmonitored for drift — the model, the data, or the threat landscape moves on, and nobody notices until something goes wrong, because the governance process had no mechanism for continuous feedback.

- **Duplicated effort across the industry.** Every FSI organization building, say, a KYC or AML agent independently re-derives the same risk categories and mitigations that dozens of peer institutions have already worked out — burning months of legal, risk, and engineering time on a problem that has effectively already been solved elsewhere.

- **Poorly defined escalation and human oversight.** "Human in the loop" gets asserted in a policy document without being enforced anywhere in the system, so in practice the agent's autonomy in production is broader than anyone signed off on.

## Open Source Versus Proprietary: The Path This Guide Takes

There are two broad ways an FSI organization can approach governance for agentic AI, and it's worth being explicit about which one this guide follows.

The first is to buy a proprietary governance platform from a large vendor. This can get a program running quickly, but it comes with real trade-offs: the risk logic and control mappings typically live inside a closed, licensed product that the FSI organization cannot fully inspect, audit, or adapt to its own specific regulatory obligations; the FSI organization's governance program becomes dependent on that vendor's roadmap and pricing; and the investment the FSI organization makes in configuring the platform for its use cases doesn't transfer if the relationship ends, and doesn't benefit any other institution facing the same problem.

The second path — the one this guide is built around — is the open-source route: FINOS's AI Governance Framework and the surrounding Governance-as-Code pipeline (CALM, Common Cloud Controls, Fluxnova, and the observability layer), developed collaboratively by the financial institutions and technology providers that actually have to answer to regulators. This isn't a philosophical preference. It carries concrete, practical advantages for an FSI organization building its own agentic AI:

- **Transparency.** The risk catalog, the mitigations, and the taxonomy are all open text a regulator, an auditor, or an internal risk committee can read directly — nothing is a black box the FSI organization has to take on faith from a vendor.

- **No lock-in.** Because the framework is open source and vendor-agnostic, the FSI organization's governance program isn't hostage to one company's licensing terms, roadmap, or continued existence.

- **Shared cost, compounding benefit.** Every risk category, mitigation, and reference architecture that AIGF already covers is work the FSI organization does not have to redo — and, as Chapter 9 shows in detail, work the FSI organization contributes back (like a KYC use case) becomes reusable infrastructure for every other institution using the framework, the same way the FSI organization benefits from what Morgan Stanley, Citi, NatWest, and others have already contributed.

- **Control stays with the institution.** The FSI organization can extend, fork, and adapt the framework to its own regulatory footprint, rather than waiting on a vendor to prioritize a feature request.

## Why This Gets an FSI Organization to ROI Faster

The pitfalls above aren't just governance problems — they're expensive ones, in time and in money. Building on AIGF's Governance-as-Code pipeline instead of starting from a blank page, or from a proprietary black box, shortens the path to a return on investment in several concrete ways:

- **Less rework, because governance is designed in rather than bolted on.** Catching a risk during architecture selection (Chapter 2) costs a design decision; catching the same risk after launch costs a rebuild. Fewer late-stage redesigns means agents reach production faster.

- **No proprietary licensing overhead.** Building on an open-source framework avoids the recurring per-seat or per-agent costs of a closed governance platform, and avoids the switching costs that come with vendor lock-in.

- **Audit and certification evidence is a byproduct, not a project.** Because the pipeline generates execution traces, CI/CD validation history, and risk mappings automatically as agents are built and run, both internal audits and external certification (Chapter 6) start from existing evidence rather than a costly, from-scratch evidence-gathering exercise.

- **Reuse compounds across the agent portfolio.** The first use case an FSI organization runs through this pipeline is the slow one — Chapter 9 shows what that first pass looks like in full. The second, and the fiftieth, move faster, because the taxonomy, the risk catalog, and the reference architectures are already in place and already proven.

- **Faster regulatory engagement.** Because AIGF's risk catalog is already mapped to frameworks regulators recognize — the EU AI Act, FCA Consumer Duty, PRA operational resilience — conversations with supervisors start from shared vocabulary rather than a bespoke internal framework nobody outside the FSI organization has seen before.

The chapters that follow walk through exactly how this works in practice — starting with what the pipeline is, then how each stage fits together, then a full worked example that turns a single use case into a governed, running, and auditable agent.
