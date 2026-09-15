<!--
SPDX-License-Identifier: CC-BY-4.0
Copyright 2026 Fintech Open Source Foundation
-->

# Chapter 13 — Evals: Measuring What Determinism Doesn't Cover

“Evals” has been sitting in this guide's own pipeline diagram since Chapter 1 — listed alongside OpenTelemetry and dashboards in the Observability & Feedback stage, and referenced again in Chapters 2, 12, and 14 as the thing that judges whether a deployed process is “still behaving as designed.” None of those mentions ever said what an eval actually is, or how to build one. This chapter fixes that.

## 13.1 What Determinism Doesn't Cover

Chapter 3 drew a hard line: Fluxnova makes the process deterministic, even though the LLM inside it isn't. That line is real and it matters, but it answers a narrower question than it sounds like. Chapter 11's agentic ad-hoc subprocess guarantees the extraction tool and the sanctions lookup are the only two things the agent can do — it says nothing about whether the extraction is any good. A well-designed CALM control (Chapter 10) stops the agent from calling a tool it isn't supposed to; it can't tell you whether that tool's output actually got the applicant's date of birth right. Evals are how a team answers that second, harder question — the quality and safety of what happens inside the boundary Fluxnova already drew, not whether the boundary held.

## 13.2 Eval-Driven Development: The Methodology

Eval-driven development (EDD) is a top-down approach: define the standard a good agent output looks like before building toward it, the way test-driven development defines a test before writing the code that passes it. As described by DeepEval, an open-source evaluation framework built around this workflow, EDD is a three-step loop:

- **Curate a small, high-quality dataset** — around 100 “goldens” (input/expected-output pairs), not thousands of auto-generated ones.

- **Define a handful of metrics that actually correlate with performance** — typically 3 to 5, not an exhaustive checklist.

- **Iterate until every metric passes** — treating a failing eval the same way a failing test blocks a merge.

The methodology borrows its shape from test-driven development, but the underlying evaluations behave nothing like a normal unit test, which is exactly why EDD needs a discipline of its own rather than just running more tests. Where a TDD assertion is free, instant, and objectively pass/fail, an eval is often an LLM judging another LLM's output — it costs money to run, takes real time, and produces a subjective, graded score rather than a clean true/false. That's precisely why the dataset stays small and curated rather than exhaustive: a bank running thousands of low-quality, auto-generated test cases through an LLM-as-judge metric is paying real money to learn very little, where a hundred carefully chosen cases, reviewed by someone who understands the use case, actually tell a team something.

## 13.3 What to Evaluate: Security and Functionality

Two categories cover most of what matters, and both map directly onto risks Chapter 9's heuristic assessment already names rather than introducing anything new:

- **Security** — prompt injection, PII leakage, toxicity, jailbreaks. For the KYC extraction tool specifically, this is the empirical test of exactly the risk Chapter 9's shortlist flagged: can a maliciously crafted document manipulate the agent's reasoning, or cause it to leak data it shouldn't.

- **Functionality** — task completion, tool-calling accuracy, and factual correctness. For extraction, this is whether the fields it pulls out of a document are actually right, not merely well-formatted; for the sanctions lookup, whether the agent calls the tool with the correct, unmodified identity details.

Security evals are close to non-negotiable — an agent that leaks PII or can be steered off-task by an injected instruction is a governance failure regardless of how well it performs otherwise. Functionality evals are where a team's actual understanding of what “good” looks like for their specific use case has to show up; nobody outside the team building the KYC extraction tool can hand them the right metric for it.

## 13.4 Unit Evals vs. Regression Evals

This is the same unit-versus-integration distinction Chapter 12 already applies to structural checks, carried over to behavioral ones:

- **Unit evals** score one component in isolation — the extraction tool's output against a document, independent of what happens afterward in the process. This is the direct analogue of validating a single CALM node rather than the whole specification.

- **Regression evals** run end-to-end over the full curated dataset every time the prompt, the model, or the subprocess's configuration changes — the behavioral equivalent of Chapter 12's full DMN test matrix, run on every change rather than once.

Both matter, for the same reason Chapter 12 argues both structural checks matter: a unit eval catches a regression in one tool before it's masked by everything downstream; a regression eval catches an interaction between components that no single unit eval would ever see on its own.

## 13.5 A Worked Example: Evals for the KYC Extraction Tool

A small golden set for the extraction tool from Chapter 11 might look like this — a handful of representative documents, each with a known-correct extraction, deliberately including the edge cases a team already knows are hard:

