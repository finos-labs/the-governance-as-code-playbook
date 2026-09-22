# Chapter 6 — AIGF and AIUC-1: Differences and Complementarity

None of this makes external certification irrelevant — it changes what that certification is built on. It's worth being precise about how AIGF-driven Governance-as-Code relates to AIUC-1, the agent security and reliability standard from the Artificial Intelligence Underwriting Company, because the two operate at different layers and answer different questions, and because confusing them is one of the more common mistakes an FSI organization makes when planning its governance program.

## 6.1 Two Different Questions, Two Different Layers

**AIUC-1 is a point-in-time, audited, insured attestation.** It combines an audit of organizational controls with adversarial testing of the product itself, backed by Lloyd's of London insurance — a structure that gives the certifier real financial exposure if a certified agent fails, refreshed quarterly to keep pace with how fast agents change. It's an external signal: proof to a regulator, a board, or a counterparty that a specific agent has been independently vetted.

**AIGF, running through the Governance-as-Code pipeline, is the continuous, internal engine that produces that proof as a byproduct of how the system was built.** It doesn't issue a certificate. It defines the risks and controls, enforces them automatically through the Controls stage's CI/CD checks and CCC, orchestrates agentic workflows through Fluxnova, and observes the running system in production.

Put simply:

- **AIGF answers "how do we build and run this responsibly, every day, for every agent?"** — it's the pipeline.

- **AIUC-1 answers "can we prove this specific agent is safe to someone outside the institution?"** — it's the credential.

## 6.2 A Closer Look at AIGF

AIGF is not a product an FSI organization buys or a body that issues verdicts — it's a shared, open-source artifact that an FSI organization's own Governance Layer uses to run its own program. Three things define what it actually is:

- **It's a catalog, not a checklist someone hands you.** The risk catalog and use-case taxonomy (Chapters 1 and 9) are structured, versioned content in a public GitHub repository. A FSI organization's Governance Layer reads it, references specific risk IDs in its own CALM controls (Chapter 10), and can propose additions back to it.

- **It's governed by consensus, not by a vendor.** Decisions about what goes into the catalog are made by a FINOS working group — the same FSI organizations and technology providers that use the framework, including Morgan Stanley, Citi, and NatWest among others. There's no company selling AIGF compliance; there's a community maintaining a shared reference.

- **It produces no certificate.** Running a use case through AIGF-driven Governance-as-Code doesn't result in a document an FSI organization can hand a counterparty saying "AIGF-certified." What it produces is the CI/CD history, the CALM specification, the execution traces, and the risk mapping — the raw evidence Chapter 10 and Chapter 11 built out for the KYC use case — which is exactly the evidence an AIUC-1 audit, or an internal audit, would otherwise have to go and collect by hand.

## 6.3 A Closer Look at AIUC-1

AIUC-1 is a specific, named certification standard with its own defined structure — worth understanding on its own terms rather than only in contrast to AIGF:

- **It's organized around six pillars.** Public descriptions of the standard group its requirements under security, safety, reliability, accountability, data and privacy, and societal risk — a broader frame than a typical security-only compliance standard.

- **Certification means passing an audit and adversarial testing, not filling out a questionnaire.** Vendors pursuing AIUC-1 undergo independent, accredited audits combined with adversarial red-teaming aimed at surfacing failure modes — unauthorized tool calls, jailbreaks, and similar attacks — before a certificate is issued.

- **The insurance is the distinguishing feature.** Because AIUC (the company) both certifies and underwrites the risk of certified agents through Lloyd's of London, a failure in a certified agent creates direct financial exposure for the certifier — a structurally different incentive than a standards body that only issues a pass/fail opinion.

- **It refreshes quarterly, not annually.** Given how quickly agent behavior and the surrounding threat landscape shift, a certification that was accurate a year ago says very little about an agent today — so AIUC-1 re-tests on a shorter cycle than most legacy compliance certifications.

## 6.4 Side by Side

