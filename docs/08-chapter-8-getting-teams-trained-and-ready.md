# Chapter 8 — Getting Teams Trained and Ready

Chapter 7 described who does what once a pipeline is running and how to sequence the work. This chapter addresses the question that comes before that: how does a Chief AI Officer get an organization that doesn't yet think this way to the point where Chapter 7 is executable at all. Training and rollout is a different problem from process design, and treating them as the same problem is itself one of the pitfalls from the Introduction — a Spoke “moving fast” in an ungoverned way usually just means nobody trained it on the taxonomy yet.

## 8.1 Training Is Role-Specific, Not a Single Curriculum

The six roles from Section 7.1 don't need the same thing from a training program, and treating them as if they do wastes effort on the roles that need it least while underserving the ones that need it most.

- **Governance Layer (MRM and Compliance)** needs the deepest investment, and it's the one group where structured, scheduled sessions are worth running: working through the risk catalog and taxonomy repeatedly until classifying a new use case takes an afternoon, not a workshop. This group's fluency is what determines whether Steps 1 and 2 are fast or slow for every use case that follows it, which makes it the highest-leverage place to invest first.

- **Business Spoke AI engineers** learn CALM and Fluxnova by writing them under review, not by attending a course. The most effective “training” here is the first pilot use case itself, done deliberately slowly with an experienced reviewer pairing on every pull request.

- **Hub Architecture and Hub MLOps** need the least ramp-up if they're already doing platform engineering work — the shift for them is conceptual more than technical: governance now lives in a CALM file and a CI/CD check, not in a wiki page nobody reads.

- **Business Spoke product managers and domain experts** need the lightest touch: enough literacy to write a use case narrative and understand why classification happens before any building starts, so Step 1 reads as useful rather than as bureaucratic friction.

## 8.2 Formal Training: Linux Foundation Education and Service Providers

Section 8.1 assumed an FSI organization builds its entire training path from scratch. It doesn't have to. Linux Foundation Education — the Linux Foundation's training and certification arm, which already runs FINOS's existing certification programs — offers formal courses and certifications covering FINOS projects, with coverage of AIGF, CALM, and Fluxnova alongside them as those projects mature. Beyond the self-paced catalog, instructor-led training is also available through Linux Foundation training partners and FINOS member service providers, and FINOS itself has begun running hands-on leader training aimed specifically at risk, compliance, legal, model governance, and operations leaders operationalizing this pipeline. For a CAIO standing up a program from nothing, this is worth treating as a foundational layer underneath Section 8.1's role-specific approach, not a substitute for it:

- **Formal courses build shared vocabulary fast.** A Governance Layer analyst who has already worked through a structured course arrives at the first taxonomy classification workshop fluent in the categories, rather than learning the taxonomy's shape for the first time under deadline pressure.

- **They fit naturally with the roles Section 8.1 flagged as needing the lightest touch.** Business Spoke product managers and domain experts, who only need enough literacy to write a use case narrative and understand why classification matters, are well served by a short formal course rather than a bespoke internal session the Governance Layer has to build and maintain itself.

- **Service providers fill the gap a self-paced course can't.** Hands-on, instructor-led sessions tailored to an FSI organization's own environment are useful when a Hub team is standing up CALM and Fluxnova tooling for the first time and wants an expert in the room rather than documentation alone — and FINOS's own leader training exists precisely because Governance Layer roles benefit from guided, cohort-based sessions more than a self-paced course.

- **None of this replaces Section 8.3's argument.** A completed course demonstrates familiarity with the concepts; writing a CALM specification that clears review demonstrates the capability. Formal training gets a squad to its first pilot faster and with fewer false starts — it is not, on its own, a finish line.

## 8.3 The First Use Case Is the Training Program

The natural instinct is to train everyone first, then start a pilot. It's worth inverting that. Pick one real, modest use case, assemble the standing cross-functional squad described in Section 7.3, and let that squad's first pass through Steps 1 through 6 be the training — documented deliberately as it happens, specifically so it becomes the FSI organization's own internal playbook layered on top of AIGF's generic guidance. This is Chapter 9's argument about the first use case becoming a template, applied to people instead of artifacts: the KYC use case in Chapters 9 through 11 is exactly the kind of pilot this section has in mind, and an FSI organization's own first pass through it produces the institution-specific version of that template that every subsequent Spoke actually learns from.

This also sets a realistic maturity progression rather than a single rollout event: one pilot squad completes a use case and writes down what it learned; that documentation, plus the reusable taxonomy and architecture artifacts, lets a second Spoke run its own use case with lighter support; by the third or fourth use case, the pattern is established enough that a new Spoke can largely self-serve from what previous ones produced, with the Governance Layer reviewing rather than teaching from scratch each time.

## 8.4 Get a Seat in the Room Early

AIGF is a living, community-governed project, not a specification that gets downloaded once and left alone — it has already gone through a major version change that added agentic-specific risk coverage. A CAIO who sends someone to FINOS's regular working group meetings (Chapter 9 mentions these as part of the contribution process) gets two things at once: the FSI organization's internal understanding stays current as the framework evolves, and the FSI organization gets a voice in what the catalog covers next, rather than finding out about a change after the fact. This is a natural complement to Section 8.2's formal training paths — a course teaches the framework as it stood when the course was recorded; a seat in the working group is how the FSI organization's understanding keeps pace with a framework that keeps moving. Treating AIGF adoption as a one-time download, formal course included, is a slower-motion version of the staleness problem Chapter 6's FAQ raises about certifications going stale between audits — the fix is the same in both cases: stay continuously engaged rather than checking in periodically.

## 8.5 The Failure Mode Specific to Training: Skew

Beyond the general pitfalls in the Introduction, rollout has one failure mode worth naming on its own: investing heavily in engineering enablement — because it's tangible, has a curriculum, and feels like real training — while leaving the Governance Layer and Business Spokes undertrained. This doesn't remove the bottleneck an FSI organization is trying to fix; it just moves it. An engineering team that can write a CALM specification quickly gains nothing if the Governance Layer still needs three weeks to classify the use case that CALM file depends on. A training investment should be sized to whichever role is currently the slowest step in Chapter 7's timeline, not to whichever role is easiest to run a workshop for — and the same imbalance can now happen inside Section 8.2's formal-training budget alone, if every seat goes to engineering courses and none to the Governance Layer sessions FINOS runs specifically for that audience.

A related version of the same mistake is training once and considering the job done. Because AIGF itself changes (Section 8.4) and because an FSI organization's own playbook keeps accumulating lessons from each new use case (Section 8.3), training is closer to an ongoing rhythm than a single onboarding event — the same continuous-engagement principle Chapter 5 argues for GRC's involvement across a use case's lifecycle applies equally to how an organization stays current on the framework itself.