```
GOLDEN SET — kyc-extraction-tool (excerpt, 3 of 104 goldens)
 
golden_001  input: US passport, standard MRZ format
            expected: { dob: "1985-03-14", name: "J. RIVERA", doc_id: "..." }
 
golden_047  input: UK driving licence, DD/MM/YYYY date format
            expected: { dob: "1990-11-02", name: "A. KHAN", doc_id: "..." }
 
golden_089  input: scanned corporate registry extract, low image quality
            expected: { entity_name: "...", registration_no: "...", jurisdiction: "..." }
```

Three metrics carry most of the signal for this tool: a Task Completion metric (did the extraction produce a structurally valid, complete output), a custom field-accuracy metric scored against the golden's expected values, and a PII-leakage check confirming the agent's reasoning trace never echoes sensitive fields anywhere it shouldn't. Running that suite looks like this:

```
$ deepeval test run test_kyc_extraction.py
 
test_kyc_extraction.py::test_extraction[golden_001] PASSED
  Task Completion:        0.94   (threshold 0.85)   PASS
  Field Accuracy (G-Eval): 0.91   (threshold 0.85)   PASS
  PII Leakage:             0.00   (threshold 0.05)   PASS
 
test_kyc_extraction.py::test_extraction[golden_047] FAILED
  Task Completion:        0.78   (threshold 0.85)   FAIL
  Field Accuracy (G-Eval): 0.69   (threshold 0.85)   FAIL
  PII Leakage:             0.00   (threshold 0.05)   PASS
  Reason: extracted date of birth transposed day/month on a
          non-US date format document
 
======================= 102 passed, 2 failed in 41.3s ========================
BUILD: FAILED — 2 goldens below threshold, merge blocked
```

That failure is a genuinely useful one to catch here rather than in production: it's exactly the kind of narrow, format-specific bug a manual code review would likely miss, and exactly the kind of thing 4,820 real KYC cases a month (Chapter 12's volume) would eventually surface anyway — just later, and after some number of UK-format documents had already been misread.

## 13.6 Evals as a CI/CD Gate

This slots into Chapter 12's build gate as a third check, alongside CALM structural validation and the DMN test matrix — not a separate pipeline, the same one:

```
$ calm validate kyc-agentic-subprocess.calm.json
✓ All nodes declared, all relationships reference declared nodes
 
$ fluxnova dmn-test kyc-risk-confidence.dmn --cases dmn-test-cases.json
✓ 5/5 test cases passed
 
$ deepeval test run test_kyc_extraction.py
✗ 102/104 goldens passed — 2 below threshold
 
BUILD: FAILED — fix failing evals or update the golden set before merging
```

One thing worth being precise about: this isn't a native Fluxnova feature, and this guide isn't claiming FINOS and DeepEval have an official integration. DeepEval instruments at the LLM call itself — wrapping the Anthropic or OpenAI client the agentic ad-hoc subprocess calls, or the surrounding function, with a lightweight decorator — which makes it independent of whatever orchestrates the call around it. That's precisely why it fits here without requiring one: Fluxnova bounds where the LLM can act (Chapter 11), and DeepEval evaluates what it does once it acts, and the two never need to know about each other to both be true at once. Ownership follows the same split Chapter 7.1 already established for other CI/CD checks — Hub MLOps/DevSecOps runs the pipeline mechanics, while the Business Spoke's AI engineers own the goldens and the metrics that matter for their specific use case, per Section 13.3's point that nobody outside the team can hand them that list.

## 13.7 From One-Time Gate to Continuous Signal

Chapter 14's observability layer already tags every production trace and mentions evals as part of what closes the loop; this is what actually fills that in. The same regression suite that blocks a merge in Section 13.6 also runs on a schedule against a sample of real production traces, not just the curated golden set — catching the drift Chapter 14.6 describes (an escalation rate climbing, or in this case, an extraction accuracy quietly declining) before it shows up as a compliance incident rather than after. A finding here feeds back exactly where Chapter 7's Step 8 already says it should: a metric trending down triggers the same feedback-loop investigation as a drifting escalation rate, because both are the same kind of signal — evidence that something approved a while ago needs a second look now.

This is also, finally, what closes the loop Chapter 1 opened on page one. The Observability & Feedback stage was always going to include evals — this chapter is what makes that entry in the diagram mean something concrete rather than a term left for later.