| **Aspect**         | **AIGF / Governance-as-Code**                                                                            | **AIUC-1**                                                                         |
|--------------------|----------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| **What it is**     | An open-source risk catalog, use-case taxonomy, and governance methodology, enforced through a pipeline. | An audited, insured certification standard for individual AI agents.               |
| **Governed by**    | A FINOS open working group — FSI and vendor participants, consensus-based.                               | The Artificial Intelligence Underwriting Company (AIUC), a private firm.           |
| **Basis of trust** | Transparency — anyone can read the risk catalog, the taxonomy, and the controls.                         | Independent audit plus adversarial testing, backed by Lloyd's of London insurance. |
| **Cost**           | Free and open source.                                                                                    | A paid certification and audit engagement.                                         |
| **Output**         | Continuous evidence, generated automatically as a byproduct of the pipeline.                             | A point-in-time certificate, refreshed quarterly.                                  |
| **Scope**          | Every AI and agentic use case across the institution.                                                    | Specific agents chosen for certification, one at a time.                           |
| **Applies to**     | Build and buy — any use case, built internally or sourced from a vendor.                                 | Any AI agent, though typically pursued for customer-facing or high-autonomy ones.  |
| **Recognized by**  | Peer financial institutions and regulators familiar with FINOS's mappings.                               | Boards, customers, and counterparties wanting independent, insured proof.          |

## 6.5 Using Them Together

An FSI organization that has already embedded AIGF into its Governance-as-Code pipeline isn't starting from zero when it decides a given agent needs AIUC-1 certification. The reference architecture already maps to known threat models. The CI/CD history already shows policy validation over time. The observability layer already has the telemetry an auditor would otherwise have to request manually. Rather than treating certification as a separate, bolt-on project, it becomes a natural checkpoint layered on top of governance that was already running — which is precisely the relationship the FINOS AI Fund gestures at when it lists certification and market-readiness support as a complement to, not a replacement for, governance-as-code enablement.

## 6.6 Frequently Asked Questions

- **Do we need both AIGF and AIUC-1?** For most FSI organizations, yes, but not for every use case. AIGF-driven Governance-as-Code is the baseline every agentic use case should run through — it's free, and Chapter 7's task lists assume it's already in place. AIUC-1 is a targeted, paid step reserved for specific agents — Chapter 7's Step 9 task list frames this as a deliberate decision, not a default.

- **If we already run AIGF, do we still need AIUC-1 for a given agent?** Depends on who needs convincing. AIGF's artifacts satisfy an internal audit and demonstrate a mature program. But AIGF alone gives no third-party attestation — no independent auditor has verified anything, and no insurer has staked money on the outcome. If a board, a major customer, or a regulator wants proof that doesn't rest on the FSI organization's own word, that's what AIUC-1 is for.

- **Can AIUC-1 replace our internal risk assessment?** No. AIUC-1 certifies a specific agent at a point in time; it doesn't classify use cases, maintain a risk catalog, or tell an engineering team which controls to build in. An FSI organization without an internal program like AIGF's would have nothing to show an AIUC-1 auditor except the agent itself — no risk mapping, no CALM specification, no CI/CD history — which is exactly the gap Chapters 9 and 10 exist to fill before Chapter 11 even starts building.

- **Does AIUC-1 only apply to vendor-bought agents?** No — it applies to any AI agent, whether built in-house or bought from a vendor. A FSI organization's own KYC agent from Chapters 9 through 11 is just as eligible for AIUC-1 certification as a third-party chatbot would be, provided it clears the same audit and testing.

- **Who's actually accountable if something goes wrong — FINOS or AIUC?** Neither takes on the FSI organization's regulatory accountability in either case; an FSI organization remains responsible for its own agents regardless of which of these it uses. The difference is in what each party puts at risk alongside that: FINOS, as an open-source foundation, doesn't issue certificates or take on financial exposure. AIUC does — the insurance backing described in Section 6.3 is AIUC's own money at stake if a certified agent fails, which is not something running AIGF alone gives an FSI organization access to.

- **What happens if we pass AIUC-1 but our AIGF risk catalog is out of date?** The certificate reflects a point in time — Section 6.3's quarterly refresh exists precisely because a stale certificate is a real risk. An out-of-date internal risk catalog is a governance gap regardless of certification status, and it's the kind of gap Chapter 5's continuous-monitoring argument (Section 5.2) is built to catch before a quarterly re-audit would.

- **Is AIUC-1 required by any regulation?** No — it's an industry-developed standard, not a legal requirement. Its value is in being independently verifiable and insured, which can make regulatory conversations easier, but it doesn't substitute for whatever an FSI organization's actual regulatory obligations are under frameworks like the EU AI Act or existing model-risk-management guidance.

- **Does running AIGF give us any external proof at all, without AIUC-1?** Indirectly, yes. Because AIGF's risk catalog is explicitly mapped to recognized frameworks (Chapter 5), an FSI organization can show a regulator that its internal program aligns with those frameworks. What it can't offer is an independent auditor's signature or an insurer's financial backing — that's specifically what Section 6.1 means by AIGF being the pipeline and AIUC-1 being the credential.
